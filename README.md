# The Great American Spring

JUCE 7 audio effect by Illicit Apothecary.

Release v2.5 defines the GAS fork from the former Stereo Crossfeed Convolver project. It packages only the four final spring tank IR files:

- `GBS-L.wav`
- `GBS-R.wav`
- `GAS-L.wav`
- `GAS-R.wav`

The plugin provides Main Tanks, optional Ext Reverb Tanks in series or parallel, a constant-sum stereo crossfade, FilterClipper, feedback phase control, mono source handling, and wet/dry output mixing.

## Hardware Mapping Notes

For the real device, the simulation's `predelay + convolution IR` stage should be treated as the software stand-in for a physical spring reverb tank.

- Primary tank simulation: both channels represent `4AB1C1B` tanks.
- Secondary tank simulation: left channel represents a `9EB2C1B` tank and right channel represents a `9EB3C1B` tank.

This means the current JUCE simulation is not just a generic convolution reverb. Its timing and IR choices are standing in for the mechanical behavior of the spring tanks we intend to use in hardware.
Only the predelay and convolution portions are simulation-only. They exist to emulate the behavior of the real spring tanks; the rest of the signal path should be treated as candidate hardware behavior unless we explicitly decide otherwise later.

## Hardware Platform Constraints

The real-world unit should be designed as primarily analog hardware:

- Use passive components, solid-state transistors, and analog / mixed-signal ICs as the main building blocks.
- Do not base the PCB design on an MCU, Arduino, Raspberry Pi, or other general-purpose embedded computer.
- The production hardware should replace the simulation-only predelay and convolution stages with real spring tanks and supporting analog electronics, not runtime convolution or software processing on the PCB.
