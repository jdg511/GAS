$p = Get-Process | Where-Object { $_.ProcessName -like 'The Great American Spring reverb Rev C*' }
if ($p) { Write-Output "ALREADY RUNNING pid $($p.Id) responding=$($p.Responding)"; exit 0 }
$exe = 'C:\Users\Jason\GAS-build\repo\cmake-out-win\TheGreatAmericanSpring_artefacts\Release\Standalone\The Great American Spring reverb Rev C.exe'
Start-Process -FilePath $exe
Start-Sleep -Seconds 6
$p = Get-Process | Where-Object { $_.ProcessName -like 'The Great American Spring reverb Rev C*' }
if ($p) { Write-Output "RELAUNCHED pid $($p.Id) responding=$($p.Responding)" } else { Write-Output "NOT RUNNING" }
