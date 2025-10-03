# 🎯 LoadDB(directorkim@scenes.kr)

ArtistSul CMS 데이터베이스에서 메시지 데이터를 주기적으로 가져와 JSON 파일로 저장하는 자동화 플러그인입니다.

## ⚠️ **중요한 보안 안내**

**현재 이 프로그램은 개발용으로 설정되어 있습니다:**

- **JWT 토큰 없이** API에 접근 가능
- **누구나** 데이터를 가져올 수 있는 상태
- **개인정보 유출 위험**이 있으므로 **프로덕션 환경에서는 반드시 JWT 토큰을 설정**해야 합니다

## ✨ 주요 기능

- 🔄 **주기적 실행**: 설정된 간격(초/분)마다 자동 실행
- 📊 **DB 연동**: ArtistSul CMS API를 통한 메시지 데이터 조회
- 💾 **JSON 저장**: 타임스탬프가 포함된 JSON 파일 자동 생성
- 📝 **실시간 로그**: 콘솔 및 파일 로그 출력
- ⚙️ **설정 관리**: `config.py`에서 모든 설정 중앙 관리
- 🔄 **자동 재시도**: 네트워크 오류 시 지수적 백오프로 재시도
- 🛡️ **에러 처리**: 다양한 오류 상황에 대한 안전한 처리

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 3.9 이상 설치 확인
python --version

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. 설정 파일 수정

`config.py` 파일에서 다음 설정을 수정하세요:

```python
# API 설정 (Cloudflare Workers)
BASE_URL = "https://artistsul-cms-worker.directorkim.workers.dev"
JWT_TOKEN = None  # 개발용: JWT 토큰 없이 작동 (보안상 위험 - 프로덕션에서는 반드시 설정 필요)

# 실행 설정
INTERVAL_SECONDS = 60  # 60초마다 실행
FETCH_LIMIT = 50       # 한 번에 가져올 메시지 수
```

**⚠️ 보안 주의사항:**
- 현재 `JWT_TOKEN = None`으로 설정되어 있어 **인증 없이** API에 접근합니다
- **프로덕션 환경**에서는 반드시 실제 JWT 토큰을 설정해야 합니다

### 3. 실행

```bash
# 일반 모드 (주기적 실행)
python main.py

# 테스트 모드 (한 번만 실행)
python main.py --test
```

## 📁 프로젝트 구조

```
PINTOOL_DBToJason/
├── main.py              # 메인 실행 파일
├── config.py            # 설정 파일
├── db_client.py         # API 클라이언트
├── data_handler.py      # JSON 저장 로직
├── logger.py           # 로깅 시스템
├── requirements.txt    # 의존성 패키지
├── README.md          # 프로젝트 설명
├── output/            # JSON 파일 저장 폴더
└── logs/             # 로그 파일 저장 폴더
```

## ⚙️ 설정 옵션

### config.py 주요 설정

| 설정 | 기본값 | 설명 |
|------|--------|------|
| `BASE_URL` | `"https://artistsul-cms-worker.directorkim.workers.dev"` | API 기본 URL (Cloudflare Workers) |
| `JWT_TOKEN` | `None` | 인증 토큰 (개발용: None, 프로덕션: 실제 토큰 필요) |
| `INTERVAL_SECONDS` | `60` | 실행 간격 (초) |
| `FETCH_LIMIT` | `50` | 한 번에 조회할 메시지 수 |
| `OUTPUT_DIR` | `"./output"` | JSON 파일 저장 경로 |
| `JSON_FILENAME` | `"messages.json"` | 고정 JSON 파일명 (갱신 방식) |
| `USE_FIXED_FILENAME` | `True` | 고정 파일명 사용 여부 (True: 갱신, False: 새 파일) |
| `LOG_TO_CONSOLE` | `True` | 콘솔 로그 출력 여부 |
| `LOG_TO_FILE` | `True` | 파일 로그 저장 여부 |

## 📊 실행 예시

### 콘솔 출력 예시

```
============================================================
🎯 DB → JSON 자동 저장 플러그인
📋 ArtistSul CMS 데이터베이스 연동
============================================================
🔄 주기적 실행 모드로 시작합니다...
⏹️ 중지하려면 Ctrl+C를 누르세요

[2025-01-18 12:00:00] 🔍 API 연결 테스트 중...
[2025-01-18 12:00:01] ✅ API 연결 성공!
[2025-01-18 12:00:01] 🔄 메인 루프 시작
[2025-01-18 12:00:01] 🔄 실행 사이클 #1 시작
[2025-01-18 12:00:01] 📅 메시지 조회: 2025-01-11 ~ 2025-01-18, 페이지: 1, 크기: 50
[2025-01-18 12:00:02] ✅ 메시지 조회 성공: 50개 (총 3페이지)
[2025-01-18 12:00:02] 💾 JSON 갱신 완료: messages.json (50개 메시지)
[2025-01-18 12:00:02] ✅ 50개 메시지 갱신 완료 → ./output/messages.json
[2025-01-18 12:00:02] ⏰ 다음 실행까지 60초 대기...
```

### JSON 파일 예시

```json
{
  "metadata": {
    "exportedAt": "2025-01-18T12:00:02.123456",
    "totalCount": 50,
    "source": "ArtistSul CMS",
    "version": "1.0"
  },
  "messages": [
    {
      "id": 28331542,
      "fileNumber": "20251201-0001",
      "createdAt": "2025-12-01T16:22:13+09:00",
      "senderType": "상처준사람",
      "target": "딸",
      "message": "딸아. 내가 미안해.",
      "hidden": false
    }
  ]
}
```

## 🔧 고급 사용법

### 1. 커스텀 날짜 범위 설정

```python
# db_client.py에서 수정
def get_messages(self, start_date="2025-01-01", end_date="2025-01-18"):
    # 특정 날짜 범위로 조회
```

### 2. 로그 레벨 변경

```python
# logger.py에서 수정
console_handler.setLevel(logging.DEBUG)  # 더 자세한 로그
```

### 3. 파일 정리 자동화

```python
# data_handler.py의 cleanup_old_files() 메서드 사용
data_handler.cleanup_old_files(keep_days=7)  # 7일 이상 된 파일 삭제
```

## 🛠️ 문제 해결

### 자주 발생하는 문제

1. **API 연결 실패**
   - `config.py`의 `JWT_TOKEN` 확인
   - 네트워크 연결 상태 확인

2. **권한 오류**
   - `output/` 폴더 쓰기 권한 확인
   - 관리자 권한으로 실행

3. **메모리 부족**
   - `FETCH_LIMIT` 값 줄이기 (50 → 20)
   - `INTERVAL_SECONDS` 늘리기 (60 → 300)

### 로그 확인

```bash
# 로그 파일 위치
./logs/app.log

# 실시간 로그 모니터링 (Linux/Mac)
tail -f ./logs/app.log
```

## 📈 성능 최적화

- `FETCH_LIMIT`을 100으로 설정 (API 최대값)
- `INTERVAL_SECONDS`를 적절히 조정 (너무 짧으면 API 부하)
- 정기적으로 오래된 JSON 파일 정리

## 🔒 보안 고려사항

### ⚠️ **현재 개발용 설정 (보안 위험)**

**현재 상태:**
- `JWT_TOKEN = None`으로 설정되어 있음
- **누구나** API에 접근하여 데이터를 가져올 수 있음
- **개인정보 유출 위험**이 매우 높음

**프로덕션 환경에서 반드시 해야 할 일:**
1. **JWT 토큰 설정**: `config.py`에서 `JWT_TOKEN = "실제_토큰_값"`
2. **Cloudflare Workers 보안 강화**: API 엔드포인트에 JWT 인증 필수화
3. **IP 화이트리스트**: 특정 IP만 접근 허용
4. **Rate Limiting**: 과도한 요청 방지

### 일반 보안 고려사항
- JWT 토큰을 환경 변수로 관리 권장
- 로그 파일에 민감한 정보 포함 주의
- 네트워크 보안 설정 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. Python 버전 (3.9 이상)
2. 의존성 패키지 설치 상태
3. `config.py` 설정 값
4. 로그 파일의 오류 메시지

---

**개발자**: 성은님  
**버전**: 1.0  
**최종 업데이트**: 2025-01-18

