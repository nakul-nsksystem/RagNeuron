@echo off
setlocal EnableDelayedExpansion

:: ==========================================
:: RagNeuron Windows Launcher (Legacy docker-compose)
:: ==========================================

:: Check for GPU
set GPU_AVAILABLE=0
nvidia-smi >nul 2>&1
if %ERRORLEVEL%==0 (
    set GPU_AVAILABLE=1
    for /f "skip=1 tokens=1 delims=," %%i in ('nvidia-smi --query-gpu=name --format=csv,noheader 2^>nul') do set GPU_NAME=%%i
)

:: Get mode from argument
set MODE=%~1

if "%MODE%"=="" (
    if !GPU_AVAILABLE!==1 (
        echo GPU detected: !GPU_NAME!
        echo.
        echo Select deployment mode:
        echo   1 - Local ingestion GPU + Docker Qdrant + Local API
        echo   2 - Full Docker stack
        echo   3 - Ingest data only
        echo   4 - API only
        echo.
        set /p MODE=Select [1]: 
        if "!MODE!"=="" set MODE=1
    ) else (
        echo No GPU detected. Using Docker mode.
        set MODE=2
    )
)

:: Stop existing containers
echo Stopping existing containers...
docker-compose down >nul 2>&1

:: Mode 1
if "%MODE%"=="1" goto :mode1
:: Mode 2
if "%MODE%"=="2" goto :mode2
:: Mode 3
if "%MODE%"=="3" goto :mode3
:: Mode 4
if "%MODE%"=="4" goto :mode4

:: Invalid
echo.
echo Usage: run-legacy.bat [1^|2^|3^|4]
echo.
echo   1 - Local ingestion GPU + Docker Qdrant + Local API
echo   2 - Full Docker stack
echo   3 - Ingest data only
echo   4 - API only
goto :end

:mode1
echo.
echo === Mode 1: Local ingestion + Docker Qdrant + Local API ===
echo.
echo Starting Qdrant...
docker-compose up -d qdrant
timeout /t 3 /nobreak >nul

echo.
echo Ingesting data...
uv run python -m src.ingest
if !ERRORLEVEL! neq 0 (
    echo.
    echo ERROR: Ingestion failed!
    pause
    exit /b 1
)

echo.
echo Starting API at http://localhost:8769 ...
uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
goto :end

:mode2
echo.
echo === Mode 2: Full Docker Stack ===
echo.
docker-compose up -d

echo.
echo =========================================
echo RAG Neuron is running!
echo =========================================
echo.
echo   API:      http://localhost:8769
echo   Qdrant:   http://localhost:6333
echo   Docs:     http://localhost:8769/docs
echo.
echo To ingest data, run:
echo   docker exec rag-neuron-api uv run python -m src.ingest
echo.
goto :end

:mode3
echo.
echo === Ingest Mode: Data ingestion only ===
echo.
echo Starting Qdrant...
docker-compose up -d qdrant
timeout /t 3 /nobreak >nul

echo.
echo Ingesting data...
uv run python -m src.ingest
goto :end

:mode4
echo.
echo === API Mode: Starting API only ===
echo.
uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
goto :end

:end
endlocal
