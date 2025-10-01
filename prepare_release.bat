@echo off
chcp 65001 > nul
echo ============================================================
echo   배포 패키지 준비 중...
echo ============================================================
echo.

REM 배포 폴더 생성
if not exist "release" mkdir release
if exist "release\*" del /Q release\*

REM 실행 파일 복사
echo [1/3] 실행 파일 복사 중...
copy /Y "dist\ClipboardTranslator.exe" "release\"

REM 사용법 복사
echo [2/3] 사용 설명서 복사 중...
copy /Y "dist\사용법.txt" "release\"

REM Tesseract 설치 파일 복사
echo [3/3] Tesseract 설치 파일 복사 중...
if exist "tesseract-ocr-w64-setup-5.3.3.20231005.exe" (
    copy /Y "tesseract-ocr-w64-setup-5.3.3.20231005.exe" "release\"
) else (
    echo ⚠️  Tesseract 설치 파일을 찾을 수 없습니다.
    echo    https://github.com/UB-Mannheim/tesseract/wiki 에서 다운로드하여
    echo    프로젝트 폴더에 넣어주세요.
)

echo.
echo ============================================================
echo   ✅ 배포 패키지 준비 완료!
echo   📁 폴더: release\
echo ============================================================
echo.
echo 다음 파일들이 준비되었습니다:
dir /B release
echo.
pause
