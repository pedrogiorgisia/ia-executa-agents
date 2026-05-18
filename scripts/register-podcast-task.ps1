# Registra a tarefa "podcast-curator-diario" no Task Scheduler do Windows.
# Roda todo dia às 07:30 (30 min depois do news-curator-diario).

$scriptPath = "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes\scripts\generate-podcast.cmd"

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"`"$scriptPath`"`""

$trigger = New-ScheduledTaskTrigger -Daily -At "07:30"

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask `
    -TaskName "podcast-curator-diario" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Gera podcast diario via NotebookLM, envia email combinado (podcast + noticias)" `
    -Force

Write-Host ""
Write-Host "Tarefa criada. Detalhes:"
Get-ScheduledTask -TaskName "podcast-curator-diario" | Format-List TaskName, State, Description
Get-ScheduledTaskInfo -TaskName "podcast-curator-diario" | Format-List NextRunTime, LastRunTime
