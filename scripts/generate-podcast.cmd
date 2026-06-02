@echo off
REM ============================================
REM podcast-curator — gera podcast diário via NotebookLM
REM Executa após o news-curator (que produz o top.md)
REM ============================================

cd /d "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes"

if not exist "logs" mkdir logs
if not exist "data\podcasts" mkdir data\podcasts

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%h%dt:~10,2%m"

"C:\Users\pedro\AppData\Roaming\npm\claude.cmd" -p "Execute o pipeline em prompts/news/podcast-master.md. Use a Skill notebooklm pra interagir com o NotebookLM. MODO AUTOMATICO — sem usuario presente, rodando via Task Scheduler. NUNCA pause pedindo interacao humana. Se o NotebookLM falhar por qualquer motivo (token expirado, erro de auth, timeout), va IMEDIATAMENTE para o Passo 9.4 (fallback: enviar email so com noticias via scripts/send_email_resend.py). Melhor email so com noticias do que nenhum email." --dangerously-skip-permissions > "logs\podcast-curator-%DATA%.log" 2>&1

exit /b %ERRORLEVEL%
