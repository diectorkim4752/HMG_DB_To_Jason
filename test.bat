@echo off
chcp 65001 >nul
echo ============================================================
echo 🧪 DB → JSON 플러그인 테스트 모드
echo ============================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    pause
    exit /b 1
)

REM 의존성 패키지 설치
echo 📦 의존성 패키지 설치 중...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치 실패!
    pause
    exit /b 1
)

echo.
echo ✅ 설치 완료!
echo.

REM 설정 파일 확인
if not exist "config.py" (
    echo ❌ config.py 파일이 없습니다!
    pause
    exit /b 1
)

echo ⚙️ 설정 확인 중...
findstr "your_jwt_token_here" config.py >nul
if not errorlevel 1 (
    echo ⚠️  경고: JWT 토큰을 설정해주세요!
    echo    config.py 파일에서 JWT_TOKEN 값을 수정하세요.
    echo.
)

echo 🧪 테스트 모드로 실행합니다...
echo    (한 번만 실행하고 종료됩니다)
echo.

REM 테스트 모드로 실행
python main.py --test

echo.
echo 👋 테스트가 완료되었습니다.
pause

