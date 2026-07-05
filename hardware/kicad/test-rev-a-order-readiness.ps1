Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$kicadRoot = $PSScriptRoot
$repoRoot = Split-Path -Parent $kicadRoot
$projectFile = Join-Path $kicadRoot "GAS-Hardware.kicad_sch"
$ercJson = Join-Path $kicadRoot "GAS-Hardware-erc-current.json"
$reportPath = Join-Path $kicadRoot "rev-a-order-readiness.md"

$kicadCli = (Get-Command kicad-cli.exe -ErrorAction Stop).Source

function Add-Line {
    param(
        [Parameter(Position = 0)]
        [object] $Lines,
        [Parameter(Position = 1)]
        [AllowEmptyString()]
        [string] $Line
    )

    $Lines.Add($Line) | Out-Null
}

function Get-ErcViolations {
    param([Parameter(Mandatory = $true)][string] $Path)

    $json = Get-Content $Path -Raw | ConvertFrom-Json
    $violations = @()

    foreach ($sheet in $json.sheets) {
        foreach ($violation in $sheet.violations) {
            $violations += [pscustomobject]@{
                Sheet       = $sheet.path
                Type        = $violation.type
                Severity    = $violation.severity
                Description = $violation.description
                Items       = (($violation.items | ForEach-Object { $_.description }) -join "; ")
            }
        }
    }

    return $violations
}

function Get-EmptyFootprintSymbols {
    $symbols = @()

    foreach ($file in Get-ChildItem -Path $kicadRoot -Filter "*.kicad_sch") {
        $lines = @(Get-Content $file.FullName)

        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -notmatch '\(property\s+"Footprint"\s+""') {
                continue
            }

            $ref = ""
            $value = ""
            $lib = ""
            $min = [Math]::Max(0, $i - 120)

            for ($j = $i; $j -ge $min; $j--) {
                if ($ref -eq "" -and $lines[$j] -match '\(property\s+"Reference"\s+"([^"]+)"') {
                    $ref = $Matches[1]
                }
                if ($value -eq "" -and $lines[$j] -match '\(property\s+"Value"\s+"([^"]*)"') {
                    $value = $Matches[1]
                }
                if ($lib -eq "" -and $lines[$j] -match '\(lib_id\s+"([^"]+)"') {
                    $lib = $Matches[1]
                }
                if ($ref -ne "" -and $value -ne "" -and $lib -ne "") {
                    break
                }
            }

            if ($ref.StartsWith("#")) {
                continue
            }

            $symbols += [pscustomobject]@{
                File  = $file.Name
                Ref   = $ref
                Value = $value
                Lib   = $lib
            }
        }
    }

    return $symbols | Sort-Object File, Ref
}

function Get-SimModelCount {
    $count = 0

    foreach ($file in Get-ChildItem -Path $kicadRoot -Filter "*.kicad_sch") {
        $text = Get-Content $file.FullName -Raw
        $count += ([regex]::Matches($text, '\(property\s+"Sim\.')).Count
    }

    return $count
}

function Get-BoardFootprintSummary {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo[]] $BoardFiles)

    $summary = @()

    foreach ($board in $BoardFiles) {
        $text = Get-Content $board.FullName -Raw
        $footprints = @([regex]::Matches($text, '\(footprint\s+"([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
        $electrical = @($footprints | Where-Object { $_ -notlike "MountingHole*" })

        $summary += [pscustomobject]@{
            File                 = $board.Name
            Footprints           = $footprints.Count
            ElectricalFootprints = $electrical.Count
        }
    }

    return $summary
}

function Invoke-BoardDrc {
    param([Parameter(Mandatory = $true)][System.IO.FileInfo[]] $BoardFiles)

    $summary = @()

    foreach ($board in $BoardFiles) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($board.Name)
        $drcJson = Join-Path $kicadRoot ("{0}.drc.json" -f $baseName)

        & $kicadCli @("pcb", "drc", $board.FullName, "--format", "json", "--output", $drcJson, "--severity-all") | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "kicad-cli DRC failed with exit code $LASTEXITCODE for $($board.Name)"
        }

        $json = Get-Content $drcJson -Raw | ConvertFrom-Json
        $summary += [pscustomobject]@{
            File             = $board.Name
            Report           = [System.IO.Path]::GetFileName($drcJson)
            Violations       = @($json.violations).Count
            UnconnectedItems = @($json.unconnected_items).Count
        }
    }

    return $summary
}

& $kicadCli @("sch", "erc", $projectFile, "--format", "json", "--output", $ercJson, "--severity-all") | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "kicad-cli ERC failed with exit code $LASTEXITCODE"
}

$auditScript = Join-Path $kicadRoot "audit-rev-a-capture.py"
$auditReport = Join-Path $kicadRoot "rev-a-capture-audit.md"
if (Test-Path $auditScript) {
    & python $auditScript --output $auditReport | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "capture audit failed with exit code $LASTEXITCODE"
    }
}

$boardFiles = @(Get-ChildItem -Path $kicadRoot -Filter "*.kicad_pcb" -File)
$boardFootprints = @(Get-BoardFootprintSummary -BoardFiles $boardFiles)
$boardDrc = @(Invoke-BoardDrc -BoardFiles $boardFiles)
$ercViolations = @(Get-ErcViolations -Path $ercJson)
$emptyFootprints = @(Get-EmptyFootprintSymbols)
$simModelCount = Get-SimModelCount

$report = [System.Collections.Generic.List[string]]::new()
Add-Line $report "# GAS Rev A KiCad Order Readiness"
Add-Line $report ""
Add-Line $report "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
Add-Line $report ""
Add-Line $report "This is the manufacturing gate for the current KiCad project. It is intentionally strict: a board should not be ordered until this report has no blockers."
Add-Line $report ""

$blockers = [System.Collections.Generic.List[string]]::new()
if ($boardFiles.Count -eq 0) {
    Add-Line $blockers "No KiCad PCB layout files (*.kicad_pcb) exist yet, so Gerbers, drills, placement files, DRC, and routed copper cannot be produced."
}
elseif (($boardFootprints | Measure-Object ElectricalFootprints -Sum).Sum -eq 0) {
    Add-Line $blockers "PCB layout files are outline-only scaffolds: they contain no non-mounting-hole electrical footprints yet."
}
if (($boardDrc | Measure-Object Violations -Sum).Sum -gt 0 -or ($boardDrc | Measure-Object UnconnectedItems -Sum).Sum -gt 0) {
    Add-Line $blockers "One or more PCB DRC reports still contain violations or unconnected items."
}
if ($ercViolations.Count -gt 0) {
    Add-Line $blockers "Top-level ERC is not clean: $($ercViolations.Count) violations are present."
}
if ($emptyFootprints.Count -gt 0) {
    Add-Line $blockers "Required non-virtual schematic symbols still have empty footprint fields: $($emptyFootprints.Count) symbols."
}
if ($simModelCount -eq 0) {
    Add-Line $blockers "No KiCad/SPICE simulation model properties are present, so KiCad simulations are not configured yet."
}

if ($blockers.Count -eq 0) {
    Add-Line $report "## Status"
    Add-Line $report ""
    Add-Line $report "PASS: no order-readiness blockers detected by this gate."
}
else {
    Add-Line $report "## Status"
    Add-Line $report ""
    Add-Line $report "BLOCKED: this project is not ready to order."
    Add-Line $report ""
    Add-Line $report "## Blockers"
    Add-Line $report ""
    foreach ($blocker in $blockers) {
        Add-Line $report "- $blocker"
    }
}

Add-Line $report ""
Add-Line $report "## Board Files"
Add-Line $report ""
if ($boardFiles.Count -eq 0) {
    Add-Line $report "- none found"
}
else {
    Add-Line -Lines $report -Line "| Board | Footprints | Electrical footprints | DRC violations | Unconnected items | DRC report |"
    Add-Line -Lines $report -Line "| --- | ---: | ---: | ---: | ---: | --- |"
    foreach ($board in $boardFiles) {
        $fp = $boardFootprints | Where-Object File -eq $board.Name | Select-Object -First 1
        $drc = $boardDrc | Where-Object File -eq $board.Name | Select-Object -First 1
        Add-Line $report ("| {0} | {1} | {2} | {3} | {4} | {5} |" -f $board.Name, $fp.Footprints, $fp.ElectricalFootprints, $drc.Violations, $drc.UnconnectedItems, $drc.Report)
    }
}

Add-Line $report ""
Add-Line $report "## ERC Summary"
Add-Line $report ""
Add-Line $report "- Source: GAS-Hardware.kicad_sch"
Add-Line $report "- Report: GAS-Hardware-erc-current.json"
Add-Line $report "- Violations: $($ercViolations.Count)"

if ($ercViolations.Count -gt 0) {
    Add-Line $report ""
    Add-Line -Lines $report -Line "| Count | Type |"
    Add-Line -Lines $report -Line "| ---: | --- |"
    foreach ($group in ($ercViolations | Group-Object Type | Sort-Object Count -Descending)) {
        Add-Line $report ("| {0} | {1} |" -f $group.Count, $group.Name)
    }

    Add-Line $report ""
    Add-Line -Lines $report -Line "| Count | Sheet |"
    Add-Line -Lines $report -Line "| ---: | --- |"
    foreach ($group in ($ercViolations | Group-Object Sheet | Sort-Object Count -Descending)) {
        Add-Line $report ("| {0} | {1} |" -f $group.Count, $group.Name)
    }
}

Add-Line $report ""
Add-Line $report "## Empty Required Footprints"
Add-Line $report ""
if ($emptyFootprints.Count -eq 0) {
    Add-Line $report "- none"
}
else {
    Add-Line -Lines $report -Line "| File | Ref | Value | Symbol |"
    Add-Line -Lines $report -Line "| --- | --- | --- | --- |"
    foreach ($symbol in $emptyFootprints) {
        Add-Line $report ("| {0} | {1} | {2} | {3} |" -f $symbol.File, $symbol.Ref, $symbol.Value, $symbol.Lib)
    }
}

Add-Line $report ""
Add-Line $report "## Simulation Readiness"
Add-Line $report ""
Add-Line $report "- KiCad/SPICE model property count: $simModelCount"
if ($simModelCount -eq 0) {
    Add-Line $report "- Required next step: add SPICE models or simulator-compatible subcircuits for the active audio stages and power blocks before expecting KiCad simulation to run."
}

Set-Content -Path $reportPath -Value $report -Encoding utf8
Write-Host "Order-readiness report written to $reportPath"

if ($blockers.Count -gt 0) {
    exit 1
}
