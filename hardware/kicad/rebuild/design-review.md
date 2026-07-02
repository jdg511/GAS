# GAS Rev A Schematic Design Review (2026-07-02)

Full-project review pass over the six rebuilt boards: signal-path polarity
trace, mode truth tables, harness pin-map cross-check, DC-offset budget,
stability of the resonance-injection paths, and rail/current budgets.

## Findings — fixed in this pass

### F1. +5VAUX regulator polluted the analog +15V rail (power-backplane)
PS501 (R-78E5.0-0.5, a switching regulator) drew its input from **+15VA**,
the post-bead filtered analog rail. Its input ripple current would inject
switching hash directly into the op-amp supply. Moved its input to
**+15VRAW** (post-DC-DC, pre-bead) — still inside the regulator's 7-28V
range and still behind the module's filtering, but its hash now stays off
the audio rail. (The external-DC doc's wording allowed either reading;
this is the electrically correct one.)

### F2. Right channel dies if the mono switch has a center-off (io-board)
U1D+ (right program buffer input) is fed only from MONO_C, which comes from
the panel switch. The control spec allows a "SPDT **or 3-state** source
switch" — in a center-off position (or with the harness unplugged) U1D+
floats and the right channel produces noise or sticks to a rail. Added
**R25, 1M, MONO_C -> R_RX**: the channel now defaults to stereo with the
switch open; switch action is unaffected (source impedances are ~100R).

## Verified clean

- **Mode truth tables**: clip decode (00 clean / 01 Si / 10 LED / 11 Ge) and
  ext-routing (A=engage, B=series/parallel; Off isolates secondary sends and
  returns) both trace correctly through the relay contact trees.
- **End-to-end wet polarity**: the wet path carries exactly two inversions
  (ext summer, crossfade summer), so wet and dry arrive **in phase** across
  the wet/dry pot — no mid-blend cancellation.
- **Harness pin maps**: every inter-board header pair matches the frozen
  schedule pin-for-pin (P2<->P201, P202<->P101, P203<->P102, P204<->P301,
  P302<->P401, P303<->P402, P304<->P3, P305<->P205, power fanout).
- **Rail budgets**: worst-case +5VAUX relay load ~210mA of the R-78E's
  500mA; OPA1656 output legs peak ~23mA into 600R (rated ~35mA); panel
  switch coil currents 12-60mA, within contact ratings.
- **Flyback diode orientations** on all relay coils.

## Minor notes (bench items, no change made)

1. **Absolute polarity**: the wet/dry blend buffer is inverting (per spec),
   so the whole unit inverts absolute polarity. If that ever matters,
   swapping hot/cold assignment at the output drivers restores it — one-net
   change, deferred.
2. **DC on the crossfade pot**: recovery-amp offset (x34 gain, direct
   coupled) puts up to ~±17mV DC on TANK_MIX, i.e. across the crossfade pot
   — possible slight scratchiness when turning. The filter board's input
   cap blocks it from propagating further. DNP slots (C175-C178) and bench
   trims exist if it bothers.
3. **Q-injection resonance paths** (HPF/LPF): fixed mild positive feedback
   (loop gain < ~0.7 worst case, stable) until the control-backplane pass
   wires the Q-pot ends, as the spec defers. Listed as a bench-listening
   item.
4. **Class-B primary sends**: bias diodes D101/D102/D121/D122 stay DNP per
   spec; crossover is corrected in-loop by the 53MHz op-amp. If HF grit is
   audible on the primary tanks at low levels, populating the bias spreaders
   is the bench remedy.
