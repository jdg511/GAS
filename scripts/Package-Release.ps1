[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('windows', 'macos', 'linux')]
    [string]$Platform,

    [Parameter(Mandatory)]
    [string]$Version,

    [Parameter(Mandatory)]
    [string]$BuildDirectory,

    [Parameter(Mandatory)]
    [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-SafeFilePart {
    param([Parameter(Mandatory)][string]$Value)

    return ($Value -replace '[^A-Za-z0-9._-]', '-')
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

$buildRoot = (Resolve-Path -LiteralPath $BuildDirectory).Path
$artifactRoot = Join-Path $buildRoot 'TheGreatAmericanSpring_artefacts/Release'
if (-not (Test-Path -LiteralPath $artifactRoot -PathType Container)) {
    throw "No JUCE Release artifacts were found at '$artifactRoot'. Build the Release targets before packaging."
}

$releaseRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null

$safeVersion = Get-SafeFilePart $Version
$archiveName = "TheGreatAmericanSpring_$safeVersion`_$Platform.zip"
$archivePath = Join-Path $releaseRoot $archiveName
if (Test-Path -LiteralPath $archivePath) {
    throw "Refusing to overwrite an existing package: '$archivePath'. Choose a new release folder."
}

$formatExtensions = @{
    VST3 = '.vst3'
    AU = '.component'
    LV2 = '.lv2'
}
$formats = @('Standalone', 'VST3', 'AU', 'LV2') |
    Where-Object { Test-Path -LiteralPath (Join-Path $artifactRoot $_) -PathType Container }
if ($formats.Count -eq 0) {
    throw "No expected plug-in format folders were found under '$artifactRoot'."
}

$stageRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("gas-release-" + [guid]::NewGuid().ToString('N'))

try {
    New-Item -ItemType Directory -Path $stageRoot | Out-Null
    foreach ($format in $formats) {
        $sourceFormatDirectory = Join-Path $artifactRoot $format
        $stagedFormatDirectory = Join-Path $stageRoot $format
        New-Item -ItemType Directory -Path $stagedFormatDirectory | Out-Null

        if ($format -eq 'Standalone') {
            Get-ChildItem -LiteralPath $sourceFormatDirectory -Force | ForEach-Object {
                Copy-Item -LiteralPath $_.FullName -Destination $stagedFormatDirectory -Recurse -Force
            }
            continue
        }

        $extension = $formatExtensions[$format]
        $bundles = @(Get-ChildItem -LiteralPath $sourceFormatDirectory -Directory -Force |
            Where-Object { $_.Name.EndsWith($extension, [System.StringComparison]::OrdinalIgnoreCase) })
        if ($bundles.Count -eq 0) {
            throw "Expected a $extension bundle under '$sourceFormatDirectory', but none was found."
        }
        foreach ($bundle in $bundles) {
            Copy-Item -LiteralPath $bundle.FullName -Destination $stagedFormatDirectory -Recurse -Force
        }
    }

    $readmePath = Join-Path $stageRoot 'PACKAGE-README.txt'
    @(
        'The Great American Spring release package'
        "Version: $Version"
        "Platform: $Platform"
        "Formats: $($formats -join ', ')"
        'macOS packages are unsigned unless the release process adds signing and notarization.'
    ) | Set-Content -LiteralPath $readmePath -Encoding utf8

    Compress-Archive -LiteralPath (Get-ChildItem -LiteralPath $stageRoot -Force | ForEach-Object FullName) `
        -DestinationPath $archivePath -CompressionLevel Optimal
}
finally {
    if (Test-Path -LiteralPath $stageRoot) {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force
    }
}

$hash = Get-Sha256Hex $archivePath
$checksumPath = Join-Path $releaseRoot "$archiveName.sha256"
"$hash  $archiveName" | Set-Content -LiteralPath $checksumPath -Encoding ascii

[ordered]@{
    product = 'The Great American Spring'
    version = $Version
    platform = $Platform
    formats = $formats
    package = $archiveName
    sha256 = $hash
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $releaseRoot "$archiveName.json") -Encoding utf8

Write-Host "Packaged: $archivePath"
Write-Host "SHA-256: $hash"
