// Standalone check of the ladder limiter curves, compiled straight against
// ClipperCircuitModels.h so it validates the shipped code rather than a model
// of it. Build with -I stub, which supplies a minimal JuceHeader.h.
//
//   cl /nologo /EHsc /O2 /std:c++17 /I stub LadderCheck.cpp
//
#include <cstdio>
#include <cmath>
#include <algorithm>
#include <utility>

#include "../Source/DSP/ClipperCircuitModels.h"

using namespace gas::circuits;

int main()
{
    const CircuitSpec sym  { Topology::shunt, 10.0e3f, 0.0f, 20.0f,
                             kDiodeRedLed, 1, kDiodeRedLed, 1,
                             kDiode1N4148, 5, kDiode1N4148, 5, 1.2e3f, 7.0f };
    const CircuitSpec asym { Topology::shunt, 10.0e3f, 0.0f, 20.0f,
                             kDiodeRedLed, 2, kDiodeRedLed, 1,
                             kDiode1N4148, 2, kDiode1N4148, 3, 1.2e3f, 7.0f };

    int failures = 0;

    std::printf("Ladder limiters, solved from the shipped header\n");
    std::printf("Rs 10k, Rd 1k2 -> slope %.4f (%.1f:1), supply +/-7 V, 20 dB input stage\n\n",
                1.2e3f / 11.2e3f, 11.2e3f / 1.2e3f);

    std::printf("%8s %12s %12s %12s %10s\n", "Vin", "Sym out", "Asym +", "Asym -", "asym dB");
    std::printf("--------------------------------------------------------------\n");
    for (float vin : { 0.05f, 0.1f, 0.25f, 0.5f, 0.75f, 1.0f, 1.5f, 2.0f, 3.0f })
    {
        const auto s = solveCircuit (vin, sym);
        const auto p = solveCircuit (vin, asym);
        const auto n = solveCircuit (-vin, asym);
        std::printf("%8.2f %12.3f %12.3f %12.3f %+10.2f\n",
                    vin, s, p, n, 20.0f * std::log10 (p / std::fabs (n)));
    }

    // Knee = where the curve departs 1 dB from its small-signal slope.
    auto knee = [&] (const CircuitSpec& spec, float sign)
    {
        const auto slope0 = solveCircuit (sign * 0.002f, spec) / (sign * 0.002f);
        for (int i = 1; i < 6000; ++i)
        {
            const auto v = i * 0.002f;
            const auto out = std::fabs (solveCircuit (sign * v, spec));
            if (20.0f * std::log10 (out / (slope0 * v)) < -1.0f)
                return std::make_pair (v, out);
        }
        return std::make_pair (0.0f, 0.0f);
    };

    struct { const char* name; const CircuitSpec* spec; float sign; float target; } checks[] = {
        { "Sym  +/-",  &sym,  +1.0f, 3.75f },
        { "Asym +",    &asym, +1.0f, 4.00f },
        { "Asym -",    &asym, -1.0f, 3.00f },
    };

    std::printf("\n%-10s %10s %10s %10s   %s\n", "half", "knee V", "target", "error", "verdict");
    std::printf("--------------------------------------------------------------\n");
    for (auto& c : checks)
    {
        const auto [vin, out] = knee (*c.spec, c.sign);
        const auto err = out - c.target;
        const bool ok = std::fabs (err) <= 0.30f;
        if (! ok) ++failures;
        std::printf("%-10s %10.3f %10.2f %+10.3f   %s\n", c.name, out, c.target, err, ok ? "ok" : "OFF TARGET");
    }

    // Smoothness: a limiter must keep rising past the knee, never flatten, and
    // never fold back. Compare against the old hard-clamp behaviour.
    std::printf("\nsmoothness check (output must keep rising, monotonic)\n");
    for (auto& c : checks)
    {
        float prev = -1e9f;
        bool monotonic = true, rising = false;
        for (float v = 0.0f; v <= 3.0f; v += 0.002f)
        {
            const auto out = std::fabs (solveCircuit (c.sign * v, *c.spec));
            if (out < prev - 1e-4f) { monotonic = false; break; }
            prev = out;
        }
        const auto a = std::fabs (solveCircuit (c.sign * 1.0f, *c.spec));
        const auto b = std::fabs (solveCircuit (c.sign * 2.0f, *c.spec));
        rising = (b - a) > 0.15f;   // still climbing well past the knee
        if (! monotonic || ! rising) ++failures;
        std::printf("  %-10s monotonic %-5s   1V->2V climbs %.3f V  %s\n",
                    c.name, monotonic ? "yes" : "NO", b - a,
                    (monotonic && rising) ? "ok" : "FAIL");
    }

    std::printf("\n%s (%d failures)\n", failures == 0 ? "ALL CHECKS PASSED" : "CHECKS FAILED", failures);
    return failures == 0 ? 0 : 1;
}
