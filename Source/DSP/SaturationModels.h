#pragma once

#include <JuceHeader.h>

#include <array>
#include <cmath>

/**
    Tube and Tape emulation built from real, buildable pedal-grade circuits:
    op-amps, JFETs, BJTs, resistors and capacitors. No abstract curves. Every
    constant below is a part value you can order, and the models are solved
    from the device equations the same way the diode clippers are.

    Both run per sample at the oversampled rate inside FilterClipperBlock.
    Level reference is the same as the pedal clippers: digital 1.0 == 100 mV
    at the circuit input (a hot guitar pickup). The output is normalised so the
    stage is unity gain below its knee, which is the same as having a volume
    pot after the circuit set for unity clean. There is no hidden make-up gain.
*/
namespace gas::saturation
{

inline constexpr float kGuitarVoltsPerFullScale = 0.1f;

//==============================================================================
/** First-order analogue transfer function H(s) = (b1 s + b0) / (a1 s + a0),
    mapped to the digital rate with the bilinear transform. Used for the RC
    shelving networks in the tape path so they are derived from the actual
    resistor and capacitor values. */
class FirstOrderAnalogue
{
public:
    void prepare (double sampleRate, double b1, double b0, double a1, double a0)
    {
        const auto k  = 2.0 * sampleRate;
        const auto d0 = a1 * k + a0;

        c0 = static_cast<float> ((b1 * k + b0) / d0);
        c1 = static_cast<float> ((b0 - b1 * k) / d0);
        d1 = static_cast<float> ((a0 - a1 * k) / d0);
        reset();
    }

    void reset() noexcept { x1 = 0.0f; y1 = 0.0f; }

    float process (float x) noexcept
    {
        const auto y = c0 * x + c1 * x1 - d1 * y1;
        x1 = x;
        y1 = y;
        return y;
    }

    /** Gain at DC, used to normalise the stage. */
    float dcGain() const noexcept { return (c0 + c1) / (1.0f + d1); }

private:
    float c0 = 1.0f, c1 = 0.0f, d1 = 0.0f;
    float x1 = 0.0f, y1 = 0.0f;
};

/** A 9 V single-rail op-amp output can swing about +-3.3 V around its
    mid-point before it hits the rails. */
inline float opAmpRails (float volts) noexcept
{
    return juce::jlimit (-3.3f, 3.3f, volts);
}

//==============================================================================
/** TUBE: a single J201 JFET common-source stage, the "Fetzer Valve" idea.

    Circuit (9 V):
        TL072 non-inverting boost, Rf 100k / Rg 10k             (x11)
        -> Cin 47 nF -> gate, Rg 1M to ground
        J201: Rd = 4.7k + 50k trimmer to +9 V, TRIMMED FOR Vd = 4.9 V
              (Rev B / Rev C board: R + RV in the drain; the model solves the
              drain resistance the trim lands on, so it tracks the J201's
              Idss spread the same way the trimmer does)
              Rs 470R to ground, bypassed by Cs 10 uF
        Output taken at the drain through a coupling cap.

    Why it sounds like a tube:
      - A JFET follows the same square-law as a triode: Id = Idss (1 - Vgs/Vp)^2.
        Gain rises on the positive half of the swing and falls toward cutoff on
        the negative half, so the two halves are squashed differently. That
        asymmetry is where the even harmonics come from.
      - The positive half eventually runs the drain down into the JFET's ohmic
        region (like a triode running out of plate swing), the negative half
        eases into cutoff. Firm one way, soft the other, exactly like a triode.
      - The gate-source junction is a real diode. Drive the gate past about
        +0.6 V and it conducts, charging Cin. That charge pushes the bias
        negative for as long as the overdrive lasts and bleeds off through the
        1M gate resistor (tau = 47 ms). This is the same mechanism as grid
        current in a tube and gives the sag / bloom on sustained notes.

    The drain load line is solved once into a table (Shichman-Hodges model,
    saturation and ohmic regions), then looked up per sample.
*/
class JfetTubeStage
{
public:
    void prepare (double sampleRate)
    {
        capDecay = static_cast<float> (std::exp (-1.0 / (sampleRate * kGateResistor * kCouplingCap)));
        buildTable();
        reset();
    }

    void reset() noexcept
    {
        capVolts = 0.0f;
    }

    float process (float input) noexcept
    {
        // Op-amp boost, limited by its rails.
        const auto boosted = opAmpRails (input * kGuitarVoltsPerFullScale * kBoostGain);

        // Gate voltage: the coupling cap's stored charge sits between the
        // op-amp and the gate. Gate DC is 0 V (Rg to ground), source sits at VsQ.
        auto vgs = (boosted - capVolts) - vsQ;

        // Gate-source diode: anything past ~0.6 V is dumped onto the cap.
        if (vgs > kGateDiodeOn)
        {
            capVolts += (vgs - kGateDiodeOn);
            vgs = kGateDiodeOn;
        }

        // Cap discharges through the 1M gate resistor.
        capVolts *= capDecay;

        const auto vd = lookupDrain (vgs);

        // The stage inverts; flip back so polarity matches the other modes.
        return -(vd - vdQ) / outputVoltsPerFullScale;
    }

private:
    // Part values
    static constexpr float kVdd         = 9.0f;
    static constexpr float kIdss        = 1.0e-3f;   // J201 typical
    static constexpr float kVp          = -0.8f;     // J201 pinch-off, typical
    static constexpr float kDrainTargetVolts = 4.9f;   // what the trimmer is set for
    static constexpr float kRdMin       = 4700.0f;     // fixed 4.7k with the trimmer at zero
    static constexpr float kRdMax       = 54700.0f;    // 4.7k + 50k trimmer
    static constexpr float kRs          = 470.0f;
    static constexpr double kGateResistor = 1.0e6;
    static constexpr double kCouplingCap  = 47.0e-9;
    static constexpr float kBoostGain   = 11.0f;     // 1 + 100k / 10k
    static constexpr float kGateDiodeOn = 0.6f;
    static constexpr float kVdsMinOhmic = 0.0f;

    static constexpr int   kTableSize = 1024;
    static constexpr float kTableMin  = -1.2f;       // Vgs range covered by the table
    static constexpr float kTableMax  =  0.7f;

    static float drainCurrent (float vgs, float vds) noexcept
    {
        if (vgs <= kVp || vds <= kVdsMinOhmic)
            return 0.0f;

        const auto beta = kIdss / (kVp * kVp);
        const auto vov  = vgs - kVp;

        if (vds >= vov)
            return beta * vov * vov;                          // saturation region

        return beta * (2.0f * vov * vds - vds * vds);         // ohmic region
    }

    // Drain voltage that satisfies the load line Vd = Vdd - Id * Rd for a given Vgs.
    float solveDrain (float vgs) const noexcept
    {
        auto lo = vsQ, hi = kVdd;

        for (int i = 0; i < 48; ++i)
        {
            const auto mid = 0.5f * (lo + hi);
            const auto f   = kVdd - mid - rd * drainCurrent (vgs, mid - vsQ);
            if (f > 0.0f) lo = mid; else hi = mid;
        }

        return 0.5f * (lo + hi);
    }

    void buildTable()
    {
        // Quiescent point: gate at 0 V, so Vgs = -Id * Rs. Solve for Vs.
        {
            auto lo = 0.0f, hi = -kVp;
            for (int i = 0; i < 48; ++i)
            {
                const auto mid = 0.5f * (lo + hi);
                const auto f   = kIdss * juce::square (1.0f - (-mid) / kVp) * kRs - mid;
                if (f > 0.0f) lo = mid; else hi = mid;
            }
            vsQ = 0.5f * (lo + hi);
        }

        // Drain trimmer: set so the quiescent drain sits at 4.9 V, mid-swing
        // for the 9 V rail, whatever this particular J201's Idss is.
        {
            const auto idQ = juce::jmax (1.0e-6f, kIdss * juce::square (1.0f - (-vsQ) / kVp));
            rd = juce::jlimit (kRdMin, kRdMax, (kVdd - kDrainTargetVolts) / idQ);
        }

        vdQ = solveDrain (-vsQ);

        for (int i = 0; i < kTableSize; ++i)
        {
            const auto vgs = kTableMin + (kTableMax - kTableMin) * static_cast<float> (i) / static_cast<float> (kTableSize - 1);
            table[static_cast<size_t> (i)] = solveDrain (vgs);
        }

        // Small-signal gain at the bias point sets the unity normalisation.
        const auto delta = 0.002f;
        const auto slope = (solveDrain (-vsQ + delta) - solveDrain (-vsQ - delta)) / (2.0f * delta);
        outputVoltsPerFullScale = juce::jmax (1.0e-3f, std::abs (slope) * kBoostGain * kGuitarVoltsPerFullScale);
    }

    float lookupDrain (float vgs) const noexcept
    {
        const auto pos = juce::jlimit (0.0f, static_cast<float> (kTableSize - 1),
                                       (vgs - kTableMin) / (kTableMax - kTableMin) * static_cast<float> (kTableSize - 1));
        const auto i0 = static_cast<size_t> (pos);
        const auto i1 = juce::jmin (i0 + 1, static_cast<size_t> (kTableSize - 1));
        const auto frac = pos - static_cast<float> (i0);
        return table[i0] + (table[i1] - table[i0]) * frac;
    }

    std::array<float, kTableSize> table {};
    float rd = 8200.0f;
    float vsQ = 0.0f;
    float vdQ = 0.0f;
    float outputVoltsPerFullScale = 1.0f;
    float capDecay = 0.0f;
    float capVolts = 0.0f;
};

//==============================================================================
/** TAPE: op-amp record EQ into a BJT differential-pair limiter, passive repro EQ.

    Circuit (9 V, mid-rail bias):
        Record EQ   TL072 non-inverting. Rf 82k. Gain leg: Rg1 10k to ground,
                    in parallel with Rs 4.7k + C 6.8 nF. Gain x9.2 at LF rising
                    to x26.6 above ~3 kHz (+9 dB high shelf, 1.6 kHz / 5 kHz).
        Limiter     Q1, Q2 2N3904 long-tailed pair. Bases biased at ~3 V
                    (47k / 22k divider), Re 470R in each emitter, shared tail
                    Rt 2.2k to ground (about 1.07 mA), Rc 4.7k on each collector.
                    Signal AC-coupled into Q1 base, Q2 base held at bias.
                    Output from Q2 collector.
        Repro EQ    R1 15k series (the 4.7k collector resistor adds to it),
                    then R2 10k + C 3.3 nF to ground. Mirror image of the record
                    shelf: unity at LF, 1/2.9 above ~3 kHz.

    Why it sounds like tape:
      - A differential pair's transfer curve is tanh(). That is the textbook
        tape magnetisation curve: dead straight in the middle, then a smooth,
        symmetric ease into saturation. Symmetric means odd harmonics (3rd, 5th),
        which is the tape flavour rather than the tube one. The emitter
        resistors widen the linear region so the knee lands at guitar levels.
      - Record pre-emphasis boosts the highs going in, repro de-emphasis takes
        them back out. Clean signal comes out flat, but a hot signal saturates
        on its treble first and then has that treble rounded off. That is why
        tape "softens" rather than "fizzes".

    Left out on purpose to keep the part count down: the repro head bump
    (needs a gyrator, one more op-amp) and hysteresis.
*/
class TapeDiffPairStage
{
public:
    void prepare (double sampleRate)
    {
        // Record EQ: G(s) = 1 + Rf / Zg,  Zg = Rg1 || (Rs + 1/sC)
        //  => [ sC (Rg1 Rs + Rf (Rg1 + Rs)) + (Rg1 + Rf) ] / [ sC Rg1 Rs + Rg1 ]
        recordEq.prepare (sampleRate,
                          kRecC * (kRg1 * kRsh + kRf * (kRg1 + kRsh)),
                          kRg1 + kRf,
                          kRecC * kRg1 * kRsh,
                          kRg1);

        // Repro EQ: passive divider H(s) = (s R2 C + 1) / (s (R1 + Rc + R2) C + 1)
        reproEq.prepare (sampleRate,
                         kR2 * kRepC,
                         1.0,
                         (kR1 + kRc + kR2) * kRepC,
                         1.0);

        buildTable();

        // Unity below the knee: LF record gain x pair small-signal gain x repro LF gain (1).
        const auto pairGain = (kTail * kRc) / (2.0f * (2.0f * kVt + kTail * kRe));
        outputVoltsPerFullScale = recordEq.dcGain() * pairGain * kGuitarVoltsPerFullScale;

        reset();
    }

    void reset() noexcept
    {
        recordEq.reset();
        reproEq.reset();
    }

    float process (float input) noexcept
    {
        const auto recorded = opAmpRails (recordEq.process (input * kGuitarVoltsPerFullScale));
        const auto collector = lookupCollector (recorded);
        const auto repro = reproEq.process (collector);
        return repro / outputVoltsPerFullScale;
    }

private:
    // Record EQ parts
    static constexpr double kRf   = 82.0e3;
    static constexpr double kRg1  = 10.0e3;
    static constexpr double kRsh  = 4.7e3;
    static constexpr double kRecC = 6.8e-9;
    // Differential pair
    static constexpr float kVt   = 0.02585f;   // kT/q at room temperature
    static constexpr float kTail = 1.07e-3f;   // (3 V - 0.65 V) / 2.2k
    static constexpr float kRe   = 470.0f;
    static constexpr float kRc   = 4700.0f;
    // Repro EQ parts
    static constexpr double kR1   = 15.0e3;
    static constexpr double kR2   = 10.0e3;
    static constexpr double kRepC = 3.3e-9;

    static constexpr int   kTableSize = 2048;
    static constexpr float kTableMax  = 4.0f;    // +- volts of differential drive covered

    // Solve the pair for a given differential input: vd = 2 Vt atanh(x) + Itail Re x,
    // where x = (Ic1 - Ic2) / Itail in (-1, 1). Output is the AC collector swing.
    static float solveCollector (float vd) noexcept
    {
        auto lo = -0.999999f, hi = 0.999999f;

        for (int i = 0; i < 48; ++i)
        {
            const auto x = 0.5f * (lo + hi);
            const auto f = 2.0f * kVt * std::atanh (x) + kTail * kRe * x - vd;
            if (f < 0.0f) lo = x; else hi = x;
        }

        return 0.5f * (lo + hi) * (0.5f * kTail * kRc);
    }

    void buildTable()
    {
        for (int i = 0; i < kTableSize; ++i)
        {
            const auto vd = -kTableMax + 2.0f * kTableMax * static_cast<float> (i) / static_cast<float> (kTableSize - 1);
            table[static_cast<size_t> (i)] = solveCollector (vd);
        }
    }

    float lookupCollector (float vd) const noexcept
    {
        const auto pos = juce::jlimit (0.0f, static_cast<float> (kTableSize - 1),
                                       (vd + kTableMax) / (2.0f * kTableMax) * static_cast<float> (kTableSize - 1));
        const auto i0 = static_cast<size_t> (pos);
        const auto i1 = juce::jmin (i0 + 1, static_cast<size_t> (kTableSize - 1));
        const auto frac = pos - static_cast<float> (i0);
        return table[i0] + (table[i1] - table[i0]) * frac;
    }

    FirstOrderAnalogue recordEq;
    FirstOrderAnalogue reproEq;
    std::array<float, kTableSize> table {};
    float outputVoltsPerFullScale = 1.0f;
};

} // namespace gas::saturation
