import fit, numpy as np
p = [4.36/31.9*1.0, 2200.0, 15*825/100825, 0.0, 0.001]
print("S", p[0], "Vref", p[2], "Iq uA", p[2]/p[1]*1e6)
ref = None
for beta, vto in ((0.75e-3, -2.0), (0.45e-3, -2.0), (1.2e-3, -2.0), (0.75e-3, -0.7), (0.75e-3, -4.5), (2.0e-3, -1.0)):
    m, dv = fit.measure(p, beta=beta, vto=vto)
    if ref is None: ref = dv
    print(f"beta {beta*1e3:.2f} mA/V2 Vp {vto}: drain V/FS {dv*4.36:.3f} (level vs typical {20*np.log10(dv/ref):+.2f} dB)")
    for L in fit.LEV:
        g0, h0 = fit.REF[L]; g, h = m[L]
        print(f"   {L:+3d}: out {g:+6.2f} ({g0:+6.2f})  H2 {h[0]:6.1f} ({h0[0]:6.1f})  H3 {h[1]:6.1f} ({h0[1]:6.1f})")
