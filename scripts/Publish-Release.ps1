[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Version
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
        throw 'CMakeLists.txt does not declare a project version.'
    }
    return $match.Groups[1].Value
}

$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$requestedVersion = $Version.TrimStart('v')
$releaseDirectory = Join-Path $repositoryRoot "releases/$requestedVersion"

Push-Location $repositoryRoot
try {
    $workingTree = @(& git status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not read the Git working-tree status.'
    }
    if ($workingTree.Count -gt 0) {
        throw 'Refusing to publish from a dirty working tree. Commit or stash all changes first.'
    }

    $projectVersion = Get-ProjectVersion (Join-Path $repositoryRoot 'CMakeLists.txt')
    if ($requestedVersion -ne $projectVersion) {
        throw "Requested version '$requestedVersion' does not match CMakeLists.txt version '$projectVersion'."
    }
    if (-not (Test-Path -LiteralPath $releaseDirectory -PathType Container)) {
        throw "No local preflight package exists at '$releaseDirectory'. Run New-Release.ps1 first."
    }

    $manifestPath = Join-Path $releaseDirectory 'release-manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "The local package does not contain '$manifestPath'."
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $commit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not resolve the current Git commit.'
    }
    if ($manifest.practice -or $manifest.workingTreeWasDirty -or $manifest.version -ne $requestedVersion -or $manifest.commit -ne $commit) {
        throw 'The local package is not a clean preflight for the current release commit. Run New-Release.ps1 again.'
    }
    if ((Get-ChildItem -LiteralPath $releaseDirectory -Filter '*.zip' -File | Measure-Object).Count -lt 2) {
        throw 'The local preflight package is incomplete: expected both the Windows and source-code ZIP files.'
    }

    $tagName = "v$requestedVersion"
    & git rev-parse -q --verify "refs/tags/$tagName" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        throw "Git tag '$tagName' already exists. Refusing to replace it."
    }

    Invoke-Checked -Program git -Arguments @('tag', '-a', $tagName, $commit, '-m', "Release $tagName")
    Invoke-Checked -Program git -Arguments @('push', 'origin', $tagName)
    Write-Host "Pushed $tagName. GitHub Actions will now build Windows, Linux, and universal macOS packages and create the GitHub Release."
}
finally {
    Pop-Location
}
