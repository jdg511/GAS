#!/usr/bin/env python3
"""
The Great American Spring - clipper / dynamics circuit models
Illicit Apothecary

Derives the static transfer curve of each clipping topology directly from the
Shockley diode equation and the real component values listed below. No SPICE:
for a static (memoryless) transfer curve the implicit node equation IS the
exact answer, and solving it numerically is more precise than reading points
off a generic SPICE sweep.

    I_d(V) = Is * (exp(V / (N * n * Vt)) - 1)

    Is = saturation current (A)      n  = ideality factor
    N  = diodes in series            Vt = kT/q = 25.85 mV at 300 K (27 C)

Reference level: digital 1.0 == 1.0 V peak at the clipper input.
Supply: 9 V, biased to 4.5 V, so op-amp output saturates at +/-4.5 V.
"""

import numpy as np
from scipy.optimize import brentq

VT = 25.85e-3       # thermal voltage @ 300K
RAIL = 4.5          # op-amp saturation, 9V supply biased at 4.5V

# ---------------------------------------------------------------------------
# Diode library.  Is / n chosen so the modelled Vf matches the datasheet
# forward-voltage points quoted in the comment for each part.
# ---------------------------------------------------------------------------
DIODES = {
    # 1N4148: standard SPICE model (Is=2.52nA, N=1.752). Vf ~0.72V @ 10mA.
    "1N4148":  dict(Is=2.52e-9,  n=1.752, desc="Silicon small-signal, DO-35"),

    # BAT41 Schottky: Vf ~0.45V @ 10mA, sharp low-current knee (n ~1.05).
    "BAT41":   dict(Is=1.20e-7,  n=1.050, desc="Silicon Schottky, DO-35"),

    # Red GaAsP LED (e.g. Kingbright WP7113ID): Vf ~1.85V @ 20mA, n ~1.9.
    "LED_RED": dict(Is=9.00e-18, n=1.900, desc="3mm red LED, GaAsP"),

    # Nexperia PMEG150G20ELP, 150V/2A SiGe rectifier, CFP5 (SOD128).
    # Is/n fitted to the 25C curve of datasheet Fig.3 in the uA-mA region where a
    # clipper works, NOT to the amp-level table rows (those carry ~58 mohm of
    # series resistance, irrelevant at signal currents). Vf 0.44V @ 1mA.
    # n=1.13 vs the 1N4148's 1.75: clips earlier than Si but with a HARDER knee.
    # Not a germanium substitute - Ge is soft and leaky, this is sharp and spec'd
    # at 0.4nA reverse leakage.
    "SIGE":    dict(Is=2.863e-10, n=1.134, desc="PMEG150G20ELP SiGe rectifier, CFP5/SOD128"),

    # 2N3904 base-emitter junction used as a diode. Near-ideal (n ~1.0) so the
    # knee is noticeably sharper/harder than a 1N4148 at the same Vf.
    "2N3904_BE": dict(Is=6.73e-15, n=1.000, desc="2N3904 B-E junction, TO-92"),
}


def diode_current(v, part, series=1):
    """Shockley current through `series` identical diodes stacked in series."""
    d = DIODES[part]
    vth = series * d["n"] * VT
    # clamp the exponent so the solver never overflows
    return d["Is"] * (np.exp(np.clip(v / vth, -80, 80)) - 1.0)


def network_current(v, pos_part, pos_n, neg_part, neg_n):
    """Net current through an anti-parallel diode network at voltage v.

    pos_n diodes of pos_part conduct on the positive half,
    neg_n diodes of neg_part conduct on the negative half.
    Equal parts + equal counts = symmetric.  Unequal = asymmetric.
    """
    return diode_current(v, pos_part, pos_n) - diode_current(-v, neg_part, neg_n)


# ---------------------------------------------------------------------------
# Topology A - diodes in the op-amp feedback loop (Tube Screamer / SD-1 / OCD)
#
#   non-inverting amp, gain = 1 + Rf/Rg, diode network across Rf
#   node equation:  Vin/Rg = Vd/Rf + I_diodes(Vd),   Vout = Vin + Vd
#
# Output keeps rising with unity slope after the diodes conduct, so the curve
# never fully flattens - this is why feedback clippers stay dynamic and touch
# sensitive rather than turning to square wave.
# ---------------------------------------------------------------------------
def feedback_clipper(vin, Rf, Rg, pos_part, pos_n, neg_part, neg_n):
    def residual(vd):
        return vin / Rg - (vd / Rf + network_current(vd, pos_part, pos_n, neg_part, neg_n))

    # bracket generously: Vd can never exceed the rails
    lo, hi = -RAIL * 2.0, RAIL * 2.0
    try:
        vd = brentq(residual, lo, hi, xtol=1e-12, rtol=1e-12, maxiter=200)
    except ValueError:
        vd = np.sign(vin) * RAIL
    return float(np.clip(vin + vd, -RAIL, RAIL))


# ---------------------------------------------------------------------------
# Topology B - series resistor into a shunt diode network (Big Muff / ladder)
#
#   node equation:  (Vin - Vout)/Rs = I_diodes(Vout)
#
# This one DOES flatten: the diodes are a hard clamp to ground, so the output
# asymptotes at the stack's forward voltage regardless of how hard it is hit.
# ---------------------------------------------------------------------------
def shunt_clipper(vin, Rs, pos_part, pos_n, neg_part, neg_n):
    def residual(vout):
        return (vin - vout) / Rs - network_current(vout, pos_part, pos_n, neg_part, neg_n)

    lo, hi = -RAIL * 2.0, RAIL * 2.0
    try:
        vout = brentq(residual, lo, hi, xtol=1e-12, rtol=1e-12, maxiter=200)
    except ValueError:
        vout = np.sign(vin) * RAIL
    return float(np.clip(vout, -RAIL, RAIL))


# ---------------------------------------------------------------------------
# The nine clipping circuits
#
# gain_db  = gain of the stage feeding the clipping network (the shunt
#            topologies need their own gain stage; the feedback ones get theirs
#            from 1 + Rf/Rg, so gain_db is 0 there and Rf/Rg does the work).
# ---------------------------------------------------------------------------
CIRCUITS = [
    dict(key="SI_SYM", name="Silicon Symmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("1N4148", 1), neg=("1N4148", 1), gain_db=0.0,
         blurb="TS808 clipping stage. 2x 1N4148 anti-parallel across Rf."),

    dict(key="SI_ASYM", name="Silicon Asymmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("1N4148", 2), neg=("1N4148", 1), gain_db=0.0,
         blurb="SD-1 clipping stage. 2 series up / 1 down -> strong 2nd harmonic."),

    dict(key="SCHOTTKY_SYM", name="Schottky Symmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("BAT41", 1), neg=("BAT41", 1), gain_db=0.0,
         blurb="Lowest headroom of the feedback set. Compressed, spitty, tight."),

    dict(key="LED_SYM", name="LED Symmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("LED_RED", 1), neg=("LED_RED", 1), gain_db=0.0,
         blurb="Bluesbreaker / OCD. Clips late and loud, big clean headroom."),

    dict(key="LED_SI_ASYM", name="LED / Silicon Asymmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("LED_RED", 1), neg=("1N4148", 1), gain_db=0.0,
         blurb="Widest asymmetry in the set: 1.85V one way, 0.72V the other."),

    dict(key="SIGE_ASYM", name="SiGe Asymmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("SIGE", 2), neg=("SIGE", 1), gain_db=0.0,
         blurb="PMEG150G20ELP SiGe. Early clip, hard knee - tight, not soft."),

    dict(key="TRANSISTOR_BE", name="Transistor B-E Symmetric", topo="feedback",
         Rf=51e3, Rg=4.7e3, pos=("2N3904_BE", 1), neg=("2N3904_BE", 1), gain_db=0.0,
         blurb="2N3904 base-emitter junctions. n~1.0 -> sharper knee than 1N4148."),

    dict(key="LADDER_SYM", name="Ladder Symmetric", topo="shunt",
         Rs=10e3, pos=("1N4148", 3), neg=("1N4148", 3), gain_db=26.0,
         blurb="3+3 series ladder, shunt to ground, after a 26 dB stage. Hard clamp."),

    dict(key="LADDER_ASYM", name="Ladder Asymmetric", topo="shunt",
         Rs=10e3, pos=("1N4148", 3), neg=("1N4148", 2), gain_db=26.0,
         blurb="3 up / 2 down ladder. Hard clamp, offset halves, heavy 2nd harmonic."),
]


def transfer(circuit, vin):
    g = 10.0 ** (circuit["gain_db"] / 20.0)
    v = np.clip(vin * g, -RAIL * 8, RAIL * 8)
    if circuit["topo"] == "feedback":
        return feedback_clipper(v, circuit["Rf"], circuit["Rg"],
                                *circuit["pos"], *circuit["neg"])
    return shunt_clipper(v, circuit["Rs"], *circuit["pos"], *circuit["neg"])


def clip_threshold(circuit):
    """Input voltage at which the curve departs 1 dB from its small-signal slope."""
    vs = np.linspace(1e-4, 3.0, 4000)
    out = np.array([transfer(circuit, v) for v in vs])
    slope0 = out[0] / vs[0]
    ideal = slope0 * vs
    dev_db = 20.0 * np.log10(np.maximum(out, 1e-12) / np.maximum(ideal, 1e-12))
    idx = np.argmax(dev_db < -1.0)
    return (vs[idx], 20.0 * np.log10(vs[idx])) if idx > 0 else (np.nan, np.nan)


if __name__ == "__main__":
    print(f"{'circuit':<26}{'gain dB':>9}{'thresh V':>10}{'thresh dBV':>12}"
          f"{'out@1V':>9}{'out@4V':>9}{'asym':>8}")
    print("-" * 84)
    for c in CIRCUITS:
        vth, dbth = clip_threshold(c)
        o1 = transfer(c, 1.0)
        o4 = transfer(c, 4.0)
        pos = transfer(c, 2.0)
        neg = abs(transfer(c, -2.0))
        asym_db = 20.0 * np.log10(pos / neg)
        print(f"{c['name']:<26}{c['gain_db']:>9.1f}{vth:>10.4f}{dbth:>12.2f}"
              f"{o1:>9.3f}{o4:>9.3f}{asym_db:>8.2f}")
