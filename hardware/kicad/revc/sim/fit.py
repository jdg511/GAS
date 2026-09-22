import subprocess, numpy as np, json, os, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
REF = {int(k): v for k, v in json.load(open("../plugin_ref.json")).items()}
LEV = [-18, -12, -6, 0, 6, 12, 18]
def netlist(level, S, Rs, Vref, delta_i, Rc, beta=0.75e-3, vto=-2.0, f=1000):
    amp = 4.36 * 10 ** (level / 20)
    ratio = S / 4.36
    r2 = 1000.0; r1 = r2 * (1 / ratio - 1)
    rref2 = 1000.0; rref1 = rref2 * (15.0 / Vref - 1)
    return f"""* tube stage
.options reltol=1e-4 abstol=1e-12 vntol=1e-7 method=gear
VCC vcc 0 15
VIN src 0 SIN(0 {amp} {f})
R01 src pad {r1}
R02 pad 0 {r2}
C01 pad cc 22n
R03 cc g 68k
R04 g bias 1meg
D01 g k BAT54
RK k bias {Rc}
IOFF 0 k {delta_i}
C02 g 0 10p
J1 d g s JMOD
R05 s 0 {Rs}
R06 vcc d 47k
RREF1 vcc ref {rref1}
RREF2 ref 0 {rref2}
R07 s svn 470k
C03 svn bias 1u
EOP biasr 0 ref svn 1e5
RLIM biasr bias 10
C04 d oc 1u
R08 oc 0 1meg
.model JMOD NJF(VTO={vto} BETA={beta} LAMBDA=0.002 IS=1e-14 CGS=4p CGD=2p)
.model BAT54 D(IS=9.4e-9 N=1.0 RS=2 CJO=10p)
.ic v(bias)={vto + (Vref/Rs/beta)**0.5 + Vref}
.tran 10u 0.6 0.5 10u
.control
run
set wr_singlescale
wrdata {{OUT}} v(oc)
.endc
.end
"""
def one(args):
    level, p, kw = args
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.txt")
        net = netlist(level, *p, **kw).replace("{OUT}", out)
        cir = os.path.join(td, "t.cir"); open(cir, "w").write(net)
        subprocess.run(["ngspice", "-b", cir], capture_output=True, text=True)
        d = np.loadtxt(out)
    tt = np.linspace(0.5, 0.6, 4096, endpoint=False)
    o = np.interp(tt, d[:, 0], d[:, 1]); o -= o.mean()
    X = np.abs(np.fft.rfft(o)) / 4096 * 2
    return level, X[100], [20 * np.log10(X[k] / X[100] + 1e-12) for k in (200, 300)]
def measure(p, **kw):
    with ThreadPoolExecutor(8) as ex:
        res = {L: (a, h) for L, a, h in ex.map(one, [(L, p, kw) for L in LEV])}
    a18 = res[-18][0]
    out = {}
    for L in LEV:
        a, h = res[L]
        out[L] = (20 * np.log10(a / a18) - 18, h)
    return out, a18 / (4.36 * 10 ** (-18 / 20))
def cost(p, verbose=False, **kw):
    S, Rs, Vref, di, Rc = p
    if not (0.05 < S < 0.4 and 300 < Rs < 6000 and 0.05 < Vref < 1.0 and 0 <= di < 50e-6 and 0 <= Rc < 200e3):
        return 1e9
    m, dvfs = measure(p, **kw)
    e = 0
    for L in LEV:
        g0, h0 = REF[L]; g, h = m[L]
        e += ((g - g0) / 0.5) ** 2 + sum(((max(a, -70) - max(b, -70)) / 4) ** 2 for a, b in zip(h, h0))
        if verbose:
            print(f"{L:+3d}: out {g:+6.2f} ({g0:+6.2f})  H2 {h[0]:6.1f} ({h0[0]:6.1f})  H3 {h[1]:6.1f} ({h0[1]:6.1f})")
    if verbose:
        print("drain volts per FS", dvfs)
    return e
if __name__ == "__main__":
    from scipy.optimize import minimize
    x0 = [0.1408, 1650, 0.152, 0.0, 1.0]
    print("start", cost(x0, True))
    best = None
    for start in ([0.1408, 1650, 0.152, 5e-6, 10e3], [0.10, 1200, 0.15, 5e-6, 10e3], [0.18, 2200, 0.2, 3e-6, 10e3]):
        r = minimize(lambda q: cost(q), start, method="Nelder-Mead", options=dict(maxiter=90, xatol=1e-3, fatol=0.05,
                     initial_simplex=None))
        print(r.x, r.fun, flush=True)
        if best is None or r.fun < best.fun: best = r
    print("BEST", list(best.x)); json.dump(list(best.x), open("best_spice.json", "w"))
    cost(best.x, True)
