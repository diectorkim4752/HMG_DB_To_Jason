# -*- coding: utf-8 -*-
"""
DB 클라이언트 모듈
ArtistSul CMS API와의 통신을 담당
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import logging

from config import (
    BASE_URL, JWT_TOKEN, API_ENDPOINTS, DEFAULT_HEADERS,
    MAX_RETRIES, RETRY_DELAY, FETCH_LIMIT
)

logger = logging.getLogger(__name__)

class DBClient:
    """ArtistSul CMS API 클라이언트"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.jwt_token = JWT_TOKEN
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """API 요청을 보내고 응답을 처리"""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"🔄 API 요청 시도 {attempt + 1}/{MAX_RETRIES}: {method} {url}")

                # JWT 토큰이 있으면 헤더에 추가 (CMS 개발자 제공 형식)
                if self.jwt_token and self.jwt_token not in ["your_jwt_token_here", "your_actual_jwt_token_here", "REQUIRED"]:
                    self.session.headers["Authorization"] = f"Bearer {self.jwt_token}"
                    logger.info(f"🔐 JWT 토큰 사용: {self.jwt_token[:20]}...")
                else:
                    logger.info("🔓 개발 모드: JWT 토큰 없이 API 접근 (보안상 주의 필요)")
                
                response = self.session.request(method, url, timeout=30, **kwargs)
                
                # 응답 내용 로깅
                logger.info(f"📡 응답 상태: {response.status_code}")
                logger.info(f"📡 응답 헤더: {dict(response.headers)}")
                logger.info(f"📡 응답 내용 (처음 200자): {response.text[:200]}")
                
                # 응답 상태 코드 확인
                if response.status_code == 200:
                    try:
                        # JSON 파싱 시도
                        json_data = response.json()
                        logger.info(f"✅ API 요청 성공: {response.status_code}")
                        return json_data
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ JSON 파싱 오류: {e}")
                        logger.error(f"❌ 응답 내용: {response.text}")
                        return None
                elif response.status_code == 401:
                    logger.warning(f"⚠️ 인증 실패 (401): JWT 토큰 확인 필요")
                    logger.warning(f"⚠️ 응답 내용: {response.text}")
                    return None
                elif response.status_code == 419:
                    logger.warning(f"⚠️ 인증 만료 (419): 새 로그인 필요")
                    logger.warning(f"⚠️ 응답 내용: {response.text}")
                    return None
                elif response.status_code == 500:
                    logger.error(f"❌ 서버 오류 (500): {response.text}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (2 ** attempt))  # 지수적 백오프
                        continue
                else:
                    logger.error(f"❌ API 오류 ({response.status_code}): {response.text}")
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"❌ 연결 오류: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                    continue
            except requests.exceptions.Timeout as e:
                logger.error(f"❌ 타임아웃 오류: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                    continue
            except Exception as e:
                logger.error(f"❌ 예상치 못한 오류: {e}")
                return None
        
        logger.error(f"❌ 최대 재시도 횟수 초과: {MAX_RETRIES}")
        return None
    
    def get_messages(self, start_date: str = None, end_date: str = None, 
                    page: int = 1, page_size: int = None) -> Optional[Dict]:
        """메시지 데이터 조회 (CMS 개발자 제공 API 스펙 기반)"""
        if page_size is None:
            page_size = min(FETCH_LIMIT, 100)  # API 최대 제한 100
        
        # 날짜 설정 (필수 파라미터)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # CMS 개발자 제공 파라미터 형식
        params = {
            "start": start_date,      # 필수: 시작날짜 (YYYY-MM-DD)
            "end": end_date,          # 필수: 종료날짜 (YYYY-MM-DD)
            "page": page,             # 기본값: 1
            "pageSize": page_size     # 기본값: 100, 최대: 100
        }
        
        logger.info(f"📅 메시지 조회: {start_date} ~ {end_date}, 페이지: {page}, 크기: {page_size}")
        
        # CMS 개발자 제공 API 엔드포인트 사용
        response = self._make_request("GET", API_ENDPOINTS["messages"], params=params)
        
        if response and response.get("ok"):
            data = response.get("data", {})
            items = data.get("items", [])
            total_pages = data.get("totalPages", 1)
            
            logger.info(f"✅ API 성공: {len(items)}개 (총 {total_pages}페이지)")
            return response
        else:
            logger.error(f"❌ API 실패: {response}")
            return None
    
    def get_recent_messages(self, limit: int = None) -> Optional[List[Dict]]:
        """최신 N개 메시지 조회 (등록시간 기준 정렬)"""
        if limit is None:
            limit = FETCH_LIMIT
        
        # 넓은 날짜 범위로 설정하여 최신 데이터 확보
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")  # 1년 범위
        
        logger.info(f"📅 최신 메시지 조회: {limit}개 (날짜 범위: {start_date} ~ {end_date})")
        
        response = self.get_messages(start_date, end_date, page_size=limit)
        
        if response and response.get("ok"):
            messages = response.get("data", {}).get("items", [])
            
            # 등록시간 기준으로 정렬 (최신순)
            if messages:
                try:
                    # createdAt 기준으로 정렬 (최신순)
                    messages.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
                    logger.info(f"✅ 최신순 정렬 완료: {len(messages)}개 메시지")
                except Exception as e:
                    logger.warning(f"⚠️ 정렬 실패, 원본 순서 유지: {e}")
            
            return messages
        return None
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        logger.info("🔍 API 연결 테스트 중...")
        
        try:
            # 1. 기본 URL 연결 테스트
            test_url = f"{self.base_url}/"
            logger.info(f"🔍 기본 URL 테스트: {test_url}")
            
            response = self.session.get(test_url, timeout=10)
            logger.info(f"📡 기본 URL 응답: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ 기본 URL 연결 성공!")
                
                # 2. 워커페이지 API 엔드포인트들 테스트
                endpoints_to_test = [
                    # 워커페이지 가능한 경로들
                    "/worker/messages",
                    "/worker/api/messages", 
                    "/functions/messages",
                    "/pages/api/messages",
                    
                    # 기존 API 경로들
                    "/api/messages",
                    "/api/admin/login",
                    "/api/v1/messages",
                    "/admin/api/messages",
                    
                    # 테스트 경로들
                    "/api/health",
                    "/api/test"
                ]
                
                for endpoint in endpoints_to_test:
                    test_result = self._test_endpoint(endpoint)
                    if test_result:
                        logger.info(f"✅ {endpoint} 엔드포인트 사용 가능!")
                        return True
                
                logger.warning("⚠️ 모든 API 엔드포인트 테스트 실패")
                return False
            else:
                logger.error(f"❌ 기본 URL 연결 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 연결 테스트 오류: {e}")
            return False
    
    def _test_endpoint(self, endpoint: str) -> bool:
        """개별 엔드포인트 테스트"""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"🔍 엔드포인트 테스트: {url}")
            
            response = self.session.get(url, timeout=10)
            logger.info(f"📡 {endpoint} 응답: {response.status_code}")
            
            # JSON 응답인지 확인
            try:
                json_data = response.json()
                logger.info(f"✅ {endpoint} JSON 응답 성공")
                return True
            except json.JSONDecodeError:
                logger.warning(f"⚠️ {endpoint} JSON 응답 아님 (HTML 또는 다른 형식)")
                return False
                
        except Exception as e:
            logger.error(f"❌ {endpoint} 테스트 오류: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """관리자 로그인 (JWT 토큰 갱신) - CMS 개발자 제공 API"""
        logger.info(f"🔐 관리자 로그인 시도: {username}")
        
        # CMS 개발자 제공 로그인 형식
        login_data = {
            "username": username,
            "password": password
        }
        
        # 로그인 시에는 JWT 토큰 없이 요청
        original_token = self.jwt_token
        self.jwt_token = None
        
        try:
            response = self._make_request("POST", API_ENDPOINTS["login"], json=login_data)
            
            if response and response.get("ok"):
                # CMS 개발자 제공 응답 형식
                data = response.get("data", {})
                token = data.get("token")
                expires_in = data.get("expiresIn", 3600)
                
                if token:
                    self.jwt_token = token
                    logger.info(f"✅ 로그인 성공! JWT 토큰 갱신됨 (만료: {expires_in}초)")
                    return True
            
            logger.error("❌ 로그인 실패!")
            return False
            
        finally:
            # 원래 토큰 복원 (로그인 실패 시)
            if not self.jwt_token:
                self.jwt_token = original_token

