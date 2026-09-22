#!/bin/bash
# usage: export_fab.sh  (uses /opt/kicad10/work/circuit-board.kicad_pcb, already DRC-clean and zone-filled)
set -e
W=/opt/kicad10/work
FAB=/home/claude/gas-revb/out/fab-RevB/circuit-board
rm -rf $FAB; mkdir -p $FAB/gerbers
cd /opt/kicad10
rm -rf $W/gerb; mkdir -p $W/gerb
chroot /opt/kicad10 /usr/bin/kicad-cli pcb export gerbers --output /work/gerb/ --layers "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts,F.Fab" --subtract-soldermask --no-protel-ext /work/circuit-board.kicad_pcb 2>&1 | tail -1
chroot /opt/kicad10 /usr/bin/kicad-cli pcb export drill --output /work/gerb/ --format excellon --excellon-units mm --excellon-zeros-format decimal --excellon-separate-th --generate-map --map-format pdf --drill-origin absolute /work/circuit-board.kicad_pcb 2>&1 | tail -1
chroot /opt/kicad10 /usr/bin/kicad-cli pcb export pos --output /work/gerb/circuit-board-centroid-RevB.csv --format csv --units mm --side front --exclude-dnp /work/circuit-board.kicad_pcb 2>&1 | tail -1 || true
chroot /opt/kicad10 /usr/bin/kicad-cli pcb export pdf --output /work/gerb/circuit-board-assembly-top-RevB.pdf --layers "F.Fab,F.SilkS,Edge.Cuts" /work/circuit-board.kicad_pcb 2>&1 | tail -1
chroot /opt/kicad10 /usr/bin/kicad-cli pcb render --output /work/gerb/circuit-board-RevB-top.png --side top --width 2000 --height 1700 --quality high /work/circuit-board.kicad_pcb 2>&1 | tail -1
chroot /opt/kicad10 /usr/bin/kicad-cli pcb render --output /work/gerb/circuit-board-RevB-iso.png --side top --rotate "-40,0,25" --width 2000 --height 1500 --quality high /work/circuit-board.kicad_pcb 2>&1 | tail -1
chroot /opt/kicad10 /usr/bin/kicad-cli sch export pdf --output /work/gerb/circuit-board-schematic-RevB.pdf /work/circuit-board.kicad_sch 2>&1 | tail -1
cp $W/gerb/*.gbr $W/gerb/*.drl $W/gerb/*.gbrjob $FAB/gerbers/ 2>/dev/null || true
cp $W/gerb/*-drl_map.pdf $FAB/gerbers/ 2>/dev/null || true
cd $FAB/gerbers && zip -q ../circuit-board-gerbers-RevB.zip * && cd ..
cp $W/gerb/circuit-board-centroid-RevB.csv $W/gerb/circuit-board-assembly-top-RevB.pdf $W/gerb/circuit-board-RevB-top.png $W/gerb/circuit-board-RevB-iso.png $W/gerb/circuit-board-schematic-RevB.pdf $FAB/
cp /home/claude/gas-revb/out/circuit-board-BOM-RevB.csv $FAB/
cp $W/final-drc.rpt $FAB/circuit-board-DRC-RevB.rpt 2>/dev/null || true
ls -la $FAB $FAB/gerbers | head -40
