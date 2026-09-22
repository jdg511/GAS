$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\Jason\GAS-build\repo'
$log = 'C:\Users\Jason\GAS-build\repo\revc-build.log'
"=== configure $(Get-Date) ===" | Out-File $log
cmake -S . -B cmake-out-win -G "Visual Studio 17 2022" -A x64 2>&1 | Tee-Object -FilePath $log -Append | Out-Null
"=== build $(Get-Date) ===" | Out-File $log -Append
cmake --build cmake-out-win --config Release --target TheGreatAmericanSpring_Standalone TheGreatAmericanSpring_VST3 -- /m 2>&1 | Tee-Object -FilePath $log -Append | Out-Null
"=== exit $LASTEXITCODE $(Get-Date) ===" | Out-File $log -Append
Write-Output "BUILD EXIT $LASTEXITCODE"
