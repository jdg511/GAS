$vst = 'C:\Program Files\Common Files\VST3\The Great American Spring reverb Rev C.vst3'
if (Test-Path $vst) { Write-Output "VST3 installed: $vst" } else { Write-Output "VST3 NOT found in Common Files" }
$exe = 'C:\Users\Jason\GAS-build\repo\cmake-out-win\TheGreatAmericanSpring_artefacts\Release\Standalone\The Great American Spring reverb Rev C.exe'
Start-Process -FilePath $exe
Start-Sleep -Seconds 6
$p = Get-Process | Where-Object { $_.ProcessName -like 'The Great American Spring reverb Rev C*' }
if ($p) { Write-Output "STANDALONE RUNNING pid $($p.Id) responding=$($p.Responding) title='$($p.MainWindowTitle)'" } else { Write-Output "STANDALONE NOT RUNNING" }
