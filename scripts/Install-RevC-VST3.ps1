$src = 'C:\Users\Jason\GAS-build\repo\cmake-out-win\TheGreatAmericanSpring_artefacts\Release\VST3\The Great American Spring reverb Rev C.vst3'
$dst = 'C:\Program Files\Common Files\VST3\The Great American Spring reverb Rev C.vst3'
Get-ChildItem 'C:\Program Files\Common Files\VST3' | Where-Object { $_.Name -like '*American Spring*' } | ForEach-Object { Write-Output "existing: $($_.Name) $($_.LastWriteTime)" }
$r = robocopy $src $dst /E /R:1 /W:1 /NJH /NJS /NFL /NDL
Write-Output "robocopy exit $LASTEXITCODE"
if (Test-Path "$dst\Contents\x86_64-win\The Great American Spring reverb Rev C.vst3") { Write-Output "VST3 INSTALLED OK" } else { Write-Output "VST3 INSTALL FAILED (needs admin?)" }
