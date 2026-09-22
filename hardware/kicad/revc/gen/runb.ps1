param([string]$m, [string]$stages = "sch,pcb,route,pour,drc", [switch]$bg)
$g = 'C:\Users\Jason\GAS-build\repo\hardware\kicad\revc\gen'
$log = "$g\logs\$m.log"; $err = "$g\logs\$m.err"
New-Item -ItemType Directory -Force "$g\logs" | Out-Null
$p = Start-Process -FilePath 'C:\Program Files\KiCad\10.0\bin\python.exe' -ArgumentList @('-u', "$g\build.py", $m, $stages) -WorkingDirectory $g -RedirectStandardOutput $log -RedirectStandardError $err -WindowStyle Hidden -PassThru
if (-not $bg) { $p.WaitForExit(); Get-Content $log; Get-Content $err | Select-String -NotMatch "image handler" }
else { "started $($p.Id)" }
