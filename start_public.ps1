@echo off
echo ============================================
echo  STELLAR Public Launch - Pre-flight Check
echo ============================================
echo.

echo [1/4] Kill stale python processes on 8420...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8420.*LISTENING"') do taskkill /PID %%a /F 2>nul

echo [2/4] Start MemGuard (port 5050)...
start /B python "C:\Users\Administrator\.qclaw\workspace-agent-d9479bde\silicon-civilization-kb\memguard\server.py" > nul 2>&1

echo [3/4] Start STELLAR Dashboard (port 8420, 0.0.0.0)...
start /B python -u "C:\Users\Administrator\.qclaw\workspace-agent-d9479bde\anima-agent\src\anima_agent\dashboard\server.py" --host 0.0.0.0 > nul 2>&1

echo [4/4] Waiting for services...
timeout /t 3 /nobreak > nul

echo.
echo === Service Status ===
netstat -ano | findstr ":5050.*LISTENING" && echo   MemGuard  :5050 OK || echo   MemGuard  :5050 FAIL
netstat -ano | findstr ":8420.*LISTENING" && echo   STELLAR   :8420 OK || echo   STELLAR   :8420 FAIL
netstat -ano | findstr ":5052.*LISTENING" && echo   Polaris   :5052 OK || echo   Polaris   :5052 NOT RUNNING

echo.
echo === Quick API test ===
curl -s http://127.0.0.1:8420/api/version 2>nul | findstr "STELLAR" > nul && echo   STELLAR API: OK || echo   STELLAR API: FAIL
curl -s http://127.0.0.1:5050/ 2>nul > nul && echo   MemGuard  root: OK || echo   MemGuard  root: FAIL

echo.
echo Done. Access at: https://wlmhan.tail306b25.ts.net/stellar/
pause