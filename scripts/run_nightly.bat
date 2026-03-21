@echo off
SETLOCAL

SET PROJECT_ROOT=C:\Users\David\CS\hobbies\sports\nba_clv_modeling
SET PYTHONPATH=%PROJECT_ROOT%

cd /d "%PROJECT_ROOT%"

:: Get today's date as YYYY-MM-DD using WMIC (locale-independent)
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set _dt=%%i
set TODAY=%_dt:~0,4%-%_dt:~4,2%-%_dt:~6,2%

if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"
SET LOGFILE=%PROJECT_ROOT%\logs\nightly_%TODAY%.log

echo === Nightly job started %DATE% %TIME% === >> "%LOGFILE%"
uv run python pipeline/nightly_job.py >> "%LOGFILE%" 2>&1
SET EXIT_CODE=%ERRORLEVEL%
echo === Nightly job finished %DATE% %TIME% (exit code %EXIT_CODE%) === >> "%LOGFILE%"

ENDLOCAL
exit /b %EXIT_CODE%
