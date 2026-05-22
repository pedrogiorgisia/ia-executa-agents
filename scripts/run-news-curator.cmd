@echo off
REM ============================================
REM news-curator — rotina diária local
REM Executado pelo Task Scheduler do Windows.
REM ============================================

REM Vai pro diretório do projeto
cd /d "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes"

REM Cria pasta de logs se não existir
if not exist "logs" mkdir logs

REM Timestamp pra nome do log
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%h%dt:~10,2%m"

REM Roda Claude Code em modo headless (-p) com o prompt
REM NEWS_SKIP_EMAIL=true: pipeline do podcast (que roda 30 min depois) vai enviar email combinado
REM --dangerously-skip-permissions: necessário pra rodar sem interação
REM Redireciona output pra arquivo de log
set NEWS_SKIP_EMAIL=true
"C:\Users\pedro\AppData\Roaming\npm\claude.cmd" -p "Execute o pipeline em prompts/news/news-master.md. Você está rodando em modo LOCAL (não cloud). Siga todos os passos incluindo o 7 (atualizar historico.md), e PULE o passo 12 (upload pro Drive — desnecessário, os arquivos locais já estão no Drive sincronizado). NEWS_SKIP_EMAIL=true está setado: PULE o envio de email no passo 10 (o podcast-master vai enviar email combinado depois)." --dangerously-skip-permissions > "logs\news-curator-%DATA%.log" 2>&1

REM Calcula data atual via Python (mais confiável que wmic no Windows 11)
for /f %%a in ('python -c "from datetime import date; print(date.today())"') do set "HOJE=%%a"
set "TOP_MD=data\news\%HOJE%\top.md"

REM Gera fila do Telegram e faz push pro GitHub (só se o top.md existir)
if exist "%TOP_MD%" (
    echo Gerando telegram-queue.json para %HOJE%... >> "logs\news-curator-%DATA%.log" 2>&1
    python scripts\generate_telegram_queue.py "%TOP_MD%" >> "logs\news-curator-%DATA%.log" 2>&1
    echo Telegram queue: exit code %ERRORLEVEL% >> "logs\news-curator-%DATA%.log" 2>&1
) else (
    echo AVISO: %TOP_MD% nao encontrado — telegram queue nao gerada >> "logs\news-curator-%DATA%.log" 2>&1
)

exit /b %ERRORLEVEL%
