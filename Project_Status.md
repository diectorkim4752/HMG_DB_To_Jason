# LoadDB(directorkim@scenes.kr) - 프로젝트 상태 보고서

## 📋 현재 진행 상황

### ✅ 완료된 작업
1. **GitHub 저장소 클론 완료**
   - 저장소: https://github.com/diectorkim4752/PINTOOL_SimpleDB_To_Jason.git
   - 로컬 경로: `C:\Users\belie\PINTOOL_SimpleDB_To_Jason`
   - 클론 성공

2. **프로젝트 구조 분석 완료**
   - Python 기반 DB → JSON 자동 저장 플러그인
   - ArtistSul CMS 데이터베이스 연동
   - 주요 파일들:
     - `main.py`: 메인 실행 파일
     - `config.py`: 설정 파일
     - `db_client.py`: API 클라이언트
     - `data_handler.py`: JSON 저장 로직
     - `gui_main.py`: GUI 인터페이스
     - `requirements.txt`: 의존성 패키지

3. **프로젝트 기능 파악**
   - 주기적 실행 (설정 가능한 간격)
   - DB 연동을 통한 메시지 데이터 조회
   - JSON 파일 자동 생성 및 저장
   - 실시간 로그 출력
   - GUI 인터페이스 제공

### ⏳ 대기 중인 작업
1. **Python 설치 필요**
   - 현재 시스템에 Python이 설치되어 있지 않음
   - Python 3.9 이상 버전 설치 필요
   - 설치 후 pip을 통한 의존성 패키지 설치 예정

2. **의존성 설치**
   - `requirements.txt`에 명시된 패키지들:
     - requests>=2.31.0
     - pandas>=2.0.0
     - schedule>=1.2.0
     - python-dotenv>=1.0.0
     - python-dateutil>=2.8.0

3. **설정 테스트 및 확인**
   - API 연결 테스트
   - 설정 파일 검증
   - 실행 테스트

### 📝 다음 단계
1. **Python 설치** (사용자 작업 필요)
   - https://www.python.org/downloads/ 에서 다운로드
   - 설치 시 "Add Python to PATH" 체크박스 선택 필수
   - 또는 Microsoft Store에서 Python 설치 가능

2. **Python 설치 후 자동 진행될 작업**
   - 의존성 패키지 설치
   - 프로젝트 설정 테스트
   - 실행 환경 검증

### ⚠️ 주의사항
- 현재 프로젝트는 **개발용 설정**으로 되어 있음
- `JWT_TOKEN = "None"`으로 설정되어 있어 보안상 위험
- 프로덕션 환경에서는 반드시 실제 JWT 토큰 설정 필요

### 📁 프로젝트 구조
```
PINTOOL_SimpleDB_To_Jason/
├── main.py              # 메인 실행 파일
├── config.py            # 설정 파일
├── db_client.py         # API 클라이언트
├── data_handler.py      # JSON 저장 로직
├── gui_main.py          # GUI 인터페이스
├── logger.py           # 로깅 시스템
├── requirements.txt    # 의존성 패키지
├── README.md          # 프로젝트 설명
├── run.bat            # 실행 배치 파일
├── run_gui.bat        # GUI 실행 배치 파일
├── test.bat           # 테스트 배치 파일
├── output/            # JSON 파일 저장 폴더
└── logs/             # 로그 파일 저장 폴더
```

### 🎯 프로젝트 목적
LoadDB(directorkim@scenes.kr) - ArtistSul CMS 데이터베이스에서 메시지 데이터를 주기적으로 가져와 JSON 파일로 저장하는 자동화 플러그인

---
**업데이트 시간**: 2025-01-18  
**상태**: Python 설치 대기 중
