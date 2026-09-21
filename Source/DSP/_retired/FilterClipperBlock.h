#pragma once

#include <JuceHeader.h>

#include <array>
#include <mutex>

#include "ClipperCircuitModels.h"
#include "DynamicsModels.h"
#include "SaturationModels.h"

/**
    The plugin's clipping / dynamics stage.

    Six selectable circuits sit between the pre-emphasis high-pass and the post
    low-pass (list trimmed 2026-09-12):

      Tube          12AX7-style triode stage: asymmetric, bias-shifting     (SaturationModels.h)
      Tape          record EQ -> magnetisation curve -> repro EQ, head bump (SaturationModels.h)
      Tube Screamer 2x 1N4148 across Rf, solved from the Shockley equation  (ClipperCircuitModels.h)
      Opto / FET / VCA  one-knob gain-reduction circuits: LA-2A, 1176, dbx 160 (DynamicsModels.h)

    Everything is driven by the single Drive control.
*/
class FilterClipperBlock
{
public:
    enum class Mode
    {
        clean = 0,
        tube,
        tape,
        tubeScreamer,
        optoCompressor,
        fetCompressor,
        vcaLimiter,
        numModes
    };

    static constexpr int numClipperCurves = 1;   // only the Tube Screamer is a solved diode curve now

    /** Display names, in parameter order. Shared by the parameter layout and
        the editor so the two can never drift apart. */
    static juce::StringArray getModeNames()
    {
        return { "Clean",
                 "Tube",
                 "Tape",
                 "Tube Screamer",
                 "Opto Comp",
                 "FET Comp",
                 "VCA Limiter" };
    }

    /** One-line description of what each circuit is, for the editor readout. */
    static juce::String getModeDescription (Mode mode)
    {
        switch (mode)
        {
            case Mode::tube:           return "J201 JFET stage after a x11 op-amp boost. Square-law squash, gate-diode bias sag.";
            case Mode::tape:           return "Op-amp record EQ into a 2N3904 diff-pair limiter, passive repro EQ. Highs squash first.";
            case Mode::tubeScreamer:   return "2x 1N4148 across Rf - TS808. Smooth, dynamic, never squares off.";
            case Mode::optoCompressor: return "Vactrol LED/LDR - LA-2A. Dual-slope release, rising ratio.";
            case Mode::fetCompressor:  return "2N5457 FET - 1176LN. 150 us attack, 4:1, FET grit included.";
            case Mode::vcaLimiter:     return "THAT2180 VCA + true RMS - dbx 160. 10:1, over-easy knee.";
            case Mode::clean:
            case Mode::numModes:
            default:                          return "No clipping stage - filters and level only.";
        }
    }

    static bool isDynamicsMode (Mode mode) noexcept
    {
        return mode == Mode::optoCompressor
            || mode == Mode::fetCompressor
            || mode == Mode::vcaLimiter;
    }

    static bool isSaturationMode (Mode mode) noexcept
    {
        return mode == Mode::tube || mode == Mode::tape;
    }

    struct Parameters
    {
        Mode mode = Mode::clean;
        float driveDb = 0.0f;
        float preHpfCutoffHz = 120.0f;
        float preHpfResonance = 1.0f;
        float postLpfCutoffHz = 15000.0f;
        float postLpfResonance = 1.0f;
    };

    void prepare (double sampleRate, int maximumBlockSize)
    {
        currentSampleRate = sampleRate;
        oversampling = std::make_unique<juce::dsp::Oversampling<float>> (2,
                                                                         2,
                                                                         juce::dsp::Oversampling<float>::filterHalfBandPolyphaseIIR,
                                                                         true);
        oversampling->initProcessing (static_cast<size_t> (maximumBlockSize));
        oversampling->reset();

        // The circuit curves are sample-rate independent, so they are solved
        // once for the whole process and shared by every instance.
        getCurves();

        const auto oversampledRate = sampleRate * static_cast<double> (oversampling->getOversamplingFactor());

        for (auto& compressor : optoCompressors)
            compressor.prepare (oversampledRate);

        for (auto& compressor : fetCompressors)
            compressor.prepare (oversampledRate);

        for (auto& limiter : vcaLimiters)
            limiter.prepare (oversampledRate);

        for (auto& triode : triodes)
            triode.prepare (oversampledRate);

        for (auto& tape : tapes)
            tape.prepare (oversampledRate);

        for (auto& filter : preHpf)
        {
            filter.reset();
            filter.setType (juce::dsp::StateVariableTPTFilterType::highpass);
        }

        for (auto& filter : postLpf)
        {
            filter.reset();
            filter.setType (juce::dsp::StateVariableTPTFilterType::lowpass);
        }

        driveDb.reset (sampleRate, 0.03);
        preHpfCutoffHz.reset (sampleRate, 0.03);
        preHpfResonance.reset (sampleRate, 0.03);
        postLpfCutoffHz.reset (sampleRate, 0.03);
        postLpfResonance.reset (sampleRate, 0.03);

        driveDb.setCurrentAndTargetValue (0.0f);
        preHpfCutoffHz.setCurrentAndTargetValue (1.0f);
        preHpfResonance.setCurrentAndTargetValue (1.0f);
        postLpfCutoffHz.setCurrentAndTargetValue (15000.0f);
        postLpfResonance.setCurrentAndTargetValue (1.0f);
        mode = Mode::clean;
    }

    void reset()
    {
        if (oversampling != nullptr)
            oversampling->reset();

        driveDb.setCurrentAndTargetValue (driveDb.getTargetValue());
        preHpfCutoffHz.setCurrentAndTargetValue (preHpfCutoffHz.getTargetValue());
        preHpfResonance.setCurrentAndTargetValue (preHpfResonance.getTargetValue());
        postLpfCutoffHz.setCurrentAndTargetValue (postLpfCutoffHz.getTargetValue());
        postLpfResonance.setCurrentAndTargetValue (postLpfResonance.getTargetValue());

        for (auto& filter : preHpf)
            filter.reset();

        for (auto& filter : postLpf)
            filter.reset();

        for (auto& compressor : optoCompressors)
            compressor.reset();

        for (auto& compressor : fetCompressors)
            compressor.reset();

        for (auto& limiter : vcaLimiters)
            limiter.reset();

        for (auto& triode : triodes)
            triode.reset();

        for (auto& tape : tapes)
            tape.reset();

        dcBlockerX1 = { { 0.0f, 0.0f } };
        dcBlockerY1 = { { 0.0f, 0.0f } };
    }

    void setParameters (const Parameters& newParameters)
    {
        if (newParameters.mode != mode)
            modeChanged.store (true, std::memory_order_relaxed);

        mode = newParameters.mode;
        driveDb.setTargetValue (newParameters.driveDb);
        preHpfCutoffHz.setTargetValue (newParameters.preHpfCutoffHz);
        preHpfResonance.setTargetValue (newParameters.preHpfResonance);
        postLpfCutoffHz.setTargetValue (newParameters.postLpfCutoffHz);
        postLpfResonance.setTargetValue (newParameters.postLpfResonance);
    }

    /** Gain reduction in dB, for metering. Zero unless a dynamics mode is active. */
    float getGainReductionDb() const noexcept { return gainReductionDb.load (std::memory_order_relaxed); }

    void process (juce::AudioBuffer<float>& stereoBuffer, int numSamples)
    {
        auto* left = stereoBuffer.getWritePointer (0);
        auto* right = stereoBuffer.getWritePointer (1);

        const auto currentDriveDb = driveDb.skip (numSamples);
        const auto currentDriveGain = juce::Decibels::decibelsToGain (currentDriveDb);
        const auto currentPreCutoff = preHpfCutoffHz.skip (numSamples);
        const auto currentPreQ = preHpfResonance.skip (numSamples);
        const auto currentPostCutoff = postLpfCutoffHz.skip (numSamples);
        const auto currentPostQ = postLpfResonance.skip (numSamples);

        updateFilterState (currentPreCutoff, currentPreQ, currentPostCutoff, currentPostQ);

        if (modeChanged.exchange (false, std::memory_order_relaxed))
            clearDynamicsState();

        const auto activeMode = mode;
        const auto dynamics = isDynamicsMode (activeMode);
        const auto saturation = isSaturationMode (activeMode);

        // No make-up anywhere in this stage. Drive is a raw gain into the
        // circuit and whatever comes out is the circuit's real level, so the
        // quiet models stay quiet and cranking Drive gets genuinely louder.
        // Output Level is the trim.

        for (int sample = 0; sample < numSamples; ++sample)
        {
            left[sample] = preHpf[0].processSample (0, left[sample] * currentDriveGain);
            right[sample] = preHpf[1].processSample (0, right[sample] * currentDriveGain);
        }

        if (activeMode != Mode::clean && oversampling != nullptr)
        {
            juce::dsp::AudioBlock<float> block (stereoBuffer);
            auto baseBlock = block.getSubBlock (0, static_cast<size_t> (numSamples));
            auto oversampledBlock = oversampling->processSamplesUp (baseBlock);

            const auto* curve = (dynamics || saturation) ? nullptr : &getCurves()[curveIndexFor (activeMode)];

            float peakInput = 0.0f;
            float peakOutput = 0.0f;

            for (size_t channel = 0; channel < oversampledBlock.getNumChannels(); ++channel)
            {
                auto* samples = oversampledBlock.getChannelPointer (channel);
                const auto channelIndex = juce::jmin (static_cast<int> (channel), 1);

                for (size_t sample = 0; sample < oversampledBlock.getNumSamples(); ++sample)
                {
                    const auto input = samples[sample];
                    float output = input;

                    switch (activeMode)
                    {
                        case Mode::tube:           output = triodes[static_cast<size_t> (channelIndex)].process (input); break;
                        case Mode::tape:           output = tapes[static_cast<size_t> (channelIndex)].process (input); break;
                        case Mode::optoCompressor: output = optoCompressors[static_cast<size_t> (channelIndex)].process (input); break;
                        case Mode::fetCompressor:  output = fetCompressors[static_cast<size_t> (channelIndex)].process (input); break;
                        case Mode::vcaLimiter:     output = vcaLimiters[static_cast<size_t> (channelIndex)].process (input); break;
                        default:                   output = curve->process (input); break;
                    }

                    samples[sample] = output;

                    if (dynamics)
                    {
                        peakInput = juce::jmax (peakInput, std::abs (input));
                        peakOutput = juce::jmax (peakOutput, std::abs (output));
                    }
                }
            }

            oversampling->processSamplesDown (baseBlock);

            if (dynamics)
            {
                const auto reduction = (peakInput > 1.0e-5f && peakOutput > 1.0e-6f)
                                     ? juce::jlimit (0.0f, 40.0f, juce::Decibels::gainToDecibels (peakInput / peakOutput))
                                     : 0.0f;
                gainReductionDb.store (reduction, std::memory_order_relaxed);
            }
            else
            {
                gainReductionDb.store (0.0f, std::memory_order_relaxed);
            }

            // The JFET stage is asymmetric and shifts its bias, so it needs the DC
            // blocker; tape and the dynamics units are symmetric and do not.
            const auto blockDc = activeMode == Mode::tube
                              || (curve != nullptr && curve->needsDcBlocker());

            // This pass exists only to strip the DC offset the asymmetric
            // circuits introduce, so skip it entirely otherwise.
            if (blockDc)
            {
                for (int channel = 0; channel < 2; ++channel)
                {
                    auto* samples = (channel == 0) ? left : right;

                    for (int sample = 0; sample < numSamples; ++sample)
                    {
                        const auto value = samples[sample];
                        const auto out = value - dcBlockerX1[static_cast<size_t> (channel)]
                                       + 0.9995f * dcBlockerY1[static_cast<size_t> (channel)];
                        dcBlockerX1[static_cast<size_t> (channel)] = value;
                        dcBlockerY1[static_cast<size_t> (channel)] = out;
                        samples[sample] = out;
                    }
                }
            }
        }
        else
        {
            gainReductionDb.store (0.0f, std::memory_order_relaxed);
        }

        for (int sample = 0; sample < numSamples; ++sample)
        {
            left[sample] = postLpf[0].processSample (0, left[sample]);
            right[sample] = postLpf[1].processSample (0, right[sample]);
        }
    }

private:
    using CircuitSpec = gas::circuits::CircuitSpec;
    using Topology = gas::circuits::Topology;
    using CircuitCurve = gas::circuits::CircuitCurve;

    /** The one remaining solved diode circuit: the Tube Screamer clipping stage.

        Gain comes from 1 + Rf/Rg (51k / 4k7 = 21.5 dB, the TS808 value). It is fed
        at guitar level (0 dBFS = 100 mV, kGuitarLevelVoltsPerFullScale) and its
        output is real volts (1 V = 0 dBFS), so that gain is what lifts guitar
        level to line level and the diode knee lands around -6 dBFS. */
    static const std::array<CircuitSpec, numClipperCurves>& getSpecs()
    {
        using namespace gas::circuits;

        static const auto specs = []
        {
            std::array<CircuitSpec, numClipperCurves> table
            { {
                { Topology::feedback, 51.0e3f, 4.7e3f, 0.0f, kDiode1N4148, 1, kDiode1N4148, 1 },
            } };

            for (auto& spec : table)
            {
                spec.inputVoltsPerFullScale  = kGuitarLevelVoltsPerFullScale;
                spec.outputVoltsPerFullScale = kLineLevelVoltsPerFullScale;
            }

            return table;
        }();

        return specs;
    }

    static const std::array<CircuitCurve, numClipperCurves>& getCurves()
    {
        static std::array<CircuitCurve, numClipperCurves> curves;
        static std::once_flag builtFlag;

        std::call_once (builtFlag, []
        {
            const auto& specs = getSpecs();

            for (size_t index = 0; index < curves.size(); ++index)
                curves[index].build (specs[index]);
        });

        return curves;
    }

    static size_t curveIndexFor (Mode mode) noexcept
    {
        juce::ignoreUnused (mode);
        return 0;   // Tube Screamer is the only solved curve
    }

    void clearDynamicsState()
    {
        for (auto& compressor : optoCompressors)
            compressor.reset();

        for (auto& compressor : fetCompressors)
            compressor.reset();

        for (auto& limiter : vcaLimiters)
            limiter.reset();

        for (auto& triode : triodes)
            triode.reset();

        for (auto& tape : tapes)
            tape.reset();

        dcBlockerX1 = { { 0.0f, 0.0f } };
        dcBlockerY1 = { { 0.0f, 0.0f } };
    }

    void updateFilterState (float preCutoff, float preQ, float postCutoff, float postQ)
    {
        const auto clampedPreCutoff = juce::jlimit (1.0f,
                                                    static_cast<float> (0.45 * currentSampleRate),
                                                    preCutoff);
        const auto clampedPostCutoff = juce::jlimit (200.0f, static_cast<float> (0.45 * currentSampleRate), postCutoff);
        const auto clampedPreQ = juce::jlimit (0.25f, 8.0f, preQ);
        const auto clampedPostQ = juce::jlimit (0.25f, 8.0f, postQ);

        for (auto& filter : preHpf)
        {
            filter.setCutoffFrequency (clampedPreCutoff);
            filter.setResonance (clampedPreQ);
        }

        for (auto& filter : postLpf)
        {
            filter.setCutoffFrequency (clampedPostCutoff);
            filter.setResonance (clampedPostQ);
        }
    }

    double currentSampleRate = 44100.0;
    Mode mode = Mode::clean;
    std::atomic<bool> modeChanged { false };
    std::atomic<float> gainReductionDb { 0.0f };

    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> driveDb;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> preHpfCutoffHz;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> preHpfResonance;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> postLpfCutoffHz;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> postLpfResonance;

    std::array<juce::dsp::StateVariableTPTFilter<float>, 2> preHpf;
    std::array<juce::dsp::StateVariableTPTFilter<float>, 2> postLpf;
    std::array<gas::dynamics::OptoCompressor, 2> optoCompressors;
    std::array<gas::dynamics::FetCompressor, 2> fetCompressors;
    std::array<gas::dynamics::VcaLimiter, 2> vcaLimiters;
    std::array<gas::saturation::JfetTubeStage, 2> triodes;
    std::array<gas::saturation::TapeDiffPairStage, 2> tapes;

    std::array<float, 2> dcBlockerX1 { { 0.0f, 0.0f } };
    std::array<float, 2> dcBlockerY1 { { 0.0f, 0.0f } };
    std::unique_ptr<juce::dsp::Oversampling<float>> oversampling;
};
