#!/bin/bash
# usage: finalize.sh routed.kicad_pcb  -> adds zones, stitching vias, refills, DRC, exports fab package
set -e
cd /home/claude/gas-revb
python3 - "$1" <<'PY'
import sys; sys.path.insert(0,'/home/claude/gas-revb')
from sexp import parse, dump, find, find_all, Sym
t=parse(open(sys.argv[1]).read())[0]
rect=[g for g in find_all(t,'gr_rect') if find(g,'layer')[1]=='Edge.Cuts'][0]
W=float(find(rect,'end')[1]); H=float(find(rect,'end')[2])
def zone(layer,name,uid):
    pts=[[Sym('xy'),0.5,0.5],[Sym('xy'),W-0.5,0.5],[Sym('xy'),W-0.5,H-0.5],[Sym('xy'),0.5,H-0.5]]
    return [Sym('zone'),[Sym('net'),'AGND'],[Sym('layer'),layer],[Sym('uuid'),uid],[Sym('name'),name],[Sym('hatch'),Sym('edge'),0.5],
            [Sym('connect_pads'),Sym('yes'),[Sym('clearance'),0.3]],[Sym('min_thickness'),0.25],
            [Sym('fill'),Sym('yes'),[Sym('thermal_gap'),0.5],[Sym('thermal_bridge_width'),0.5],[Sym('island_removal_mode'),0]],
            [Sym('polygon'),[Sym('pts')]+pts]]
t=[c for c in t if not (isinstance(c,list) and c[0]=='zone')]
t.append(zone('F.Cu','AGND_top','c0a7d000-0000-4000-8000-000000000001'))
t.append(zone('B.Cu','AGND_bottom','c0a7d000-0000-4000-8000-000000000002'))
open('/opt/kicad10/work/fin0.kicad_pcb','w').write(dump(t)+'\n')
PY
PAD_VIAS=0 python3 stitch.py /opt/kicad10/work/fin0.kicad_pcb /opt/kicad10/work/fin.kicad_pcb 8
cd /opt/kicad10
chroot /opt/kicad10 /usr/bin/kicad-cli pcb drc --output /work/fin-drc.rpt --format report --severity-all --refill-zones --save-board /work/fin.kicad_pcb 2>&1 | tail -1
grep "^\[" /opt/kicad10/work/fin-drc.rpt | grep -v lib_footprint | sort | uniq -c | sort -rn
grep -A3 "unconnected_items\|clearance\|short" /opt/kicad10/work/fin-drc.rpt | grep -v lib_footprint | head -20
