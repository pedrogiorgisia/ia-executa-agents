@echo off
REM ============================================
REM keep-alive-notebooklm — renova token do NotebookLM a cada 4h
REM ============================================

cd /d "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes"

if not exist "logs" mkdir logs

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%h%dt:~10,2%m"

echo [%DATA%] Tentando refresh silencioso... >> "logs\notebooklm-keepalive.log"
notebooklm auth refresh --quiet >> "logs\notebooklm-keepalive.log" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [%DATA%] Refresh silencioso falhou. Tentando via cookies do Chrome... >> "logs\notebooklm-keepalive.log"
    notebooklm auth refresh --browser-cookies chrome >> "logs\notebooklm-keepalive.log" 2>&1
)

echo [%DATA%] Keep-alive concluido. ERRORLEVEL=%ERRORLEVEL% >> "logs\notebooklm-keepalive.log"

exit /b 0
