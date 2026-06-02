# Registra notebooklm-keepalive com 6 triggers diarios (03,07,11,15,19,23h)
# 07:00 garante token renovado 30min antes do podcast (07:30)

$scriptPath = "g:\Meu Drive\20-empresas\projetos-paralelos\01-ativas\01-empresa-ia-pedro\02-maquina-agentes\scripts\keep-alive-notebooklm.cmd"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument ("/c `"`"" + $scriptPath + "`"`"")

$t1 = New-ScheduledTaskTrigger -Daily -At "03:00"
$t2 = New-ScheduledTaskTrigger -Daily -At "07:00"
$t3 = New-ScheduledTaskTrigger -Daily -At "11:00"
$t4 = New-ScheduledTaskTrigger -Daily -At "15:00"
$t5 = New-ScheduledTaskTrigger -Daily -At "19:00"
$t6 = New-ScheduledTaskTrigger -Daily -At "23:00"

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "notebooklm-keepalive" -Action $action -Trigger @($t1,$t2,$t3,$t4,$t5,$t6) -Settings $settings -Description "Renova token NotebookLM 6x/dia — 07:00 garante token fresco antes do podcast 07:30" -Force

Write-Host "Tarefa registrada:"
Get-ScheduledTask -TaskName "notebooklm-keepalive" | Format-List TaskName, State, Description
Get-ScheduledTaskInfo -TaskName "notebooklm-keepalive" | Format-List NextRunTime, LastRunTime
