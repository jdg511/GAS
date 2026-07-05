Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$kicadRoot = Join-Path $repoRoot "kicad"
$outRoot = Join-Path $kicadRoot "release-exports\\rev-a-release"

$kicadCli = (Get-Command kicad-cli.exe -ErrorAction Stop).Source

function Invoke-KiCad {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments
    )

    & $kicadCli @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "kicad-cli failed with exit code $LASTEXITCODE for arguments: $($Arguments -join ' ')"
    }
}

$schematicFiles = @(
    @{ Name = "top-level"; File = "GAS-Hardware.kicad_sch"; ExportBOM = $true; ExportNetlist = $true; RunERC = $true },
    @{ Name = "io-board"; File = "io-board.kicad_sch"; ExportBOM = $false; ExportNetlist = $false; RunERC = $false },
    @{ Name = "tank-driver-recovery"; File = "tank-driver-recovery.kicad_sch"; ExportBOM = $false; ExportNetlist = $false; RunERC = $false },
    @{ Name = "ext-tank-routing"; File = "ext-tank-routing.kicad_sch"; ExportBOM = $false; ExportNetlist = $false; RunERC = $false },
    @{ Name = "crossfade-feedback-wet"; File = "crossfade-feedback-wet.kicad_sch"; ExportBOM = $false; ExportNetlist = $false; RunERC = $false },
    @{ Name = "filter-clipper"; File = "filter-clipper.kicad_sch"; ExportBOM = $false; ExportNetlist = $false; RunERC = $false },
    @{ Name = "power-backplane"; File = "power-backplane.kicad_sch"; ExportBOM = $false; ExportNetlist = $false; RunERC = $false }
)

$dirs = @(
    $outRoot,
    (Join-Path $outRoot "pdf"),
    (Join-Path $outRoot "bom"),
    (Join-Path $outRoot "netlist"),
    (Join-Path $outRoot "erc"),
    (Join-Path $outRoot "pcb"),
    (Join-Path $outRoot "drc")
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

foreach ($entry in $schematicFiles) {
    $inputFile = Join-Path $kicadRoot $entry.File
    $pdfOut = Join-Path $outRoot ("pdf\\{0}.pdf" -f $entry.Name)

    Invoke-KiCad -Arguments @("sch", "export", "pdf", $inputFile, "--output", $pdfOut, "--exclude-pdf-property-popups", "--exclude-pdf-hierarchical-links", "--exclude-pdf-metadata")

    if ($entry.RunERC) {
        $ercJsonOut = Join-Path $outRoot ("erc\\{0}-erc.json" -f $entry.Name)
        $ercReportOut = Join-Path $outRoot ("erc\\{0}-erc.txt" -f $entry.Name)
        Invoke-KiCad -Arguments @("sch", "erc", $inputFile, "--output", $ercJsonOut, "--format", "json", "--severity-all")
        Invoke-KiCad -Arguments @("sch", "erc", $inputFile, "--output", $ercReportOut, "--format", "report", "--severity-all")
    }

    if ($entry.ExportNetlist) {
        $netlistOut = Join-Path $outRoot ("netlist\\{0}.net" -f $entry.Name)
        Invoke-KiCad -Arguments @("sch", "export", "netlist", $inputFile, "--output", $netlistOut, "--format", "kicadsexpr")
    }

    if ($entry.ExportBOM) {
        $bomOut = Join-Path $outRoot ("bom\\{0}.csv" -f $entry.Name)
        Invoke-KiCad -Arguments @("sch", "export", "bom", $inputFile, "--output", $bomOut, "--fields", "Reference,Value,Footprint,Datasheet,QUANTITY,DNP", "--labels", "Ref,Value,Footprint,Datasheet,Qty,DNP")
    }
}

$pcbFiles = Get-ChildItem -Path $kicadRoot -Filter "*.kicad_pcb" -File | Sort-Object Name

foreach ($pcb in $pcbFiles) {
    $pcbCopyOut = Join-Path $outRoot ("pcb\\{0}" -f $pcb.Name)
    $drcJsonOut = Join-Path $outRoot ("drc\\{0}-drc.json" -f $pcb.BaseName)
    $drcReportOut = Join-Path $outRoot ("drc\\{0}-drc.txt" -f $pcb.BaseName)

    Copy-Item -Path $pcb.FullName -Destination $pcbCopyOut -Force
    Invoke-KiCad -Arguments @("pcb", "drc", $pcb.FullName, "--output", $drcJsonOut, "--format", "json", "--severity-all")
    Invoke-KiCad -Arguments @("pcb", "drc", $pcb.FullName, "--output", $drcReportOut, "--format", "report", "--severity-all")
}

$supportFiles = @(
    "rev-a-release-manifest.csv",
    "rev-a-order-readiness.md",
    "place-rev-a-board-footprints.py"
)

foreach ($supportFile in $supportFiles) {
    $source = Join-Path $kicadRoot $supportFile
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination (Join-Path $outRoot $supportFile) -Force
    }
}

Write-Host "Rev A KiCad release exports written to $outRoot"
