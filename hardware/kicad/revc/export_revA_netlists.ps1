$cli = 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
$k = 'C:\Users\Jason\GAS-build\repo\hardware\kicad'
$out = Join-Path $k 'revc\revA-netlists'
New-Item -ItemType Directory -Force $out | Out-Null
foreach ($b in 'io-board','power-backplane','tank-driver-recovery','ext-tank-routing','crossfade-feedback-wet') {
  & $cli sch export netlist --format kicadsexpr --output (Join-Path $out "$b.net") (Join-Path $k "$b.kicad_sch") 2>&1 | Select-Object -Last 2
  & $cli pcb drc --severity-error --output (Join-Path $out "$b-drc.rpt") (Join-Path $k "$b.kicad_pcb") 2>&1 | Select-Object -Last 3
}
Get-ChildItem $out | Select-Object Name, Length
