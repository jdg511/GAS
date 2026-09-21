#pragma once

#include <JuceHeader.h>

#include <array>
#include <cmath>
#include <mutex>

/**
    Component-level models of the clipping circuits offered by the plugin.

    Every curve here is solved from the Shockley diode equation against the real
    component values of the circuit it represents, rather than being an ad-hoc
    "sounds about right" waveshaper:

        I_d(V) = Is * (exp(V / (N * n * Vt)) - 1)

    The implicit node equation is solved once per table entry by bisection when
    the plugin first loads, baked into a warped lookup table, and then read with
    linear interpolation on the audio thread. The curves do not depend on sample
    rate, so the tables are built exactly once and shared by every instance.

    Reference levels (changed 2026-09-12): each circuit declares how many volts
    a digital full-scale sample represents at its input and output
    (CircuitSpec::inputVoltsPerFullScale / outputVoltsPerFullScale). The
    Tube Screamer stage is a guitar-level circuit, so it sees 0 dBFS as 100 mV
    (a hot pickup) and puts out real volts (1 V == 0 dBFS): its op-amp gain is
    what lifts guitar level to line level, exactly as the pedal does, and the
    Drive knob reads as "how hard into the diodes".
    Supply: 9 V biased to 4.5 V, so the op-amp saturates at +/-4.5 V. That rail
    clamp is part of the model - crank the Drive and you get real op-amp
    saturation on top of the diode clipping, exactly like the hardware.

    The matching Python reference implementation lives in models/clipper_models.py.
*/
namespace gas::circuits
{

inline constexpr float kThermalVoltage = 0.02585f;   // kT/q at 300 K
inline constexpr float kSupplyRail     = 4.5f;       // 9 V rail, biased to 4.5 V

/** Digital full scale at a guitar-level input: a hot passive pickup peaks
    around 100 mV, so 0 dBFS == 0.1 V for the pedal-style circuits. */
inline constexpr float kGuitarLevelVoltsPerFullScale = 0.1f;

/** Digital full scale at a line-level output: 0 dBFS == 1 V. */
inline constexpr float kLineLevelVoltsPerFullScale = 1.0f;


/** One diode type: saturation current and ideality factor. */
struct Diode
{
    float saturationCurrent;   // Is, amperes
    float ideality;            // n
};

// Is / n are chosen so the modelled forward voltage matches the datasheet
// figures quoted alongside each part.
inline constexpr Diode kDiode1N4148    { 2.52e-9f,  1.752f };  // Si, Vf 0.72 V @ 10 mA
inline constexpr Diode kDiodeBAT41     { 1.20e-7f,  1.050f };  // Schottky, Vf 0.45 V @ 10 mA
inline constexpr Diode kDiodeRedLed    { 9.00e-18f, 1.900f };  // GaAsP red LED, Vf 1.85 V @ 20 mA
// Nexperia PMEG150G20ELP, 150 V / 2 A SiGe rectifier, CFP5 (SOD128).
// Is / n fitted to the 25 C curve of datasheet Fig. 3 in the microamp-to-
// milliamp region where a clipper actually works, not to the amp-level table
// entries (those are dominated by ~58 mohm of series resistance, which is
// irrelevant at signal currents). Gives Vf 0.44 V @ 1 mA.
//
// Note n = 1.13 against the 1N4148's 1.75: this part clips EARLIER than silicon
// but with a considerably HARDER knee. It is not a germanium substitute - real
// Ge is soft-kneed and leaky, while this is sharp and specified at 0.4 nA
// reverse leakage.
inline constexpr Diode kDiodePMEG150G20 { 2.863e-10f, 1.134f };
inline constexpr Diode k2N3904BaseEmit { 6.73e-15f, 1.000f };  // 2N3904 B-E junction, n ~ 1.0

enum class Topology
{
    /** Diodes across the op-amp feedback resistor (Tube Screamer / SD-1 / OCD).
        Output keeps climbing with unity slope past the knee, so it never fully
        squares off - this is what keeps these circuits touch sensitive. */
    feedback,

    /** Series resistor into a shunt diode stack (ladder clippers).

        With legResistance = 0 this is a hard clamp to the stack's forward
        voltage. Adding resistance in series with the diodes turns it into a
        soft limiter instead: once the stack conducts, the output keeps rising
        on a divider slope of Rd / (Rd + Rs), which is the compression ratio. */
    shunt
};

/** A complete clipping circuit: topology, resistors, and the diode network.

    Each half of the anti-parallel network can stack two different diode types
    in series (primary x count, then secondary x count2). Mixing a couple of
    LEDs with a silicon diode is how the ladders reach a high threshold while
    keeping a soft knee, and it is exactly how you would build it on a board.
    Mixed stacks are supported on the shunt topology only. */
struct CircuitSpec
{
    Topology topology;
    float    seriesOrFeedbackR;   // Rf (feedback) or Rs (shunt), ohms
    float    gainSetR;            // Rg for the feedback topology, ohms
    float    inputStageGainDb;    // gain of the stage ahead of a shunt network

    Diode positiveDiode;
    int   positiveCount;          // diodes in series on the positive half
    Diode negativeDiode;
    int   negativeCount;          // diodes in series on the negative half

    // Optional second diode type stacked in series with the first, per half.
    Diode positiveDiode2 { 1.0e-12f, 1.0f };
    int   positiveCount2 = 0;
    Diode negativeDiode2 { 1.0e-12f, 1.0f };
    int   negativeCount2 = 0;

    // Series resistance inside the shunt leg. Sets the post-knee slope.
    float legResistance = 0.0f;

    // Supply rail for this circuit. The pedal-style clippers run from 9 V
    // biased at 4.5 V; the ladder limiters need a bigger supply, because a
    // threshold near 3.7 V on a 4.5 V rail would hard-clamp almost immediately
    // and there would be no room for the soft limiting to be audible.
    float supplyRail = kSupplyRail;

    // How many volts one digital full-scale sample is at this circuit's input.
    // Set from the topology in FilterClipperBlock::getSpecs(): guitar level for
    // the pedal (feedback) circuits, line level for the ladders.
    float inputVoltsPerFullScale = kLineLevelVoltsPerFullScale;

    // How many volts of circuit OUTPUT map back to one digital full-scale
    // sample. 1 V for the pedal circuits (their output really is louder than
    // their input); equal to the input scale for the ladders so they sit at
    // unity below the knee.
    float outputVoltsPerFullScale = kLineLevelVoltsPerFullScale;

    bool isAsymmetric() const noexcept
    {
        auto sameDiode = [] (const Diode& a, const Diode& b)
        {
            return a.saturationCurrent == b.saturationCurrent && a.ideality == b.ideality;
        };

        return positiveCount != negativeCount
            || positiveCount2 != negativeCount2
            || ! sameDiode (positiveDiode, negativeDiode)
            || (positiveCount2 > 0 && ! sameDiode (positiveDiode2, negativeDiode2));
    }
};

/** Current through `count` identical diodes stacked in series. */
inline float diodeCurrent (float voltage, const Diode& diode, int count) noexcept
{
    const auto scale = static_cast<float> (count) * diode.ideality * kThermalVoltage;
    const auto exponent = juce::jlimit (-80.0f, 80.0f, voltage / scale);
    return diode.saturationCurrent * (std::exp (exponent) - 1.0f);
}

/** Net current through an anti-parallel diode network at a given voltage. */
inline float networkCurrent (float voltage, const CircuitSpec& spec) noexcept
{
    return diodeCurrent (voltage, spec.positiveDiode, spec.positiveCount)
         - diodeCurrent (-voltage, spec.negativeDiode, spec.negativeCount);
}

/** Voltage across a series diode stack carrying a given forward current.

    This is the Shockley equation inverted, which is the natural direction for
    the shunt topology: a series stack shares one current, so summing each
    element's voltage is exact and needs no nested solve, and it handles a
    stack of mixed diode types for free.

        V = N * n * Vt * ln(I / Is + 1)
*/
inline float stackVoltage (float current,
                           const Diode& primary, int primaryCount,
                           const Diode& secondary, int secondaryCount) noexcept
{
    const auto safeCurrent = juce::jmax (0.0f, current);
    auto volts = 0.0f;

    if (primaryCount > 0)
        volts += static_cast<float> (primaryCount) * primary.ideality * kThermalVoltage
               * std::log (safeCurrent / primary.saturationCurrent + 1.0f);

    if (secondaryCount > 0)
        volts += static_cast<float> (secondaryCount) * secondary.ideality * kThermalVoltage
               * std::log (safeCurrent / secondary.saturationCurrent + 1.0f);

    return volts;
}

/** Solves the shunt topology for one input voltage, working in leg current.

        Vin = Vstack(I) + I * (Rd + Rs)      then      Vout = Vstack(I) + I * Rd

    Vstack rises monotonically with I, so the whole expression is monotonic and
    bisection converges without any bracketing games. With Rd = 0 the result is
    the old hard clamp; with Rd > 0 the output keeps climbing at Rd / (Rd + Rs)
    once the stack conducts, which is the limiter slope.
*/
inline float solveShunt (float driven, const CircuitSpec& spec) noexcept
{
    const auto magnitude = std::abs (driven);
    const auto sign = driven < 0.0f ? -1.0f : 1.0f;

    const auto& primary       = driven < 0.0f ? spec.negativeDiode  : spec.positiveDiode;
    const auto  primaryCount  = driven < 0.0f ? spec.negativeCount  : spec.positiveCount;
    const auto& secondary     = driven < 0.0f ? spec.negativeDiode2 : spec.positiveDiode2;
    const auto  secondaryCount = driven < 0.0f ? spec.negativeCount2 : spec.positiveCount2;

    const auto totalR = spec.legResistance + spec.seriesOrFeedbackR;

    // I can never exceed the value it would reach with the stack shorted.
    auto low = 0.0f;
    auto high = magnitude / juce::jmax (1.0f, totalR);

    for (int iteration = 0; iteration < 64; ++iteration)
    {
        const auto mid = 0.5f * (low + high);
        const auto trial = stackVoltage (mid, primary, primaryCount, secondary, secondaryCount)
                         + mid * totalR;

        if (trial > magnitude)
            high = mid;
        else
            low = mid;
    }

    const auto current = 0.5f * (low + high);
    const auto output = stackVoltage (current, primary, primaryCount, secondary, secondaryCount)
                      + current * spec.legResistance;

    return juce::jlimit (-spec.supplyRail, spec.supplyRail, sign * output);
}

/** Solves the circuit's node equation for one input voltage.

    feedback:  Vin/Rg = Vd/Rf + I_diodes(Vd),  Vout = Vin + Vd
    shunt:     see solveShunt above

    Bisection rather than Newton: it cannot diverge on the stiff exponential,
    and this only ever runs at load time.
*/
inline float solveCircuit (float inputVolts, const CircuitSpec& spec) noexcept
{
    const auto driven = inputVolts * juce::Decibels::decibelsToGain (spec.inputStageGainDb);

    if (spec.topology == Topology::shunt)
        return solveShunt (driven, spec);

    auto residual = [&] (float unknown)
    {
        return driven / spec.gainSetR - (unknown / spec.seriesOrFeedbackR + networkCurrent (unknown, spec));
    };

    auto low  = -2.0f * spec.supplyRail;
    auto high =  2.0f * spec.supplyRail;

    // Widen the bracket if the solution sits outside it (only possible before
    // the rail clamp bites, and cheap to guard against).
    for (int attempt = 0; attempt < 8 && residual (low) * residual (high) > 0.0f; ++attempt)
    {
        low  *= 2.0f;
        high *= 2.0f;
    }

    if (residual (low) * residual (high) > 0.0f)
        return juce::jlimit (-spec.supplyRail, spec.supplyRail, driven);

    for (int iteration = 0; iteration < 64; ++iteration)
    {
        const auto mid = 0.5f * (low + high);

        if (residual (low) * residual (mid) <= 0.0f)
            high = mid;
        else
            low = mid;
    }

    const auto solved = 0.5f * (low + high);
    const auto output = (spec.topology == Topology::feedback) ? driven + solved : solved;

    return juce::jlimit (-spec.supplyRail, spec.supplyRail, output);
}

//==============================================================================
/** A solved circuit baked into a lookup table.

    The table is indexed through a warp, u = v / (kWarp + |v|), which concentrates
    resolution around zero where the knee lives while still reaching the tens of
    volts a fully cranked Drive can produce.
*/
class CircuitCurve
{
public:
    static constexpr int   kTableSize = 4096;
    static constexpr float kWarp      = 0.5f;

    void build (const CircuitSpec& spec)
    {
        asymmetric = spec.isAsymmetric();
        inputVoltsPerFullScale = spec.inputVoltsPerFullScale;
        outputGain = 1.0f / juce::jmax (1.0e-6f, spec.outputVoltsPerFullScale);

        for (int index = 0; index < kTableSize; ++index)
        {
            const auto u = juce::jmap (static_cast<float> (index),
                                       0.0f, static_cast<float> (kTableSize - 1),
                                       -kMaxWarped, kMaxWarped);
            table[static_cast<size_t> (index)] = solveCircuit (unwarp (u), spec);
        }
    }

    /** x is a digital sample; it is converted to volts at this circuit's input
        level, run through the solved circuit, and the result is converted back
        to digital at the circuit's output level. */
    float process (float x) const noexcept
    {
        const auto u = warp (x * inputVoltsPerFullScale);
        const auto position = juce::jmap (juce::jlimit (-kMaxWarped, kMaxWarped, u),
                                          -kMaxWarped, kMaxWarped,
                                          0.0f, static_cast<float> (kTableSize - 1));
        const auto lowIndex = static_cast<int> (position);
        const auto highIndex = juce::jmin (lowIndex + 1, kTableSize - 1);
        const auto fraction = position - static_cast<float> (lowIndex);

        const auto a = table[static_cast<size_t> (lowIndex)];
        const auto b = table[static_cast<size_t> (highIndex)];

        // No hidden makeup gain: the curve is the circuit's real output voltage,
        // converted back at the declared output reference level. Pedal circuits
        // (1 V/FS out) come out as loud as the hardware does; the ladders use a
        // matching in/out scale so they are unity below the knee.
        return (a + fraction * (b - a)) * outputGain;
    }

    bool needsDcBlocker() const noexcept { return asymmetric; }

private:
    static constexpr float kMaxWarped = 0.995f;

    static float warp (float v) noexcept   { return v / (kWarp + std::abs (v)); }
    static float unwarp (float u) noexcept { return kWarp * u / juce::jmax (1.0e-6f, 1.0f - std::abs (u)); }

    std::array<float, kTableSize> table {};
    bool  asymmetric = false;
    float inputVoltsPerFullScale = kLineLevelVoltsPerFullScale;
    float outputGain = 1.0f;
};

} // namespace gas::circuits
