@echo off
setlocal

cd /d "%~dp0"

set "HTTP_PROXY=http://127.0.0.1:7891"
set "HTTPS_PROXY=http://127.0.0.1:7891"

echo ============================================
echo Starting AI Pre-sales Assistant...
echo Project directory: %cd%
echo Proxy: 127.0.0.1:7891
echo URL: http://localhost:8501
echo ============================================
echo.

if not exist ".\.venv\Scripts\streamlit.exe" (
    echo ERROR: .venv\Scripts\streamlit.exe not found.
    echo Please make sure this BAT file is in the project root directory.
    echo.
    pause
    exit /b 1
)

.\.venv\Scripts\streamlit.exe run app_streamlit.py --server.port 8501

echo.
echo Streamlit stopped.
pause
