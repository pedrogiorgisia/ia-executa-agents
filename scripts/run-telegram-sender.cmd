@echo off
REM ============================================
REM telegram-sender — dispara 1 noticia/hora
REM Roda todo hora via Task Scheduler (fallback do Railway).
REM O script já verifica horário (07h-22h BRT) e estado no GitHub.
REM ============================================

cd /d "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes"

if not exist "logs" mkdir logs

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%h%dt:~10,2%m"

python scripts\railway_telegram_sender.py >> "logs\telegram-sender-%DATA%.log" 2>&1

exit /b %ERRORLEVEL%
