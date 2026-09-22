#include <JuceHeader.h>
#include "ClipperCircuitModels.h"
#include "DynamicsModels.h"
#include <cstdio>

using namespace gas::circuits;

static const std::array<CircuitSpec, 9> kSpecs
{ {
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, kDiode1N4148,    1, kDiode1N4148,    1 },
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, kDiode1N4148,    2, kDiode1N4148,    1 },
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, kDiodeBAT41,     1, kDiodeBAT41,     1 },
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, kDiodeRedLed,    1, kDiodeRedLed,    1 },
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, kDiodeRedLed,    1, kDiode1N4148,    1 },
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, kDiodePMEG150G20, 2, kDiodePMEG150G20, 1 },
    { Topology::feedback, 51.0e3f, 4.7e3f,  0.0f, k2N3904BaseEmit, 1, k2N3904BaseEmit, 1 },
    { Topology::shunt,    10.0e3f, 0.0f,   26.0f, kDiode1N4148,    3, kDiode1N4148,    3 },
    { Topology::shunt,    10.0e3f, 0.0f,   26.0f, kDiode1N4148,    3, kDiode1N4148,    2 },
} };

static const char* kNames[9] = { "Silicon Sym","Silicon Asym","Schottky Sym","LED Sym",
                                 "LED/Si Asym","SiGe Asym","Transistor B-E","Ladder Sym","Ladder Asym" };

int main()
{
    int failures = 0;
    std::array<CircuitCurve, 9> curves;

    const auto t0 = juce::Time::getMillisecondCounterHiRes();
    for (size_t i = 0; i < curves.size(); ++i)
        curves[i].build (kSpecs[i]);
    const auto buildMs = juce::Time::getMillisecondCounterHiRes() - t0;

    std::printf ("Built 9 circuit tables in %.1f ms (once per process, off the audio thread)\n\n", buildMs);
    std::printf ("%-16s %9s %9s %9s %9s %8s %7s\n",
                 "circuit", "out@0.1", "out@0.5", "out@2.0", "out@8.0", "asym dB", "DC blk");
    std::printf ("--------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < curves.size(); ++i)
    {
        const auto o01 = curves[i].process (0.1f);
        const auto o05 = curves[i].process (0.5f);
        const auto o20 = curves[i].process (2.0f);
        const auto o80 = curves[i].process (8.0f);
        const auto asymDb = juce::Decibels::gainToDecibels (std::abs (o20) / juce::jmax (1.0e-6f, std::abs (curves[i].process (-2.0f))));

        std::printf ("%-16s %9.4f %9.4f %9.4f %9.4f %8.2f %7s\n",
                     kNames[i], o01, o05, o20, o80, asymDb,
                     curves[i].needsDcBlocker() ? "yes" : "no");

        // Monotonicity: a clipper must never fold back on itself.
        float previous = -1.0e9f;
        for (float v = -12.0f; v <= 12.0f; v += 0.002f)
        {
            const auto out = curves[i].process (v);

            if (! std::isfinite (out)) { std::printf ("  !! non-finite at %.3f\n", v); ++failures; break; }
            if (out < previous - 1.0e-4f) { std::printf ("  !! non-monotonic at %.3f\n", v); ++failures; break; }
            previous = out;
        }

        // Level matching: every circuit should land near the same output RMS
        // for the same input, so switching circuits is not a volume jump.
        double sum = 0.0;
        constexpr int n = 4096;
        for (int k = 0; k < n; ++k)
        {
            const auto x = 0.5f * std::sin (juce::MathConstants<float>::twoPi * (float) k / (float) n);
            const auto y = curves[i].process (x);
            sum += (double) y * (double) y;
        }
        const auto rms = std::sqrt (sum / n);
        if (rms < 0.20 || rms > 0.45) { std::printf ("  !! level match out of range: rms %.3f\n", rms); ++failures; }
    }

    // ── dynamics ────────────────────────────────────────────────────────────
    std::printf ("\n%-14s %12s %12s %12s\n", "circuit", "GR @ -6dBFS", "GR @ 0dBFS", "release ms");
    std::printf ("--------------------------------------------------------\n");

    const double sr = 192000.0;   // the block runs these at 4x oversampled rate

    auto measure = [&] (auto& unit, const char* name)
    {
        unit.prepare (sr);

        auto steadyGrDb = [&] (float peak)
        {
            unit.reset();
            float maxOut = 0.0f;
            const int total = (int) (sr * 1.5);          // let the slow tail settle
            for (int i = 0; i < total; ++i)
            {
                const auto x = peak * std::sin (juce::MathConstants<float>::twoPi * 220.0f * (float) i / (float) sr);
                const auto y = unit.process (x);
                if (i > total - 4096) maxOut = juce::jmax (maxOut, std::abs (y));
            }
            return juce::Decibels::gainToDecibels (peak / juce::jmax (1.0e-6f, maxOut));
        };

        const auto gr6 = steadyGrDb (0.5f);
        const auto gr0 = steadyGrDb (1.0f);

        // Release: drive it hard, then measure recovery to within 1 dB of unity.
        unit.reset();
        for (int i = 0; i < (int) (sr * 0.5); ++i)
            unit.process (1.0f * std::sin (juce::MathConstants<float>::twoPi * 220.0f * (float) i / (float) sr));

        int samples = 0;
        const int limit = (int) (sr * 6.0);
        for (; samples < limit; ++samples)
        {
            const auto y = unit.process (0.05f);
            if (std::abs (y) > 0.05f * 0.89f) break;      // back within ~1 dB
        }
        const auto releaseMs = 1000.0 * samples / sr;

        std::printf ("%-14s %12.2f %12.2f %12.1f\n", name, gr6, gr0, releaseMs);

        if (! (gr0 > gr6)) { std::printf ("  !! more level should give more reduction\n"); ++failures; }
        if (gr0 < 1.0f)    { std::printf ("  !! barely compressing at 0 dBFS\n"); ++failures; }
    };

    // Rev C units are stereo linked; drive both channels with the same signal.
    struct LinkedOpto { gas::dynamics::OptoCompressor u; void prepare (double sr) { u.prepare (sr); } void reset() { u.reset(); }
                        float process (float x) { float l = x, r = x; u.process (l, r); return l; } } opto;
    struct LinkedVca  { gas::dynamics::VcaLimiter u;     void prepare (double sr) { u.prepare (sr); } void reset() { u.reset(); }
                        float process (float x) { float l = x, r = x; u.process (l, r); return l; } } vca;
    measure (opto, "Comp (opto)");
    measure (vca,  "Limit (VCA)");

    std::printf ("\n%s (%d failures)\n", failures == 0 ? "ALL CHECKS PASSED" : "CHECKS FAILED", failures);
    return failures == 0 ? 0 : 1;
}
