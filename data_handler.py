# -*- coding: utf-8 -*-
"""
데이터 처리 모듈
JSON 저장 및 데이터 변환을 담당
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

from config import OUTPUT_DIR, JSON_FILENAME_PREFIX, JSON_FILENAME, USE_FIXED_FILENAME

logger = logging.getLogger(__name__)

class DataHandler:
    """데이터 처리 및 JSON 저장 클래스"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.filename_prefix = JSON_FILENAME_PREFIX
        self.fixed_filename = JSON_FILENAME
        self.use_fixed_filename = USE_FIXED_FILENAME
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """출력 디렉토리 생성"""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                logger.info(f"📁 출력 디렉토리 생성: {self.output_dir}")
        except Exception as e:
            logger.error(f"❌ 출력 디렉토리 생성 실패: {e}")
    
    def _generate_filename(self) -> str:
        """JSON 파일명 생성 (고정 파일명 또는 타임스탬프 포함)"""
        if self.use_fixed_filename:
            return self.fixed_filename
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            return f"{self.filename_prefix}_{timestamp}.json"
    
    def _format_message_data(self, messages: List[Dict]) -> List[Dict]:
        """메시지 데이터 포맷팅"""
        formatted_messages = []
        
        for msg in messages:
            formatted_msg = {
                "id": msg.get("id"),
                "fileNumber": msg.get("fileNumber"),
                "createdAt": msg.get("createdAt"),
                "senderType": msg.get("senderType"),
                "target": msg.get("target"),
                "message": msg.get("message"),
                "hidden": msg.get("hidden", False)
            }
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
    
    def save_messages_to_json(self, messages: List[Dict], 
                            metadata: Optional[Dict] = None) -> Optional[str]:
        """메시지 데이터를 JSON 파일로 저장"""
        try:
            # 메시지가 없어도 빈 데이터로 저장
            if not messages:
                logger.info("📝 데이터가 없습니다. 빈 데이터로 JSON 파일을 갱신합니다")
                messages = []  # 빈 리스트로 설정
            
            # 파일명 생성
            filename = self._generate_filename()
            filepath = os.path.join(self.output_dir, filename)
            
            # 메타데이터 준비
            if metadata is None:
                metadata = {}
            
            # 저장할 데이터 구조
            save_data = {
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "totalCount": len(messages),
                    "source": "ArtistSul CMS",
                    "version": "1.0",
                    **metadata
                },
                "messages": self._format_message_data(messages)
            }
            
            # JSON 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            if self.use_fixed_filename:
                logger.info(f"💾 JSON 갱신 완료: {filename} ({len(messages)}개 메시지)")
            else:
                logger.info(f"💾 JSON 저장 완료: {filename} ({len(messages)}개 메시지)")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ JSON 저장 실패: {e}")
            return None
    
    def save_messages_with_api_response(self, api_response: Dict) -> Optional[str]:
        """API 응답을 그대로 JSON으로 저장"""
        try:
            if not api_response or not api_response.get("ok"):
                logger.error("❌ 유효하지 않은 API 응답")
                return None
            
            data = api_response.get("data", {})
            messages = data.get("items", [])
            
            # 메시지가 없어도 빈 데이터로 저장
            if not messages:
                logger.info("📝 API에서 데이터가 없습니다. 빈 데이터로 JSON 파일을 갱신합니다")
                messages = []  # 빈 리스트로 설정
            
            # 파일명 생성
            filename = self._generate_filename()
            filepath = os.path.join(self.output_dir, filename)
            
            # API 응답에 메타데이터 추가
            enhanced_response = {
                "exportedAt": datetime.now().isoformat(),
                "source": "ArtistSul CMS API",
                "version": "1.0",
                **api_response
            }
            
            # JSON 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(enhanced_response, f, ensure_ascii=False, indent=2)
            
            if self.use_fixed_filename:
                logger.info(f"💾 API 응답 JSON 갱신 완료: {filename} ({len(messages)}개 메시지)")
            else:
                logger.info(f"💾 API 응답 JSON 저장 완료: {filename} ({len(messages)}개 메시지)")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ API 응답 JSON 저장 실패: {e}")
            return None
    
    def get_saved_files(self) -> List[str]:
        """저장된 JSON 파일 목록 조회"""
        try:
            if not os.path.exists(self.output_dir):
                return []
            
            files = []
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.json') and filename.startswith(self.filename_prefix):
                    files.append(filename)
            
            # 파일명으로 정렬 (최신순)
            files.sort(reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"❌ 저장된 파일 목록 조회 실패: {e}")
            return []
    
    def get_latest_file(self) -> Optional[str]:
        """가장 최근 저장된 파일 경로 반환"""
        files = self.get_saved_files()
        if files:
            return os.path.join(self.output_dir, files[0])
        return None
    
    def cleanup_old_files(self, keep_days: int = 7) -> int:
        """오래된 파일 정리 (기본 7일 이상 된 파일 삭제)"""
        try:
            files = self.get_saved_files()
            deleted_count = 0
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            
            for filename in files:
                filepath = os.path.join(self.output_dir, filename)
                file_time = os.path.getmtime(filepath)
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"🗑️ 오래된 파일 삭제: {filename}")
            
            if deleted_count > 0:
                logger.info(f"🧹 파일 정리 완료: {deleted_count}개 파일 삭제")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 파일 정리 실패: {e}")
            return 0

