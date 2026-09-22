import numpy as np, sys
from scipy.optimize import minimize
from triode import stage as tri, harm
LEV=[-18,-12,-6,-3,0,3,6,9,12,18]
tri_h=[harm(tri,L,N=1024) for L in LEV]
Vt=0.02585
def bisect(f,lo,hi,n=55):
    for _ in range(n):
        m=(lo+hi)/2; s=f(m)>0; hi=np.where(s,m,hi); lo=np.where(s,lo,m)
    return (lo+hi)/2
ISD,ND=9.4e-9,1.0   # BAT54 fit: 240 mV @ 100 uA
def make(beta,Vp,Vov,Rs,S,Rc,Rgs=68e3,Delta=0.0):
    Iq=beta*Vov**2; Vgsq=Vp+Vov; Vgq=Vgsq+Iq*Rs; Vcl=Vgq+Delta
    gm=2*np.sqrt(beta*Iq); geff=gm/(1+gm*Rs)
    def Id_vgs(v): return np.where(v>Vp, beta*(v-Vp)**2, 0)
    def fn(x):
        wb=Vgq+x*S
        def f(vg):
            I=(wb-vg)/Rgs; vd=vg-Vcl-I*Rc
            return I - ISD*(np.exp(np.clip(vd/(ND*Vt),-60,60))-1)
        vg=bisect(lambda v:-f(v), np.minimum(wb,Vcl)-1, np.maximum(wb,Vcl)+1)
        vg=np.where(wb<Vcl, wb, vg)
        vgs=bisect(lambda v: v+Id_vgs(v)*Rs-vg, np.full_like(vg,Vp-3), vg)
        vgs=np.minimum(vgs,0.45)
        return (Id_vgs(vgs)-Iq)/(geff*S), Iq, geff
    return fn
def evaluate(fn,verbose=False):
    g=lambda x: fn(x)[0]
    err=0; xs=np.linspace(-4,4,81)
    err+=np.mean((g(xs)-tri(xs))**2)*50
    for L,(f0,h0,d0) in zip(LEV,tri_h):
        f,h,d=harm(g,L,N=1024)
        err+=((f-f0)/1.5)**2+sum(((max(a,-80)-max(b,-80))/8)**2 for a,b in zip(h[:2],h0[:2]))
        if verbose: print(f"{L:+3d}: out {f:+6.2f} ({f0:+6.2f})  H2 {h[0]:6.1f} ({h0[0]:6.1f})  H3 {h[1]:6.1f} ({h0[1]:6.1f})")
    return err
B0,VP0=0.75e-3,-2.0
def cost(p):
    Vov,Rs,S,Rc=p
    if not(0.05<Vov<0.45 and 0<=Rs<20e3 and 0.02<S<2 and 0<=Rc<500e3): return 1e9
    return evaluate(make(B0,VP0,Vov,Rs,S,Rc))
if __name__=="__main__":
    best=None
    for V0 in (0.2,0.35):
      for Rs0 in (500,3000):
        for S0 in (0.1,0.3):
          res=minimize(cost,[V0,Rs0,S0,30e3],method='Nelder-Mead',options=dict(maxiter=350,xatol=1e-3,fatol=1e-2))
          print(np.round(res.x,4),round(res.fun,2),flush=True)
          if best is None or res.fun<best.fun: best=res
    print("BEST",best.x,best.fun); np.save('best3.npy',best.x)
    evaluate(make(B0,VP0,*best.x),True)
