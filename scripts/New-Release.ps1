[CmdletBinding()]
param(
    [string]$Version,
    [switch]$Practice,
    [switch]$SkipBuild,
    [string]$BuildDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Checked {
    param(
        [Parameter(Mandatory)][string]$Program,
        [Parameter(Mandatory)][string[]]$Arguments
    )

    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Program $($Arguments -join ' ')"
    }
}

function Get-ProjectVersion {
    param([Parameter(Mandatory)][string]$CMakePath)

    $cmakeText = Get-Content -LiteralPath $CMakePath -Raw
    $match = [regex]::Match($cmakeText, '(?im)^\s*project\s*\([^\r\n]*?\sVERSION\s+([0-9A-Za-z._-]+)')
    if (-not $match.Success) {
        return $null
    }

    return $match.Groups[1].Value
}

function Get-Sha256Hex {
    param([Parameter(Mandatory)][string]$Path)

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        return ([System.BitConverter]::ToString($sha256.ComputeHash($stream)) -replace '-', '').ToLowerInvariant()
    }
    finally {
        $stream.Dispose()
        $sha256.Dispose()
    }
}

$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$cmakePath = Join-Path $repositoryRoot 'CMakeLists.txt'
$packageScript = Join-Path $PSScriptRoot 'Package-Release.ps1'

Push-Location $repositoryRoot
try {
    $gitRoot = (& git rev-parse --show-toplevel).Trim()
    $normalizedGitRoot = if ($gitRoot) { [System.IO.Path]::GetFullPath($gitRoot).TrimEnd('\', '/') } else { '' }
    $normalizedRepositoryRoot = [System.IO.Path]::GetFullPath($repositoryRoot).TrimEnd('\', '/')
    if ($LASTEXITCODE -ne 0 -or -not [string]::Equals($normalizedGitRoot, $normalizedRepositoryRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Run this script from the tracked GAS repository, not from a copied build folder.'
    }

    $projectVersion = Get-ProjectVersion $cmakePath
    $requestedVersion = if ([string]::IsNullOrWhiteSpace($Version)) { '' } else { $Version.TrimStart('v') }
    if ([string]::IsNullOrWhiteSpace($requestedVersion) -and -not $Practice) {
        $requestedVersion = $projectVersion
    }
    if (-not $Practice -and [string]::IsNullOrWhiteSpace($requestedVersion)) {
        throw 'No release version was supplied and CMakeLists.txt does not declare one. Use -Version <version>.'
    }
    if (-not $Practice -and $projectVersion -and $requestedVersion -ne $projectVersion) {
        throw "Requested version '$requestedVersion' does not match CMakeLists.txt version '$projectVersion'. Update CMake first so the binaries and release name agree."
    }

    $dirtyPaths = @(& git status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not read the Git working-tree status.'
    }
    $isDirty = $dirtyPaths.Count -gt 0
    if ($isDirty -and -not $Practice) {
        throw "The working tree is not clean. Commit or stash all changes before a real release. Use -Practice for a local test only."
    }

    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $releaseId = if ($Practice) { "practice-$timestamp" } elseif ($requestedVersion) { $requestedVersion } else { $timestamp }
    $releaseDirectory = Join-Path $repositoryRoot "releases/$releaseId"
    if (Test-Path -LiteralPath $releaseDirectory) {
        throw "Refusing to overwrite existing release folder '$releaseDirectory'. Choose a new version or remove it yourself after inspection."
    }

    $commit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not resolve the release commit.'
    }

    $effectiveVersion = if ($requestedVersion) { $requestedVersion } else { $timestamp }
    $effectiveBuildDirectory = if ($BuildDirectory) {
        [System.IO.Path]::GetFullPath($BuildDirectory)
    }
    else {
        Join-Path $repositoryRoot '.release-build/windows'
    }

    if (-not $SkipBuild) {
        Invoke-Checked -Program cmake -Arguments @(
            '-S', $repositoryRoot, '-B', $effectiveBuildDirectory, '-G', 'Visual Studio 17 2022', '-A', 'x64',
            '-DSCC_BASE_PLUGIN_FORMATS=Standalone;VST3;LV2',
            '-DSCC_DEPLOY_WINDOWS_VST3_AFTER_BUILD=OFF'
        )

        foreach ($target in @('TheGreatAmericanSpring_Standalone', 'TheGreatAmericanSpring_VST3', 'TheGreatAmericanSpring_LV2')) {
            Invoke-Checked -Program cmake -Arguments @('--build', $effectiveBuildDirectory, '--config', 'Release', '--target', $target, '--parallel', '2')
        }
    }

    New-Item -ItemType Directory -Path $releaseDirectory | Out-Null
    & $packageScript -Platform windows -Version $effectiveVersion -BuildDirectory $effectiveBuildDirectory -OutputDirectory $releaseDirectory
    if ($LASTEXITCODE -ne 0) {
        throw 'Windows artifact packaging failed.'
    }

    $sourceName = if ($requestedVersion) {
        "Source-Code_$requestedVersion`_$timestamp.zip"
    }
    else {
        "Source-Code_$timestamp.zip"
    }
    $sourceArchive = Join-Path $releaseDirectory $sourceName
    Invoke-Checked -Program git -Arguments @('archive', '--format=zip', "--prefix=TheGreatAmericanSpring-$releaseId/", "--output=$sourceArchive", $commit)

    $files = Get-ChildItem -LiteralPath $releaseDirectory -File |
        Where-Object { $_.Name -notin @('release-manifest.json', 'SHA256SUMS.txt') }
    $checksums = foreach ($file in $files) {
        "{0}  {1}" -f (Get-Sha256Hex $file.FullName), $file.Name
    }
    $checksums | Set-Content -LiteralPath (Join-Path $releaseDirectory 'SHA256SUMS.txt') -Encoding ascii

    [ordered]@{
        product = 'The Great American Spring'
        version = $requestedVersion
        releaseId = $releaseId
        timestamp = $timestamp
        commit = $commit
        sourceArchive = $sourceName
        workingTreeWasDirty = $isDirty
        practice = [bool]$Practice
        localPlatforms = @('windows')
        cloudPlatforms = @('windows', 'linux', 'macos-universal')
        formats = @{
            windows = @('Standalone', 'VST3', 'LV2')
            linux = @('Standalone', 'VST3', 'LV2')
            macos = @('Standalone', 'VST3', 'AU', 'LV2')
        }
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $releaseDirectory 'release-manifest.json') -Encoding utf8

    Write-Host "Local release package created: $releaseDirectory"
    if ($isDirty) {
        Write-Warning 'This practice archive contains the committed Git revision only; it intentionally excludes uncommitted changes.'
    }

}
finally {
    Pop-Location
}
