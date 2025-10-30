@echo off
REM Quick start script for Streamlit web interface
REM Run this from the web_interface directory

echo.
echo ========================================
echo NHS Strategic Analysis - Web Interface
echo ========================================
echo.

REM Check if .env exists in parent directory
if not exist "..\\.env" (
    echo ERROR: .env file not found in parent directory!
    echo.
    echo Please create .env file with your OpenAI API key:
    echo   OPENAI_API_KEY=sk-...
    echo.
    pause
    exit /b 1
)

REM Check if ChromaDB exists
if not exist "..\\chroma_db_test" (
    echo WARNING: ChromaDB not found!
    echo.
    echo Please run the ingestion pipeline first:
    echo   python run_full_pipeline.py
    echo.
    pause
)

REM Install requirements if needed
echo Checking dependencies...
pip install -q streamlit plotly pandas

echo.
echo ========================================
echo Starting Streamlit app...
echo ========================================
echo.
echo Opening http://localhost:8501 in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
