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

      Comp   MMBF5457 JFET shunt (1176 style), feedback linked sidechain   <- Rev C
      Limit  Coolaudio V2181 VCA + discrete log-average detector (dbx 160 style), feedback

    2026-09-30: Comp is the FET compressor, refs 12xx on the Rev C circuit board. The
    VTL5C3 vactrol (OptoCompressor, refs 11xx) is NOT on the Rev C board; it is kept
    below for reference only and nothing calls it. The limiter part is a Coolaudio
    V2181 rather than a THAT2180A; the 6.1 mV/dB control law is identical, so the
    VcaLimiter maths is unchanged, but RV1301 / RV1321 symmetry trims are now fitted.
*/
namespace gas::dynamics
{

inline constexpr float kBusVoltsPerFullScale = 6.93f;   // mode bus: 0 dBFS = 6.93 Vpk
// Fixed, as on the hardware: RV1201 / RV1221 (Comp) and RV1342 (Limit) are trimmed to
// it, not exposed as a knob. 2026-09-30: dropped 6 dB, from -18 to -24 dBFS, so both
// circuits start working earlier now that they sit in the feedback return leg and their
// job is holding the loop down rather than shaping the wet signal.
inline constexpr float kThresholdDbfs        = -24.0f;
inline constexpr float kThermalVoltage       = 0.02585f;
/** The +/-15 V rails carry OPA1679 quads (and OPA1656 duals on the tank driver board).
    TI specifies the OPA1679's rail-to-rail output as swinging to within 800 mV of the
    rail into 2 kohm, so 15.0 - 0.8 = 14.2 V is the datasheet figure and 14.0 V is a
    slightly conservative stand-in that also covers heavier loading. The TL072H parts
    are not on these rails; they run from the separate +9 V clipper supply, whose own
    4.5 V rail is modelled in ClipperCircuitModels.h. */
inline constexpr float kOpAmpRail            = 14.0f;

/** Where the output stage stops being linear, as a fraction of kOpAmpRail. The OPA1679
    has a rail-to-rail output, so its swing limit is set by the output device's on
    resistance against the load current rather than a fixed transistor drop: it comes
    out of linear across roughly the same 800 mV the datasheet quotes as headroom.
    0.93 * 14 V = 13.0 V puts the knee about a volt below the rail, which matches that.
    TI quotes a single headroom figure rather than separate positive and negative ones,
    so the curve is symmetric; there is no published asymmetry to model. */
inline constexpr float kRailKneeFraction     = 0.93f;

/** One op-amp output running out of rail.

    While the feedback loop still has headroom the output is exactly linear, so this
    returns the sample untouched below the knee and nothing at normal levels is altered
    at all. Above the knee the loop gain collapses and the output stage compresses, so
    the curve rounds over and then pins at the rail. Value and slope match at both ends
    of the knee, which is what keeps it from producing the harsh high harmonics a bare
    hard clip does.

    `rail` is in the same units as the sample, so callers pass the rail expressed as
    linear gain rather than volts.
*/
inline float saturateAtRail (float value, float rail) noexcept
{
    const auto magnitude = std::abs (value);
    const auto knee = kRailKneeFraction * rail;

    if (magnitude <= knee)
        return value;

    const auto sign = value < 0.0f ? -1.0f : 1.0f;
    const auto span = rail - knee;              // how much output is left above the knee

    // Slope 1 at the knee means the input runs 2 * span before the output pins.
    const auto u = (magnitude - knee) / (2.0f * span);

    if (u >= 1.0f)
        return sign * rail;

    return sign * (knee + span * u * (2.0f - u));
}

/** One-pole coefficient for an RC time constant. */
inline float rcCoefficient (double seconds, double sampleRate) noexcept
{
    return static_cast<float> (std::exp (-1.0 / (sampleRate * juce::jmax (1.0e-6, seconds))));
}

//==============================================================================
/** COMP: MMBF5457 FET compressor, 1176 territory (Rev C refs 12xx).

    This is the Comp position on the Rev C board. Read off
    `hardware/kicad/revc/gen/boards/circuit_board.py`, block
    "Comp: MMBF5457 FET compressor (1176 territory), linked feedback sidechain".

    Audio (per channel, U1201 A / B)
             R1201 22k from DYN_IN into FET_DIV, R1202 2.2k from FET_DIV to AGND,
             Q1201 MMBF5457 drain on FET_DIV and source on AGND, so the JFET is a
             voltage-controlled resistor in parallel with the 2.2k shunt leg.
             Non-inverting make-up R1207 100k / R1208 10k = x11.
             At rest the JFET is pinched off, so the divider is 2.2k / 24.2k = 1/11
             and the make-up puts it back: the circuit is exactly unity until it
             starts working. That is why 22k, 2.2k and x11 are the values they are.

    Gate     R1204 1M from the gate to FET_DIV and R1203 1M from the gate to the
             control voltage, so Vg sits at the midpoint of the two. This is the
             1176 distortion-cancelling trick: feeding half the drain swing back to
             the gate cancels the square-law term, so in the ohmic region the JFET
             is a clean resistor. It stops cancelling once the drain swing pushes
             the device toward saturation, and that residual is the grit.

    Control  RV1201 10k trim off -15VA sets FET_BIAS. R1205 47k from FET_BIAS and
             R1206 100k from the shared sidechain envelope meet at FET_CV, so
             FET_CV = 0.680 * bias + 0.320 * envelope. With the trim hard over that
             reaches Vgs = -5.1 V, which is the figure in the hardware notes and is
             why the part is screened for |Vgs(off)| under 5 V.

    Sidechain (feedback, linked)
             Taken from the compressor OUTPUT, not its input: R1241 / R1242 20k from
             FET_OUT_L and FET_OUT_R into U1201C with R1243 40.2k feedback, so
             SUM = -2.01 * (L + R), the "x4" over (L+R)/2.
             U1201D with D1241 / D1242 and R1244 / R1245 10k is a precision half-wave
             rectifier, so those two diode drops are inside the loop and cancel.
             D1243 1N5819HW is OUTSIDE the loop into R1246 1.5k + C1241 100nF:
             150 us attack, and R1247 2.2M across the cap gives 220 ms release.
             The Schottky drop is therefore real and is part of where it starts.

    Ratio is not a knob and not a fixed number. It falls out of the feedback loop
    and the JFET law, exactly as the Rev B notes say ("ratio is set by the FET law
    plus the pad, not a fixed 4:1"). RV1201 is trimmed on the bench so gain just
    starts to drop at -18 dBFS, and prepare() solves the same bias here.

    JFET spread: 2N5457 / MMBF5457 is specified Idss 1 to 5 mA and Vgs(off) -0.5 to
    -6 V. Modelled at a typical Idss 3 mA, Vp -3 V. On the board RV1201 / RV1221
    absorb the part-to-part spread, which is what those trims are for.
*/
class FetCompressor
{
public:
    void prepare (double sampleRate)
    {
        attackCoefficient  = rcCoefficient (kAttackR * kDetectorC, sampleRate);    // 1.5k  * 100n = 150 us
        releaseCoefficient = rcCoefficient (kReleaseR * kDetectorC, sampleRate);   // 2.2M  * 100n = 220 ms

        // Solve RV1201 the way the bench procedure sets it: "gain just starts to drop
        // at the threshold", which means the gate just reaches pinch-off at that level.
        const auto thresholdPeak = juce::Decibels::decibelsToGain (kThresholdDbfs) * kBusVoltsPerFullScale;
        const auto sidechainPeak = kSidechainGain * 2.0f * thresholdPeak;          // L and R both at threshold
        const auto envelopeAtThreshold = juce::jmax (0.0f, sidechainPeak - kSchottkyDrop);

        // Vg = FET_CV / 2 with no signal on the drain, and we want Vg = Vp there.
        biasVolts = juce::jlimit (-15.0f, 0.0f,
                                  (2.0f * kPinchOff - kScShare * envelopeAtThreshold) / kBiasShare);
        reset();
    }

    void reset() noexcept
    {
        envelope = 0.0f;
        currentGain = 1.0f;
    }

    /** Process one stereo sample pair in place (digital full-scale units). */
    void process (float& left, float& right) noexcept
    {
        // The detector hangs off the output, so it always acts on the previous sample.
        // That one-sample lag is what the real loop has too: the cap cannot move faster
        // than its own time constant.
        const auto controlVolts = kBiasShare * biasVolts + kScShare * envelope;

        const auto outLeft  = solveDivider (left  * kBusVoltsPerFullScale, controlVolts);
        const auto outRight = solveDivider (right * kBusVoltsPerFullScale, controlVolts);

        // Small-signal gain at this control voltage, for the meter.
        const auto restOverdrive = 0.5f * controlVolts - kPinchOff;
        const auto restConductance = restOverdrive > 0.0f ? 2.0f * kBeta * restOverdrive : 0.0f;
        currentGain = kMakeUpGain / (kMakeUpGain + kSeriesResistor * restConductance);

        left  = outLeft  / kBusVoltsPerFullScale;
        right = outRight / kBusVoltsPerFullScale;

        // --- sidechain: summed from both outputs, rectified, peak detected
        //
        // U1201C is an OPA1679 on +/-15 V like everything else, so the summer runs out
        // of rail at about 14 V. At x2.01 over (L + R) that starts to bite around
        // +6 dBFS in, and it is why the compressor tops out near 11 dB of reduction
        // rather than carrying on for ever. Same physics that killed the old x13
        // vactrol driver, just far better behaved here.
        const auto summed = saturateAtRail (kSidechainGain * (outLeft + outRight), kOpAmpRail);
        const auto rectified = juce::jmax (0.0f, summed);                  // diode drops cancelled in the loop
        const auto target = juce::jmax (0.0f, rectified - kSchottkyDrop);  // D1243 sits outside it

        const auto coefficient = target > envelope ? attackCoefficient : releaseCoefficient;
        envelope = target + coefficient * (envelope - target);
    }

    float getGainReductionDb() const noexcept
    {
        return -juce::Decibels::gainToDecibels (juce::jmax (1.0e-6f, currentGain));
    }

private:
    /** JFET drain current and its slope, with the gate at (controlVolts + Vd) / 2.

        The device is symmetric, so a negative drain node just swaps which end is the
        source; working from |Vd| and putting the sign back gives the same answer.
    */
    static float jfetCurrent (float drainVolts, float controlVolts, float& slope) noexcept
    {
        const auto sign = drainVolts < 0.0f ? -1.0f : 1.0f;
        const auto u = std::abs (drainVolts);
        const auto overdrive = 0.5f * (controlVolts + u) - kPinchOff;

        if (overdrive <= 0.0f)     // pinched off: the 2.2k leg is the whole shunt
        {
            slope = 0.0f;
            return 0.0f;
        }

        if (u < overdrive)         // ohmic. The u^2 term is what the 1M / 1M gate network cancels.
        {
            slope = 2.0f * kBeta * (overdrive - 0.5f * u);
            return sign * 2.0f * kBeta * (overdrive * u - 0.5f * u * u);
        }

        slope = kBeta * overdrive; // saturated: current stops following the drain, so it stops being a resistor
        return sign * kBeta * overdrive * overdrive;
    }

    /** Solves (vin - vd) / 22k = vd / 2.2k + Ids(vd) for the drain node, then the x11 make-up. */
    static float solveDivider (float vin, float controlVolts) noexcept
    {
        auto vd = vin * kRestDivider;   // start from the pinched-off answer, which is exact at rest

        for (int i = 0; i < 3; ++i)
        {
            float slope = 0.0f;
            const auto current = jfetCurrent (vd, controlVolts, slope);
            const auto error = (vin - vd) * kSeriesConductance - vd * kShuntConductance - current;
            const auto derivative = -kSeriesConductance - kShuntConductance - slope;
            vd -= error / derivative;
        }

        return vd * kMakeUpGain;
    }

    // Parts
    static constexpr float kSeriesResistor = 22.0e3f;      // R1201
    static constexpr float kShuntResistor  = 2.2e3f;       // R1202
    static constexpr float kSeriesConductance = 1.0f / kSeriesResistor;
    static constexpr float kShuntConductance  = 1.0f / kShuntResistor;
    static constexpr float kRestDivider    = kShuntResistor / (kSeriesResistor + kShuntResistor);
    static constexpr float kMakeUpGain     = 11.0f;        // 1 + R1207 100k / R1208 10k
    static constexpr float kSidechainGain  = 2.01f;        // R1243 40.2k / R1241 20k
    static constexpr float kSchottkyDrop   = 0.27f;        // D1243 1N5819HW at detector currents
    static constexpr double kAttackR       = 1.5e3;        // R1246
    static constexpr double kReleaseR      = 2.2e6;        // R1247
    static constexpr double kDetectorC     = 100.0e-9;     // C1241
    static constexpr float kBiasShare      = 0.6802f;      // 100k / (47k + 100k), R1205 / R1206
    static constexpr float kScShare        = 0.3197f;      // 47k  / (47k + 100k)

    // MMBF5457, typical part (the board trims the spread out)
    static constexpr float kIdss     = 3.0e-3f;
    static constexpr float kPinchOff = -3.0f;
    static constexpr float kBeta     = kIdss / (kPinchOff * kPinchOff);

    float attackCoefficient = 0.0f, releaseCoefficient = 0.0f;
    float biasVolts = -10.0f;
    float envelope = 0.0f;
    float currentGain = 1.0f;
};

//==============================================================================
/** COMP (Rev B only, NOT on the Rev C board): Vactrol opto compressor (Rev B refs 11xx).

    Kept for reference. Rev C dropped the vactrol and uses FetCompressor above.
    Nothing in the plugin calls this class.

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

        // Threshold reference: mean of the full-wave rectified sum at the threshold.
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
