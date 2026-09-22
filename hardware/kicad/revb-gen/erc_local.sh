#!/bin/bash
# usage: erc_local.sh file.kicad_sch  -> prints report
cp "$1" /opt/kicad10/work/test.kicad_sch
rm -f /opt/kicad10/work/erc.rpt
chroot /opt/kicad10 /usr/bin/kicad-cli sch erc --output /work/erc.rpt --format report --severity-all /work/test.kicad_sch 2>&1 | tail -5
[ -f /opt/kicad10/work/erc.rpt ] && cat /opt/kicad10/work/erc.rpt | tail -30
