import pcbnew, os, re
fp=pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_Audio.pretty","Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal")
for m in fp.Models():
    print(m.m_Filename, m.m_Offset.x, m.m_Offset.y, m.m_Offset.z, m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z)
d=r"C:\Program Files\KiCad\10.0\share\kicad\3dmodels\Connector_Audio.3dshapes"
for f in os.listdir(d):
    if 'NCJ6FI-H' in f: print(f, os.path.getsize(os.path.join(d,f)))
f=os.path.join(d,"Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal.wrl")
if os.path.exists(f):
    s=open(f,errors='ignore').read()
    pts=re.findall(r'point\s*\[([^\]]*)\]',s)
    xs=[];ys=[];zs=[]
    for blk in pts:
        nums=[float(v) for v in re.findall(r'-?\d+\.?\d*(?:e-?\d+)?',blk)]
        xs+=nums[0::3]; ys+=nums[1::3]; zs+=nums[2::3]
    k=2.54
    print('x',min(xs)*k,max(xs)*k,'y',min(ys)*k,max(ys)*k,'z',min(zs)*k,max(zs)*k)
