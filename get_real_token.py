#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 JWT 토큰 획득 스크립트
"""

import requests
import json

def get_jwt_token():
    """JWT 토큰 획득"""
    url = "https://artistsul-cms-worker.directorkim.workers.dev/api/admin/login"
    
    print("=" * 60)
    print("🔐 JWT 토큰 획득")
    print("=" * 60)
    print("실제 관리자 계정 정보를 입력해주세요:")
    
    username = input("사용자명: ").strip()
    password = input("비밀번호: ").strip()
    
    if not username or not password:
        print("❌ 사용자명과 비밀번호를 모두 입력해주세요.")
        return None
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        print(f"🔐 로그인 시도 중...")
        response = requests.post(url, json=data, timeout=30)
        
        print(f"📡 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📡 응답 내용: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('ok'):
                token = result['data']['token']
                expires_in = result['data'].get('expiresIn', 3600)
                print(f"✅ 로그인 성공!")
                print(f"🔑 JWT 토큰: {token}")
                print(f"⏰ 만료 시간: {expires_in}초")
                return token
            else:
                print(f"❌ 로그인 실패: {result.get('error', '알 수 없는 오류')}")
        else:
            print(f"❌ HTTP 오류: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
    
    return None

def save_token_to_config(token):
    """토큰을 config.py에 저장"""
    config_path = "config.py"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip().startswith("JWT_TOKEN ="):
                    f.write(f'JWT_TOKEN = "{token}"  # 실제 JWT 토큰\n')
                else:
                    f.write(line)
        
        print(f"✅ JWT 토큰이 {config_path}에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ config.py 저장 실패: {e}")

if __name__ == "__main__":
    token = get_jwt_token()
    
    if token:
        save_token_to_config(token)
        print("\n🎉 JWT 토큰 설정 완료!")
        print("이제 프로그램을 실행하면 JWT 토큰을 사용합니다.")
    else:
        print("\n❌ JWT 토큰 획득 실패")
        print("관리자 계정 정보를 확인해주세요.")
    
    input("\n아무 키나 눌러 종료...")
