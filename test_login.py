#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그인 테스트 스크립트
"""

import requests
import json

def test_login():
    """로그인 테스트"""
    url = "https://artistsul-cms-worker.directorkim.workers.dev/api/admin/login"
    
    # 여러 가능한 계정 정보 시도
    test_accounts = [
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "password"},
        {"username": "admin", "password": "123456"},
        {"username": "admin", "password": "admin123"},
        {"username": "directorkim", "password": "admin"},
        {"username": "directorkim", "password": "password"},
    ]
    
    for account in test_accounts:
        try:
            print(f"🔐 로그인 시도: {account['username']} / {account['password']}")
            
            response = requests.post(url, json=account, timeout=10)
            print(f"📡 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📡 응답 내용: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get('ok'):
                    token = result['data']['token']
                    print(f"✅ 로그인 성공! JWT 토큰: {token}")
                    return token
                else:
                    print(f"❌ 로그인 실패: {result.get('error', '알 수 없는 오류')}")
            else:
                print(f"❌ HTTP 오류: {response.text}")
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
    
    print("❌ 모든 계정으로 로그인 실패")
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 로그인 테스트 스크립트")
    print("=" * 60)
    
    token = test_login()
    
    if token:
        print(f"\n🎉 JWT 토큰 획득 성공!")
        print(f"토큰: {token}")
        print(f"\n이 토큰을 Cloudflare Workers의 Variables and Secrets에 입력하세요:")
        print(f"Variable name: JWT_TOKEN")
        print(f"Value: {token}")
    else:
        print(f"\n❌ JWT 토큰 획득 실패")
        print(f"실제 관리자 계정 정보를 확인해주세요.")
    
    input("\n아무 키나 눌러 종료...")
