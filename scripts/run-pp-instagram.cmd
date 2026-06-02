@echo off
REM ============================================================
REM pp-travel instagram motor — rotina diaria 10h BRT
REM Executado pelo Task Scheduler do Windows.
REM
REM Workflow (apenas GERA — NAO posta):
REM   1. Sourcing (run_pp_sourcing.py) — digest.md do dia
REM   2. Claude headless gera content.json (parte criativa)
REM   3. post.py gera midia + render + preview.html (sem postar)
REM
REM Pedro abre dashboard.html quando quiser, revisa, e fala
REM "posta o de hoje" no chat. Ai Claude interativo roda --publish.
REM ============================================================

cd /d "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes"

REM Pasta de logs
if not exist "logs" mkdir logs

REM Timestamp pra nome do log
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATA=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%h%dt:~10,2%m"
set "LOG=logs\pp-instagram-%DATA%.log"

echo. >> "%LOG%"
echo ============================================================ >> "%LOG%"
echo Inicio: %DATA% >> "%LOG%"
echo ============================================================ >> "%LOG%"

REM ===== Passo 1: Sourcing =====
echo. >> "%LOG%"
echo [1/3] Sourcing (run_pp_sourcing.py) >> "%LOG%"
python -X utf8 scripts\run_pp_sourcing.py >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [FAIL] sourcing falhou >> "%LOG%"
  exit /b 1
)

REM ===== Passo 2: Claude headless gera content.json =====
echo. >> "%LOG%"
echo [2/3] Claude headless gera content.json >> "%LOG%"

set PROMPT=Voce esta executando a skill instagram-motor (SKILL.md em .claude/skills/instagram-motor/). Tarefa: gerar content.json para o post de hoje da PP-Travel. Passos: (1) determine pilar do dia via pages/pp-travel/pilares.md (rotacao semanal); (2) leia configs (guia-objetivos.md no topo, voice, formatos, sourcing, ideias/disponiveis.md, ideias/usadas.md, historico.md); (3) leia digest.md ja gerado em data/instagram/pp-travel/HOJE/digest.md; (4) gere 5 candidatos seguindo o checklist do pilar correspondente do guia; (5) escolha o melhor candidato; (6) salve em data/instagram/pp-travel/HOJE/content.json com schema completo (pilar, formato, tema, kicker, headline_html, sub_pill, photo_prompt OU video_prompt, caption, first_comment, hook_source, linhas_frase se reflexivo); (7) adicione os 4 candidatos nao escolhidos em pages/pp-travel/ideias/disponiveis.md. NAO POSTE. NAO RODE post.py. APENAS gere content.json.

"C:\Users\pedro\AppData\Roaming\npm\claude.cmd" -p "%PROMPT%" --dangerously-skip-permissions >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [FAIL] claude headless falhou >> "%LOG%"
  exit /b 1
)

REM ===== Passo 3: post.py (modo generate — gera midia/render/preview, NAO posta) =====
echo. >> "%LOG%"
echo [3/3] post.py (generate mode — gera midia + render + preview) >> "%LOG%"
python -X utf8 scripts\post.py >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [FAIL] post.py falhou >> "%LOG%"
  exit /b 1
)

echo. >> "%LOG%"
echo ============================================================ >> "%LOG%"
echo Fim com sucesso. Conteudo pronto pra revisao do Pedro. >> "%LOG%"
echo Abra: data\instagram\pp-travel\_dashboard.html >> "%LOG%"
echo ============================================================ >> "%LOG%"

exit /b 0
