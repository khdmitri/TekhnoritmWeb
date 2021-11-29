@ECHO OFF
TIMEOUT 5
start %SystemRoot%\system32\cmd.exe /k d:\TekhnoritmWeb\run_django
TIMEOUT 3
start %SystemRoot%\system32\cmd.exe /k d:\TekhnoritmWeb\run_nginx
TIMEOUT 80
SET ThisScriptsDirectory=%~dp0
SET PowerShellScriptPath=%ThisScriptsDirectory%run_redis.ps1
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""%PowerShellScriptPath%""' -Verb RunAs}";
TIMEOUT 5
start %SystemRoot%\system32\cmd.exe /k d:\TekhnoritmWeb\run_celery
ECHO
TIMEOUT 5
start %SystemRoot%\system32\cmd.exe /k d:\TekhnoritmWeb\run_celery_beat
ECHO