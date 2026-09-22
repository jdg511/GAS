import numpy as np
from scipy.optimize import minimize
import jfet3 as J
from triode import harm
def with_fixed_norm(beta,Vp,Iq,Rs,S,Rc,geff0):
    Vov=np.sqrt(Iq/beta); fn=J.make(beta,Vp,Vov,Rs,S,Rc)
    return lambda x: (fn(x)[0]*fn(x)[2]/geff0, None, None)
def run(Vov0):
    if Vov0 is None:
        p=np.load('best3.npy')
    else:
        res=None
        for Rs0 in (800,2000):
            r=minimize(lambda q: J.cost([Vov0,*q]),[Rs0,0.13,1e3],method='Nelder-Mead',options=dict(maxiter=300,xatol=1e-3,fatol=1e-2))
            if res is None or r.fun<res.fun: res=r
        p=np.array([Vov0,*res.x])
    Vov,Rs,S,Rc=p; Iq=J.B0*Vov**2
    g0=J.make(J.B0,J.VP0,*p)(np.array([0.]))[2]
    print(f"== Vov {Vov:.3f} Rs {Rs:.0f} S {S:.4f} Rc {abs(Rc):.0f} Iq {Iq*1e6:.1f} uA gm_eff {g0*1e3:.3f} mS")
    for beta in (0.45e-3,0.75e-3,1.05e-3):
        fn=with_fixed_norm(beta,J.VP0,Iq,Rs,S,abs(Rc),g0)
        print(f" beta {beta*1e3:.2f} mA/V2  Vov {np.sqrt(Iq/beta):.3f}")
        J.evaluate(fn,True)
    return p
p=run(None); p2=run(0.35); np.save('best35.npy',p2)
