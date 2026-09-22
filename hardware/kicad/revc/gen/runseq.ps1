param([string[]]$mods)
$g = 'C:\Users\Jason\GAS-build\repo\hardware\kicad\revc\gen'
foreach ($m in $mods) {
  $log = "$g\logs\$m.log"; $err = "$g\logs\$m.err"
  $p = Start-Process -FilePath 'C:\Program Files\KiCad\10.0\bin\python.exe' -ArgumentList @('-u', "$g\build.py", $m, 'sch,pcb,route,pour,drc') -WorkingDirectory $g -RedirectStandardOutput $log -RedirectStandardError $err -WindowStyle Hidden -PassThru
  $p.WaitForExit()
}
