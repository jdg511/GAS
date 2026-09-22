param([string]$script, [string]$a1="", [string]$a2="", [string]$a3="")
& 'C:\Program Files\KiCad\10.0\bin\python.exe' "C:\Users\Jason\GAS-build\repo\hardware\kicad\revc\gen\$script" $a1 $a2 $a3 2>&1
