# GAS Rev A Numeric Targets

This file gathers the hard numeric targets that are already implicit across the hardware package.

## External Audio Targets

### Balanced Input

- interface type: balanced line input
- nominal operating level: `+4 dBu`
- professional 600-ohm capable interfacing

### Balanced Output

- interface type: balanced line output
- nominal operating level: `+4 dBu`
- professional 600-ohm capable interfacing

## Rail Targets

- normal target rails:
  - `+15VA`
  - `-15VA`
- auxiliary rail:
  - `+5VAUX`
- preferred device tolerance where practical:
  - `+18V / -18V`

## Internal Headroom Target

The rev-A architecture currently targets:

- at least `+20 dBu` internal analog headroom where reasonable on `+/-15V` rails

This is the design intent currently called out for the I/O board and should be preserved through the rest of the signal path unless a stage forces a lower working margin.

## Power Budget Snapshot

From the current first-pass budget:

- analog split rails:
  - about `114 mA` to `154 mA` estimated static draw before final signal-drive margins
- `+5V` auxiliary:
  - reserve around `100 mA` for relay/control use as a safe early allowance

See:

- [rev-a-power-budget.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-power-budget.md:1)

## Values That Are Still Intentionally Not Frozen

- primary tank send amplitude target
- exact primary class-AB idle current
- exact recovery gain
- exact filter frequencies and Q ranges after listening tests

Those remain prototype-tuning items rather than fake-final numbers.
