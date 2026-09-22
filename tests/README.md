# Circuit model tests

Offline harness for the clipping and dynamics circuits in `Source/DSP`. It is
deliberately **not** part of the plugin build, so it never slows CI down.

What it checks:

- every clipper curve is finite and monotonic across +/-12 V (a clipper that
  folds back on itself is a bug, not a feature)
- all nine circuits land within a narrow output-RMS window for the same input,
  so switching circuits changes character without changing volume
- the DC blocker is enabled on exactly the asymmetric circuits
- each dynamics circuit reduces more as you feed it more, and its release time
  matches the hardware it models

Run it:

```
cmake -S tests -B tests/build -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DJUCE_SOURCE_DIR=/path/to/JUCE
cmake --build tests/build
./tests/build/GasCircuitTest_artefacts/Release/GasCircuitTest
```

`models/clipper_models.py` is the Python reference for the same equations.
