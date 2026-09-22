"""Port of gas::tube::TriodeStage / TriodeStageFS (plugin TriodeModels.h), dynamic, for sine tests."""
import numpy as np
from triode import Ip, solve_plate, B, Rp, Rk
mu,ex,kg1,kp,kvb=72.45,1.631,517.4,211.1,12705.7
Rg, Rgs, Cc, Is, nVt = 1e6, 68e3, 22e-9, 1e-5, 0.217
ip,vk,vpq,g = np.load('tri_consts.npy')
# plate table
cut=-vk
while Ip(np.array([B]),np.array([cut]))[0] > 0.001*ip and cut>-60: cut-=0.05
pmin, pmax = cut-1.0, 3.0
vgs=np.linspace(pmin,pmax,2048); ptab=solve_plate(vgs)
gx=np.linspace(-1.0,120.0,2048)
lo=np.full_like(gx,-1.0); hi=gx+1
for _ in range(60):
    m=(lo+hi)/2; f=m+Rgs*Is*np.exp(m/nVt)-gx; lo=np.where(f<0,m,lo); hi=np.where(f<0,hi,m)
gtab=(lo+hi)/2
def run(level_db, fs=176400, f=1000, secs=0.6):
    n=int(fs*secs); t=np.arange(n)/fs
    x=10**(level_db/20)*np.sin(2*np.pi*f*t)*vk
    dt=1/fs; decay=np.exp(-dt/(Rg*Cc)); cpa=dt/Cc
    cap=0.0; out=np.empty(n)
    for i in range(n):
        wb=(x[i]-cap)-vk
        if wb>-1.0:
            vg=np.interp(wb,gx,gtab); cap+=(wb-vg)/Rgs*cpa
        else: vg=wb
        cap*=decay
        vp=np.interp(vg,vgs,ptab); out[i]=-(vp-vpq)/(g*vk)
    seg=out[int(0.5*fs):int(0.6*fs)]; seg=seg-seg.mean()
    X=np.abs(np.fft.rfft(seg))/len(seg)*2; k=int(round(f*0.1))
    return 20*np.log10(X[k]), [20*np.log10(X[j*k]/X[k]+1e-12) for j in (2,3)]
if __name__=="__main__":
    res={}
    for L in (-18,-12,-6,0,6,12,18):
        res[L]=run(L); print(L,res[L])
    import json; json.dump(res,open('plugin_ref.json','w'))
