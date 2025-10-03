@echo off
chcp 65001 >nul
echo ============================================================
echo 🎯 LoadDB(directorkim@scenes.kr)
echo 📋 ArtistSul CMS 데이터베이스 연동
echo ============================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo    Python 3.9 이상을 설치해주세요.
    echo    https://www.python.org/downloads/
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

echo 🚀 프로그램을 시작합니다...
echo ⏹️  중지하려면 Ctrl+C를 누르세요
echo.

REM 메인 프로그램 실행
python main.py

echo.
echo 👋 프로그램이 종료되었습니다.
pause

