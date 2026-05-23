@echo off
REM Gera telegram-queue.json do dia e faz push pro GitHub.
REM Roda às 07:15 via Task Scheduler (15 min após o news-curator).

cd /d "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes"

if not exist "logs" mkdir logs

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%h%dt:~10,2%m"

python scripts\generate_telegram_queue.py > "logs\telegram-queue-%DATA%.log" 2>&1

exit /b %ERRORLEVEL%
