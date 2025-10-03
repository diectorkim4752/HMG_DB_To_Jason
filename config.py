# -*- coding: utf-8 -*-
"""
DB → JSON 자동 저장 플러그인 설정 파일
ArtistSul CMS 데이터베이스 연동 설정
"""

# API 설정 (하드코딩)
BASE_URL = "https://artistsul-cms-worker.directorkim.workers.dev"
JWT_TOKEN = "None"

# 출력 설정
OUTPUT_DIR = "./output"
JSON_FILENAME_PREFIX = "messages"
JSON_FILENAME = "messages.json"  # 고정 파일명 (갱신 방식)
USE_FIXED_FILENAME = True  # True: 고정 파일명, False: 타임스탬프 포함

# 실행 설정
INTERVAL_SECONDS = 5
FETCH_LIMIT = 50
AUTO_START = True  # 프로그램 실행 시 자동으로 데이터 수집 시작

# 로그 설정
LOG_TO_CONSOLE = True
LOG_TO_FILE = True
LOG_FILE_PATH = "./logs/app.log"

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY = 5

# 데이터베이스 쿼리 설정
DEFAULT_START_DATE = "2025-01-01"
DEFAULT_END_DATE = None

# API 엔드포인트
API_ENDPOINTS = {
    "messages": "/api/messages",
    "login": "/api/admin/login",
    "export": "/api/messages/export"
}

# 요청 헤더
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "DBToJSON-Plugin/1.0"
}
