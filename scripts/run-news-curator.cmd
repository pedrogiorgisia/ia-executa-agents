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
REM --dangerously-skip-permissions: necessário pra rodar sem interação
REM Redireciona output pra arquivo de log
"C:\Users\pedro\AppData\Roaming\npm\claude.cmd" -p "Execute o pipeline em prompts/news/news-master.md. Você está rodando em modo LOCAL (não cloud). Siga todos os passos incluindo o 7 (atualizar historico.md), e PULE o passo 12 (upload pro Drive — desnecessário, os arquivos locais já estão no Drive sincronizado)." --dangerously-skip-permissions > "logs\news-curator-%DATA%.log" 2>&1

exit /b %ERRORLEVEL%
