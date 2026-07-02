# Rev A Clean Rebuild — Tank Driver / Recovery Board

Branch: `rev-a-clean-rebuild`. Board 1 of 6, taken end-to-end first per plan.

## What exists now

| Artifact | Status |
| --- | --- |
| `../tank-driver-recovery.kicad_sch` | Full electrical capture, 97 components, **ERC = 0** |
| `../sim/tank-driver-recovery-sim/` | Simulation testbench project, **ERC = 0**, **runs in ngspice with no errors** |
| `../tank-driver-recovery.kicad_pcb` | Netlist-synced board, 90 footprints placed by stage, outline + M3 holes + AGND pours, **DRC errors = 0** (13 silk warnings), routing not yet done |
| `gen_tdr.py` | Generates both schematics from one circuit definition — edit this, not the .kicad_sch |
| `gen_tdr_pcb.py` | Generates the board placement from the same circuit definition |
| `run_sim.py` | Runs the testbench through KiCad's bundled ngspice.dll and sanity-checks levels |

## Verified simulation results (0.5 Vpk 1 kHz drive, ±15 V rails)

- Primary send: unity gain, 0.52 Vpk into the 8R tank model (~65 mA pk), op-amp
  pre-driver swings ±1.16 V to correct the class-B follower dead zone in-loop
- Primary recovery: 20 mV tank return -> 0.69 Vpk out (gain 34)
- Secondary send: gain 2.2 into the 800R tank model; recovery -> 0.86 Vpk
- Left/right channels identical; no convergence errors over 60 ms

## Engineering decisions made during capture (vs. the written spec)

1. **Feedback point**: R108/R128 feedback is taken from `PRI_OUT_L/R`
   (after the BD139/BD140 followers) instead of the op-amp output pin. With
   the bias diodes DNP per spec, the followers would otherwise run open-loop
   class-B with gross crossover distortion. In-loop feedback is the standard
   fix and simulation confirms clean output. D101/D102/D121/D122 stay as DNP
   bias-spreader reserves exactly as specced.
2. **Tank cable landings** (`J101-J108`): spec defers RCA vs shielded-wire.
   Chosen: JST XH 2-pin board landings (stock footprint, cheap, crimp
   harness to the tanks' RCA plugs). Swappable later without net changes.
3. **Recovery input coupling**: direct-coupled by default via 0R jumpers
   R183-R186, with DNP film caps C175-C178 in parallel positions, so the
   bench choice in the spec stays a solder-jumper choice.
4. **Decoupling**: C299 + C300 bulk (one per rail) — spec reserved only
   C291-C299 but intent lists two bulk parts.

## Tank models

`sim/tank-driver-recovery-sim/tanks.lib` models what the electronics see:
input coil L+R load, band-limited coupling (~80 Hz-4 kHz) with realistic
insertion loss, output coil source impedance. Spring delay/reverb tail is
intentionally NOT modeled — that is what the real tanks are for.

## How to run the simulation in KiCad

1. Open `hardware/kicad/sim/tank-driver-recovery-sim/tank-driver-recovery-sim.kicad_pro`
2. Inspect -> Simulator -> Run (the `.tran 20u 60m` directive is on the sheet)
3. Probe `PRI_OUT_L`, `PRI_RET_L`, `SEC_RET_L`, etc. For frequency response,
   comment `.tran` and uncomment `.ac dec 50 10 100k` on the sheet text.

## Still to do (after review sign-off)

- Route the board (power first, then signals), refill zones, DRC to zero
  including connectivity, then Gerber/drill/BOM/position exports
- Replicate this workflow for the other five boards
- Order: fab/assembly quote packet per `hardware/rev-a-manufacturing.md`
