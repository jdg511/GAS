import re
f=r"C:\Program Files\KiCad\10.0\share\kicad\3dmodels\Connector_Audio.3dshapes\Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal.step"
s=open(f,errors='ignore').read()
pts=re.findall(r"CARTESIAN_POINT\('[^']*',\(([-\d.E+]+),([-\d.E+]+),([-\d.E+]+)\)\)",s)
import statistics
xs=[float(p[0]) for p in pts]; ys=[float(p[1]) for p in pts]; zs=[float(p[2]) for p in pts]
print(len(pts),'x',min(xs),max(xs),'y',min(ys),max(ys),'z',min(zs),max(zs))
# circle centres of the 6.35 jack bore: CIRCLE with radius ~3.2
circ=re.findall(r"#(\d+)\s*=\s*CIRCLE\('[^']*',#(\d+),([\d.E+-]+)\)",s)
print('circles', sorted(set(round(float(c[2]),2) for c in circ))[:40])
