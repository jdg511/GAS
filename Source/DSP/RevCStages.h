#pragma once

#include <JuceHeader.h>

#include <array>
#include <atomic>
#include <mutex>
#include <vector>

#include "ClipperCircuitModels.h"
#include "DynamicsModels.h"
#include "SaturationModels.h"

namespace gas::revc
{
inline constexpr size_t kOversamplingOrder  = 2;                          // 2^2 = 4x
inline constexpr size_t kOversamplingFactor = size_t (1) << kOversamplingOrder;
}

/**
    Rev C circuit stages.

    Three places in the Rev C signal path hold real circuits, each one a
    pull-knob or a switch on the board:

      TubeTapeStage      "Vol (pull for Tube)" at the wet input, and the Output
                         knob ("pull for Tape") at the very end. Tube = the J201
                         stage, Tape = the 2N3904 differential pair with record /
                         repro EQ. When the input knob is pulled the output stage
                         runs the tube as well, ahead of the tape.

      DirtDynamicsBlock  where the Rev B mode circuit sat: pre-HPF -> Gain knob
                         ("pull for Dirt" = Tube Screamer) -> Comp / Off / Limit
                         switch (vactrol compressor / THAT2180 limiter) -> post-LPF.

    Every nonlinear circuit runs 4x oversampled (as the Rev B plugin did). Engaging a circuit crossfades
    over about 15 ms so a pull never clicks; the fade happens INSIDE the chain
    (before whatever follows) so a compressor always sees the signal it will pass.
*/

//==============================================================================
/** Stereo tube and/or tape emulation, oversampled. */
class TubeTapeStage
{
public:
    void prepare (double sampleRate, int maximumBlockSize)
    {
        oversampling = std::make_unique<juce::dsp::Oversampling<float>> (2, gas::revc::kOversamplingOrder,
                            juce::dsp::Oversampling<float>::filterHalfBandPolyphaseIIR, true);
        oversampling->initProcessing (static_cast<size_t> (maximumBlockSize));

        const auto oversampledRate = sampleRate * static_cast<double> (gas::revc::kOversamplingFactor);

        for (auto& t : triodes) t.prepare (oversampledRate);
        for (auto& t : tapes)   t.prepare (oversampledRate);

        tubeMix.reset (sampleRate, 0.015);
        tapeMix.reset (sampleRate, 0.015);
        tubeMix.setCurrentAndTargetValue (0.0f);
        tapeMix.setCurrentAndTargetValue (0.0f);

        tubeRamp.assign (static_cast<size_t> (maximumBlockSize), 0.0f);
        tapeRamp.assign (static_cast<size_t> (maximumBlockSize), 0.0f);
        reset();
    }

    void reset()
    {
        if (oversampling != nullptr)
            oversampling->reset();

        for (auto& t : triodes) t.reset();
        for (auto& t : tapes)   t.reset();
        dcX1 = { { 0.0f, 0.0f } };
        dcY1 = { { 0.0f, 0.0f } };
    }

    void setEnabled (bool tube, bool tape)
    {
        tubeMix.setTargetValue (tube ? 1.0f : 0.0f);
        tapeMix.setTargetValue (tape ? 1.0f : 0.0f);
    }

    bool isTubeEngaged() const noexcept { return tubeMix.getTargetValue() > 0.5f; }
    bool isTapeEngaged() const noexcept { return tapeMix.getTargetValue() > 0.5f; }

    void process (juce::AudioBuffer<float>& stereo, int numSamples)
    {
        const auto tubeActive = tubeMix.getTargetValue() > 0.5f || tubeMix.isSmoothing();
        const auto tapeActive = tapeMix.getTargetValue() > 0.5f || tapeMix.isSmoothing();

        if (! tubeActive && ! tapeActive)
        {
            tubeMix.skip (numSamples);
            tapeMix.skip (numSamples);
            return;
        }

        // Engage ramps at the base rate; the oversampled loop reads them at i / factor.
        for (int i = 0; i < numSamples; ++i)
        {
            tubeRamp[static_cast<size_t> (i)] = tubeMix.getNextValue();
            tapeRamp[static_cast<size_t> (i)] = tapeMix.getNextValue();
        }

        juce::dsp::AudioBlock<float> block (stereo);
        auto base = block.getSubBlock (0, static_cast<size_t> (numSamples));
        auto up = oversampling->processSamplesUp (base);

        for (size_t channel = 0; channel < 2; ++channel)
        {
            auto* samples = up.getChannelPointer (channel);
            auto& triode = triodes[channel];
            auto& tape = tapes[channel];

            for (size_t i = 0; i < up.getNumSamples(); ++i)
            {
                const auto baseIndex = juce::jmin (i / gas::revc::kOversamplingFactor, static_cast<size_t> (numSamples - 1));
                auto x = samples[i];

                if (tubeActive)
                {
                    const auto y = triode.process (x);
                    x += (y - x) * tubeRamp[baseIndex];
                }

                if (tapeActive)
                {
                    const auto y = tape.process (x);
                    x += (y - x) * tapeRamp[baseIndex];
                }

                samples[i] = x;
            }
        }

        oversampling->processSamplesDown (base);

        // The JFET stage is asymmetric and shifts its bias, so strip the DC it
        // leaves behind. First-order, ~3.5 Hz at 44.1 kHz: inaudible on program.
        if (tubeActive)
        {
            for (int channel = 0; channel < 2; ++channel)
            {
                auto* out = stereo.getWritePointer (channel);
                auto& x1 = dcX1[static_cast<size_t> (channel)];
                auto& y1 = dcY1[static_cast<size_t> (channel)];

                for (int i = 0; i < numSamples; ++i)
                {
                    const auto value = out[i];
                    const auto blocked = value - x1 + 0.9995f * y1;
                    x1 = value;
                    y1 = blocked;
                    out[i] = blocked;
                }
            }
        }
    }

private:
    std::unique_ptr<juce::dsp::Oversampling<float>> oversampling;
    std::array<gas::saturation::JfetTubeStage, 2> triodes;
    std::array<gas::saturation::TapeDiffPairStage, 2> tapes;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> tubeMix, tapeMix;
    std::vector<float> tubeRamp, tapeRamp;
    std::array<float, 2> dcX1 { { 0.0f, 0.0f } }, dcY1 { { 0.0f, 0.0f } };
};

//==============================================================================
/** Pre-HPF -> Gain -> [Tube Screamer] -> [Comp | Off | Limit] -> post-LPF. */
class DirtDynamicsBlock
{
public:
    enum class Dynamics
    {
        comp = 0,
        off,
        limit
    };

    static juce::StringArray getDynamicsNames() { return { "Comp", "Off", "Limit" }; }

    struct Parameters
    {
        float gainDb = 0.0f;
        bool dirt = false;
        Dynamics dynamics = Dynamics::off;
        float preHpfCutoffHz = 120.0f;
        float postLpfCutoffHz = 15000.0f;
        float filterQ = 0.70710678f;
    };

    void prepare (double sampleRate, int maximumBlockSize)
    {
        currentSampleRate = sampleRate;
        oversampling = std::make_unique<juce::dsp::Oversampling<float>> (2, gas::revc::kOversamplingOrder,
                            juce::dsp::Oversampling<float>::filterHalfBandPolyphaseIIR, true);
        oversampling->initProcessing (static_cast<size_t> (maximumBlockSize));

        getTubeScreamerCurve();

        const auto oversampledRate = sampleRate * static_cast<double> (gas::revc::kOversamplingFactor);
        opto.prepare (oversampledRate);
        vca.prepare (oversampledRate);

        for (auto& f : preHpf)  { f.reset(); f.setType (juce::dsp::StateVariableTPTFilterType::highpass); }
        for (auto& f : postLpf) { f.reset(); f.setType (juce::dsp::StateVariableTPTFilterType::lowpass); }

        gainDb.reset (sampleRate, 0.03);
        preHpfCutoffHz.reset (sampleRate, 0.03);
        postLpfCutoffHz.reset (sampleRate, 0.03);
        dirtMix.reset (sampleRate, 0.015);
        gainDb.setCurrentAndTargetValue (0.0f);
        preHpfCutoffHz.setCurrentAndTargetValue (120.0f);
        postLpfCutoffHz.setCurrentAndTargetValue (15000.0f);
        dirtMix.setCurrentAndTargetValue (0.0f);

        dirtRamp.assign (static_cast<size_t> (maximumBlockSize), 0.0f);
        reset();
    }

    void reset()
    {
        if (oversampling != nullptr)
            oversampling->reset();

        for (auto& f : preHpf)  f.reset();
        for (auto& f : postLpf) f.reset();
        opto.reset();
        vca.reset();
        gainDb.setCurrentAndTargetValue (gainDb.getTargetValue());
        preHpfCutoffHz.setCurrentAndTargetValue (preHpfCutoffHz.getTargetValue());
        postLpfCutoffHz.setCurrentAndTargetValue (postLpfCutoffHz.getTargetValue());
    }

    void setParameters (const Parameters& p)
    {
        gainDb.setTargetValue (p.gainDb);
        dirtMix.setTargetValue (p.dirt ? 1.0f : 0.0f);
        preHpfCutoffHz.setTargetValue (p.preHpfCutoffHz);
        postLpfCutoffHz.setTargetValue (p.postLpfCutoffHz);
        filterQ = p.filterQ;

        if (p.dynamics != dynamics)
        {
            dynamics = p.dynamics;
            dynamicsChanged.store (true, std::memory_order_relaxed);
        }
    }

    /** Gain reduction of the active dynamics circuit, dB, for metering. */
    float getGainReductionDb() const noexcept { return gainReductionDb.load (std::memory_order_relaxed); }

    void process (juce::AudioBuffer<float>& stereo, int numSamples)
    {
        auto* left = stereo.getWritePointer (0);
        auto* right = stereo.getWritePointer (1);

        const auto gain = juce::Decibels::decibelsToGain (gainDb.skip (numSamples));
        updateFilters (preHpfCutoffHz.skip (numSamples), postLpfCutoffHz.skip (numSamples));

        if (dynamicsChanged.exchange (false, std::memory_order_relaxed))
        {
            opto.reset();
            vca.reset();
        }

        // Pre-HPF, then the Gain knob (the board's +/-18 dB pot stage).
        for (int i = 0; i < numSamples; ++i)
        {
            left[i]  = preHpf[0].processSample (0, left[i]) * gain;
            right[i] = preHpf[1].processSample (0, right[i]) * gain;
        }

        const auto dirtActive = dirtMix.getTargetValue() > 0.5f || dirtMix.isSmoothing();
        const auto activeDynamics = dynamics;
        const auto dynamicsActive = activeDynamics != Dynamics::off;

        if (dirtActive || dynamicsActive)
        {
            for (int i = 0; i < numSamples; ++i)
                dirtRamp[static_cast<size_t> (i)] = dirtMix.getNextValue();

            juce::dsp::AudioBlock<float> block (stereo);
            auto base = block.getSubBlock (0, static_cast<size_t> (numSamples));
            auto up = oversampling->processSamplesUp (base);

            const auto& curve = getTubeScreamerCurve();
            auto* l = up.getChannelPointer (0);
            auto* r = up.getChannelPointer (1);

            for (size_t i = 0; i < up.getNumSamples(); ++i)
            {
                auto xl = l[i];
                auto xr = r[i];

                if (dirtActive)
                {
                    const auto amount = dirtRamp[juce::jmin (i / gas::revc::kOversamplingFactor, static_cast<size_t> (numSamples - 1))];
                    xl += (curve.process (xl) - xl) * amount;
                    xr += (curve.process (xr) - xr) * amount;
                }

                switch (activeDynamics)
                {
                    case Dynamics::comp:  opto.process (xl, xr); break;
                    case Dynamics::limit: vca.process (xl, xr); break;
                    case Dynamics::off:
                    default: break;
                }

                l[i] = xl;
                r[i] = xr;
            }

            oversampling->processSamplesDown (base);

            gainReductionDb.store (activeDynamics == Dynamics::comp  ? opto.getGainReductionDb()
                                 : activeDynamics == Dynamics::limit ? vca.getGainReductionDb()
                                                                     : 0.0f,
                                   std::memory_order_relaxed);
        }
        else
        {
            dirtMix.skip (numSamples);
            gainReductionDb.store (0.0f, std::memory_order_relaxed);
        }

        for (int i = 0; i < numSamples; ++i)
        {
            left[i]  = postLpf[0].processSample (0, left[i]);
            right[i] = postLpf[1].processSample (0, right[i]);
        }
    }

private:
    using CircuitSpec = gas::circuits::CircuitSpec;
    using CircuitCurve = gas::circuits::CircuitCurve;

    /** The Tube Screamer clipping stage (Rev B refs 8xx / 9xx): TL072, Rf 51k with
        2x 1N4148W anti-parallel, Rg 4.7k, 9 V rail biased to 4.5 V. Fed at pedal
        level through the board's -36.8 dB pad (0 dBFS = 100 mV) and scaled back
        to bus level, so the +1.4 dB clean gain and the -6 dBFS knee land where
        the hardware puts them. Solved from the Shockley equation once per process. */
    static const CircuitCurve& getTubeScreamerCurve()
    {
        using namespace gas::circuits;
        static CircuitCurve curve;
        static std::once_flag built;

        std::call_once (built, []
        {
            CircuitSpec spec { Topology::feedback, 51.0e3f, 4.7e3f, 0.0f, kDiode1N4148, 1, kDiode1N4148, 1 };
            spec.inputVoltsPerFullScale  = kGuitarLevelVoltsPerFullScale;
            spec.outputVoltsPerFullScale = kLineLevelVoltsPerFullScale;
            curve.build (spec);
        });

        return curve;
    }

    void updateFilters (float preCutoff, float postCutoff)
    {
        const auto nyquistGuard = static_cast<float> (0.45 * currentSampleRate);
        const auto pre = juce::jlimit (1.0f, nyquistGuard, preCutoff);
        const auto post = juce::jlimit (200.0f, nyquistGuard, postCutoff);

        for (auto& f : preHpf)  { f.setCutoffFrequency (pre);  f.setResonance (filterQ); }
        for (auto& f : postLpf) { f.setCutoffFrequency (post); f.setResonance (filterQ); }
    }

    double currentSampleRate = 44100.0;
    Dynamics dynamics = Dynamics::off;
    std::atomic<bool> dynamicsChanged { false };
    std::atomic<float> gainReductionDb { 0.0f };
    float filterQ = 0.70710678f;

    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> gainDb, preHpfCutoffHz, postLpfCutoffHz, dirtMix;
    std::vector<float> dirtRamp;
    std::array<juce::dsp::StateVariableTPTFilter<float>, 2> preHpf, postLpf;
    gas::dynamics::OptoCompressor opto;
    gas::dynamics::VcaLimiter vca;
    std::unique_ptr<juce::dsp::Oversampling<float>> oversampling;
};
