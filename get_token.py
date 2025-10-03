#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT 토큰 획득 스크립트
Cloudflare Workers API를 통해 JWT 토큰을 가져옵니다.
"""

import requests
import json
import os

# config.py에서 BASE_URL 가져오기
try:
    from config import BASE_URL
except ImportError:
    BASE_URL = "https://artistsul-cms-worker.directorkim.workers.dev"  # 기본값

def get_jwt_token(username, password):
    """JWT 토큰 획득"""
    url = f"{BASE_URL}/api/admin/login"
    data = {
        "username": username,
        "password": password
    }
    
    print(f"🔐 로그인 시도 중: {url}")
    print(f"📝 사용자명: {username}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        result = response.json()
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📡 응답 내용: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('ok'):
            token = result['data']['token']
            expires_in = result['data'].get('expiresIn', 3600)
            print(f"✅ 로그인 성공! JWT 토큰 획득: {token[:50]}... (만료: {expires_in}초)")
            return token
        else:
            error_msg = result.get('error', '알 수 없는 오류')
            raise Exception(f"로그인 실패: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 오류: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   응답 상태: {e.response.status_code}")
            print(f"   응답 내용: {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ 토큰 획득 중 오류 발생: {e}")
        raise

def save_token_to_config(token):
    """획득한 토큰을 config.py에 저장"""
    config_path = "config.py"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip().startswith("JWT_TOKEN ="):
                    f.write(f'JWT_TOKEN = "{token}"  # 실제 JWT 토큰으로 교체하세요\n')
                else:
                    f.write(line)
        
        print(f"✅ JWT 토큰이 {config_path}에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ config.py 저장 실패: {e}")

def test_api_connection():
    """API 연결 테스트"""
    print(f"🧪 API 연결 테스트: {BASE_URL}")
    
    # 여러 가능한 엔드포인트 테스트
    test_endpoints = [
        "/api/health",
        "/api/test", 
        "/api/messages",
        "/api/admin/login",
        "/",
        "/health",
        "/test"
    ]
    
    for endpoint in test_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            print(f"🔍 테스트 중: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"📡 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ API 연결 성공! 엔드포인트: {endpoint}")
                return True
            elif response.status_code == 404:
                print(f"❌ 404 오류: {endpoint}")
            else:
                print(f"⚠️ 응답: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ 연결 실패: {endpoint} - {e}")
    
    print("❌ 모든 API 엔드포인트 테스트 실패")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Cloudflare Workers JWT 토큰 획득 스크립트")
    print("=" * 60)
    
    # API 연결 테스트
    if not test_api_connection():
        print("❌ API 연결에 실패했습니다. BASE_URL을 확인해주세요.")
        exit(1)
    
    print("\n" + "=" * 60)
    print("📝 로그인 정보를 입력해주세요:")
    print("=" * 60)
    
    username = input("사용자명 (예: admin): ").strip()
    password = input("비밀번호: ").strip()
    
    if not username or not password:
        print("❌ 사용자명과 비밀번호를 모두 입력해주세요.")
        exit(1)
    
    try:
        token = get_jwt_token(username, password)
        save_token_to_config(token)
        
        print("\n" + "=" * 60)
        print("🎉 JWT 토큰 획득 및 저장 완료!")
        print("=" * 60)
        print("이제 프로그램을 실행할 수 있습니다:")
        print("  - GUI 버전: python gui_main.py")
        print("  - 콘솔 버전: python main.py --test")
        
    except Exception as e:
        print(f"\n❌ 토큰 획득 및 저장 실패: {e}")
        print("\n💡 해결 방법:")
        print("  1. 사용자명과 비밀번호를 확인해주세요")
        print("  2. Cloudflare Workers가 정상 작동하는지 확인해주세요")
        print("  3. BASE_URL이 올바른지 확인해주세요")
    
    finally:
        input("\n아무 키나 눌러 종료...")