# Registra a tarefa "news-curator-diario" no Task Scheduler do Windows.
# Roda todo dia às 07:00.

$scriptPath = "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes\scripts\run-news-curator.cmd"

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"`"$scriptPath`"`""

$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask `
    -TaskName "news-curator-diario" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Curadoria diaria de noticias de IA - envia email via Resend" `
    -Force

Write-Host ""
Write-Host "Tarefa criada. Detalhes:"
Get-ScheduledTask -TaskName "news-curator-diario" | Format-List TaskName, State, Description
Get-ScheduledTaskInfo -TaskName "news-curator-diario" | Format-List NextRunTime, LastRunTime
