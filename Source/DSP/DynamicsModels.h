#pragma once

#include <JuceHeader.h>

#include <cmath>

/**
    Rev C dynamics circuits, modelled from the parts on the Rev B / Rev C
    circuit board rather than from a generic compressor recipe.

    Both units are STEREO LINKED, exactly as the board wires them: one sidechain
    sums L and R and one control signal drives both channels, so the stereo
    image never shifts when one side gets louder.

    Level plan (Rev B circuit-board definition, section 2): on the mode bus
    0 dBFS = 6.93 Vpk, so the fixed -18 dBFS threshold is 0.87 Vpk. Every
    voltage below is a real node voltage on the board; every resistor, cap and
    time constant is a part you can order.

      Comp   VTL5C3 vactrol shunt (LA-2A style), feed-forward linked sidechain
      Limit  THAT2180 VCA + discrete log-average detector (dbx 160 style), feedback
*/
namespace gas::dynamics
{

inline constexpr float kBusVoltsPerFullScale = 6.93f;   // mode bus: 0 dBFS = 6.93 Vpk
inline constexpr float kThresholdDbfs        = -18.0f;  // fixed, as on the hardware
inline constexpr float kThermalVoltage       = 0.02585f;
inline constexpr float kOpAmpRail            = 14.0f;   // +/-15 V op-amps swing about 14 V

/** One-pole coefficient for an RC time constant. */
inline float rcCoefficient (double seconds, double sampleRate) noexcept
{
    return static_cast<float> (std::exp (-1.0 / (sampleRate * juce::jmax (1.0e-6, seconds))));
}

//==============================================================================
/** COMP: Vactrol opto compressor (Rev B refs 11xx).

    Audio    R1101 22k series into the VTL5C3 photocell to AGND (shunt divider),
             buffered by U202D. Dark the cell is > 10 M, so the mode is unity at rest.
    Sidechain (feed-forward, linked)
             U1101B sums L and R (100k / 100k / 47k: -0.47 each)
             U1101C precision half-wave rectifier (10k / 10k, 1N4148W pair)
             R1146 10k + C1141 1u: 10 ms average
             U1101D non-inverting x13 (120k / 10k) drives the two vactrol LEDs
             (3.4 V forward, in series) through the LED resistor.
    Cell law VTL5C3 datasheet: about 1.5 k at 1 mA LED current, falling roughly as
             I^-0.7 (300 R at 10 mA). Turn-on ~2.5 ms. Turn-off is the dual slope:
             a fast ~35 ms decay carrying most of the change and a long
             photoconductor memory tail (seconds), which is where the LA-2A
             "breathing" release comes from.

    Depth and headroom (Rev C change to the sidechain driver): Rev B used a x13
    driver with the two LED forward drops as the only threshold and R1150 2.2k +
    RV1101 10k as the LED resistor. Solving the cell law against the design target
    (7 dB of gain reduction at +12 dB over threshold) shows two problems: 12k
    would run the LEDs near 1 mA and pull the divider down by 20 dB or more, and
    a x13 driver hits its 14 V rail at only +12 dB over threshold, so the
    compressor would stop compressing there. The Rev C driver is therefore
    x3 with a 2.62 V DC offset (LEDs still light at the 0.26 V / -18 dBFS
    sidechain level) and a 78k LED resistor. That gives 7 dB at +12 dB over,
    keeps rising (vactrol law, about 3:1 asymptotic) and does not rail until
    about +23 dB over threshold. These are the values modelled below and the
    ones to carry into the Rev C schematic (see the Rev C notes).
*/
class OptoCompressor
{
public:
    void prepare (double sampleRate)
    {
        averageCoefficient = rcCoefficient (kAverageR * kAverageC, sampleRate);
        cellOnCoefficient  = rcCoefficient (0.0025, sampleRate);
        cellOffFast        = rcCoefficient (0.035, sampleRate);
        cellOffSlow        = rcCoefficient (1.5, sampleRate);
        reset();
    }

    void reset() noexcept
    {
        average = 0.0f;
        fastConductance = slowConductance = kDarkConductance;
    }

    /** Process one stereo sample pair in place (digital full-scale units). */
    void process (float& left, float& right) noexcept
    {
        // --- sidechain, in bus volts
        const auto sum = -kSumGain * (left + right) * kBusVoltsPerFullScale;
        const auto rectified = juce::jmax (0.0f, sum);
        average += (rectified - average) * (1.0f - averageCoefficient);

        const auto driver = juce::jlimit (0.0f, kOpAmpRail, kDriverGain * average + kDriverOffsetVolts);
        const auto ledCurrent = juce::jmax (0.0f, driver - kLedForwardVolts) / kLedResistor;   // amps

        // --- photocell: conductance follows LED current with the vactrol's own ballistics
        const auto targetConductance = ledCurrent > 1.0e-9f
            ? 1.0f / (kCellOhmsAt1mA * std::pow (1.0e-3f / ledCurrent, kCellExponent))
            : kDarkConductance;

        fastConductance = follow (fastConductance, targetConductance, cellOnCoefficient, cellOffFast);
        slowConductance = follow (slowConductance, targetConductance, cellOnCoefficient, cellOffSlow);
        const auto conductance = 0.8f * fastConductance + 0.2f * slowConductance;

        // --- shunt divider: Vout / Vin = Rcell / (22k + Rcell) = 1 / (1 + 22k * G)
        const auto gain = 1.0f / (1.0f + kSeriesResistor * conductance);
        currentGain = gain;

        left  *= gain;
        right *= gain;
    }

    float getGainReductionDb() const noexcept
    {
        return -juce::Decibels::gainToDecibels (juce::jmax (1.0e-6f, currentGain));
    }

private:
    static float follow (float state, float target, float onCoefficient, float offCoefficient) noexcept
    {
        const auto coefficient = (target > state) ? onCoefficient : offCoefficient;
        return target + coefficient * (state - target);
    }

    // Parts
    static constexpr float kSeriesResistor   = 22.0e3f;    // R1101
    static constexpr float kSumGain          = 0.47f;      // 100k / 100k into 47k
    static constexpr double kAverageR        = 10.0e3;     // R1146
    static constexpr double kAverageC        = 1.0e-6;     // C1141
    static constexpr float kDriverGain       = 3.0f;       // Rev C: 1 + 20k / 10k
    static constexpr float kDriverOffsetVolts = 2.62f;     // Rev C: DC offset so the LEDs light at 0.26 V average
    static constexpr float kLedForwardVolts  = 3.4f;       // two vactrol LEDs in series
    static constexpr float kLedResistor      = 78.0e3f;    // Rev C value (see header note)
    static constexpr float kCellOhmsAt1mA    = 1500.0f;    // VTL5C3
    static constexpr float kCellExponent     = 0.7f;
    static constexpr float kDarkConductance  = 1.0f / 10.0e6f;

    float averageCoefficient = 0.0f, cellOnCoefficient = 0.0f, cellOffFast = 0.0f, cellOffSlow = 0.0f;
    float average = 0.0f;
    float fastConductance = kDarkConductance, slowConductance = kDarkConductance;
    float currentGain = 1.0f;
};

//==============================================================================
/** LIMIT: THAT2180 VCA with a discrete log-average detector (Rev B refs 13xx).

    Audio    U1301A unity inverter -> C1301 1u -> R1303 20k -> THAT2180 pin 1,
             pin 8 -> U1301B current-to-voltage (R1304 20k). Net non-inverting.
             Ec+ to AGND, Ec- is the shared control. The 2180's law is
             gain = -Ec / 6.1 mV per dB.
    Detector (feedback, linked, log-average)
             U1305A sums the two VCA outputs, SUM = -(L+R)/2 (20k / 20k / 10k)
             U1305B half-wave + U1305C summer = full-wave, FW = |L+R| / 2
             R1346 10k + C1344 1u: 10 ms average
             R1350 100k into U1305D with Q1341 (MMBT3906) as a transdiode:
             DET = Vt ln (I / Is), +3.0 mV per dB
    Control  U1302A difference amplifier x18.2 (10k / 182k, 100k / 1.82M)
             between DET and TH_REF (RV1342). 18.2 x 3.0 mV/dB = 54 mV/dB at Ec-,
             the 2180 takes off 6.1 mV/dB, so the loop gain is 8.9 dB per dB over
             threshold: a feedback ratio of about 10:1, hard knee.
             U1302B precision positive clamp: Ec never goes negative, so there
             is no gain boost below threshold. U1302D buffers it into Ec-.

    TH_REF is solved here for the -18 dBFS threshold (a full-scale-referenced
    sine at 0.87 Vpk on both channels averages 0.554 V after the rectifier,
    5.5 uA into the log transistor), which is what RV1342 is trimmed to.
*/
class VcaLimiter
{
public:
    void prepare (double sampleRate)
    {
        averageCoefficient = rcCoefficient (kAverageR * kAverageC, sampleRate);

        // Threshold reference: mean of the full-wave rectified sum at -18 dBFS.
        const auto thresholdPeakVolts = juce::Decibels::decibelsToGain (kThresholdDbfs) * kBusVoltsPerFullScale;
        const auto thresholdAverage   = 2.0f * thresholdPeakVolts / juce::MathConstants<float>::pi;
        thresholdReference = logConvert (thresholdAverage / kLogResistor);
        reset();
    }

    void reset() noexcept
    {
        average = 0.0f;
        controlVolts = 0.0f;
    }

    void process (float& left, float& right) noexcept
    {
        // --- VCA: gain set by the control voltage from the previous sample
        const auto gainDb = -controlVolts / kVcaVoltsPerDb;
        const auto gain = std::exp (gainDb * kDbToNatural);
        left  *= gain;
        right *= gain;

        // --- detector on the VCA OUTPUT (feedback topology), in bus volts
        const auto fullWave = std::abs (0.5f * (left + right)) * kBusVoltsPerFullScale;
        average += (fullWave - average) * (1.0f - averageCoefficient);

        const auto detector = logConvert (average / kLogResistor);

        // --- difference amp + positive clamp -> Ec-
        controlVolts = juce::jlimit (0.0f, kMaxControlVolts, kDifferenceGain * (detector - thresholdReference));
    }

    float getGainReductionDb() const noexcept { return controlVolts / kVcaVoltsPerDb; }

private:
    static float logConvert (float amps) noexcept
    {
        return kThermalVoltage * std::log (juce::jmax (1.0e-13f, amps) / kTransdiodeIs);
    }

    // Parts
    static constexpr double kAverageR        = 10.0e3;      // R1346
    static constexpr double kAverageC        = 1.0e-6;      // C1344
    static constexpr float kLogResistor      = 100.0e3f;    // R1350
    static constexpr float kTransdiodeIs     = 1.0e-14f;    // MMBT3906, cancels against TH_REF
    static constexpr float kDifferenceGain   = 18.2f;       // 182k / 10k
    static constexpr float kVcaVoltsPerDb    = 0.0061f;     // THAT2180: 6.1 mV per dB
    static constexpr float kMaxControlVolts  = 0.0061f * 60.0f;   // 60 dB of reduction is all the 2180 will give cleanly
    static constexpr float kDbToNatural      = 0.11512925f; // ln(10) / 20

    float averageCoefficient = 0.0f;
    float thresholdReference = 0.0f;
    float average = 0.0f;
    float controlVolts = 0.0f;
};

} // namespace gas::dynamics
