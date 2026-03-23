@echo off
REM Run daily NBA predictions — compare model spreads/win probs to market lines.
REM Run this AFTER run_nightly.bat, before the next game slate.
REM Usage: run_predictions.bat [YYYY-MM-DD]
REM If no date is given, defaults to tomorrow.

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set LOG_DIR=%PROJECT_ROOT%\logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "tokens=2 delims==" %%I in ('"wmic os get LocalDateTime /value"') do set DT=%%I
set DATESTAMP=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%

set LOG_FILE=%LOG_DIR%\predictions_%DATESTAMP%.log

echo Running outcome tracking + NBA predictions for %1 >> "%LOG_FILE%" 2>&1
echo Log: %LOG_FILE%

set PYTHONPATH=%PROJECT_ROOT%

REM Resolve yesterday's predictions against actual scores first
uv run --project "%PROJECT_ROOT%" python "%PROJECT_ROOT%\downstream\track_outcomes.py" >> "%LOG_FILE%" 2>&1

REM Generate predictions for the next slate
if "%1"=="" (
    uv run --project "%PROJECT_ROOT%" python "%PROJECT_ROOT%\downstream\predictions.py" >> "%LOG_FILE%" 2>&1
) else (
    uv run --project "%PROJECT_ROOT%" python "%PROJECT_ROOT%\downstream\predictions.py" --date %1 >> "%LOG_FILE%" 2>&1
)

echo Done. Exit code: %ERRORLEVEL%
