import numpy as np
mu,ex,kg1,kp,kvb=72.45,1.631,517.4,211.1,12705.7
def Ip(vp,vg):
    vp=np.maximum(vp,1e-9)
    a=kp*(1/mu+vg/np.sqrt(kvb+vp*vp)); sp=np.where(a>40,a,np.log1p(np.exp(np.minimum(a,40))))
    e1=vp/kp*sp; return np.where(e1>0,2*e1**ex/kg1,0)
B,Rp,Rk=250,47e3,470
def solve_plate(vg):
    lo=np.zeros_like(vg); hi=np.full_like(vg,B)
    for _ in range(60):
        mid=(lo+hi)/2; f=B-mid-Rp*Ip(mid,vg); lo=np.where(f>0,mid,lo); hi=np.where(f>0,hi,mid)
    return (lo+hi)/2
lo,hi=0,B/(Rp+Rk)
for _ in range(80):
    m=(lo+hi)/2; f=Ip(B-m*Rp,-m*Rk)-m; lo,hi=(m,hi) if f>0 else (lo,m)
ip=(lo+hi)/2; vk=ip*Rk; vpq=solve_plate(np.array([-vk]))[0]
d=0.002; g=abs(solve_plate(np.array([-vk+d]))[0]-solve_plate(np.array([-vk-d]))[0])/(2*d)
print("Ip mA",ip*1e3,"Vk",vk,"Vp",vpq,"gain",g)
# grid: Vgk + Rgs*Is*exp(Vgk/nVt)=x
Rgs,Is,nVt=68e3,1e-5,0.217
def grid(x):
    lo=np.full_like(x,-60.); hi=x+1
    for _ in range(80):
        mid=(lo+hi)/2; f=mid+Rgs*Is*np.exp(np.minimum(mid/nVt,200))-x; lo=np.where(f<0,mid,lo); hi=np.where(f<0,hi,mid)
    return (lo+hi)/2
def stage(xfs):   # static, no cap charge
    wb=xfs*vk - vk
    vg=grid(wb)
    return -(solve_plate(vg)-vpq)/(g*vk)
np.save('tri_consts.npy',np.array([ip,vk,vpq,g]))
def harm(fn,level_db,N=4096):
    t=np.arange(N); x=10**(level_db/20)*np.sin(2*np.pi*t*8/N); y=fn(x)
    Y=np.abs(np.fft.rfft(y))/N*2; fund=Y[8]
    return 20*np.log10(fund), [20*np.log10(Y[8*k]/fund+1e-12) for k in (2,3,4,5)], y.mean()
if __name__=="__main__":
    for L in (-18,-12,-6,-3,0,3,6,9,12,18):
        f,h,dc=harm(stage,L); print(f"in {L:+3d} dBFS out {f:+6.2f}  H2 {h[0]:6.1f} H3 {h[1]:6.1f} H4 {h[2]:6.1f} H5 {h[3]:6.1f} dc {dc:+.3f}")
    xs=np.array([-6,-4,-3,-2,-1.5,-1,-.5,0,.5,1,1.5,2,3,4,6.])
    print(np.round(stage(xs),3))
