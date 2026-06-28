#pragma once

#include <JuceHeader.h>

#include <array>

class FilterClipperBlock
{
public:
    enum class Mode
    {
        clean = 0,
        silicon,
        led,
        germanium
    };

    struct Parameters
    {
        Mode mode = Mode::clean;
        float driveDb = 6.0f;
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

        driveDb.setCurrentAndTargetValue (6.0f);
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

        dcBlockerX1 = { { 0.0f, 0.0f } };
        dcBlockerY1 = { { 0.0f, 0.0f } };
    }

    void setParameters (const Parameters& newParameters)
    {
        mode = newParameters.mode;
        driveDb.setTargetValue (newParameters.driveDb);
        preHpfCutoffHz.setTargetValue (newParameters.preHpfCutoffHz);
        preHpfResonance.setTargetValue (newParameters.preHpfResonance);
        postLpfCutoffHz.setTargetValue (newParameters.postLpfCutoffHz);
        postLpfResonance.setTargetValue (newParameters.postLpfResonance);
    }

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

        for (int sample = 0; sample < numSamples; ++sample)
        {
            left[sample] = preHpf[0].processSample (0, left[sample] * currentDriveGain);
            right[sample] = preHpf[1].processSample (0, right[sample] * currentDriveGain);
        }

        if (mode != Mode::clean && oversampling != nullptr)
        {
            juce::dsp::AudioBlock<float> block (stereoBuffer);
            auto baseBlock = block.getSubBlock (0, static_cast<size_t> (numSamples));
            auto oversampledBlock = oversampling->processSamplesUp (baseBlock);
            const auto tuning = getModeTuning (mode);

            for (size_t channel = 0; channel < oversampledBlock.getNumChannels(); ++channel)
            {
                auto* samples = oversampledBlock.getChannelPointer (channel);

                for (size_t sample = 0; sample < oversampledBlock.getNumSamples(); ++sample)
                    samples[sample] = applyTransferFunction (samples[sample], tuning);
            }

            oversampling->processSamplesDown (baseBlock);

            // Static makeup gain + DC blocker (asymmetric modes only), base rate.
            for (int channel = 0; channel < 2; ++channel)
            {
                auto* samples = (channel == 0) ? left : right;

                for (int sample = 0; sample < numSamples; ++sample)
                {
                    auto value = samples[sample] * tuning.makeup;

                    if (tuning.blockDc)
                    {
                        const auto out = value - dcBlockerX1[channel] + 0.9995f * dcBlockerY1[channel];
                        dcBlockerX1[channel] = value;
                        dcBlockerY1[channel] = out;
                        value = out;
                    }

                    samples[sample] = value;
                }
            }
        }

        for (int sample = 0; sample < numSamples; ++sample)
        {
            left[sample] = postLpf[0].processSample (0, left[sample]);
            right[sample] = postLpf[1].processSample (0, right[sample]);
        }
    }

private:
    struct ModeTuning
    {
        // Per-diode model.
        //  thresholdPos/Neg : forward-voltage clip points (normalised). Unequal
        //                     values = asymmetric clipping -> even harmonics.
        //  knee             : transition sharpness (higher = harder/sharper).
        //  bleed            : feedback-loop passthrough that keeps the curve
        //                     rising so it never fully flattens (op-amp feedback
        //                     topologies). 0 for shunt-to-ground.
        //  makeup           : static output gain so the quieter modes land near
        //                     LED's loudness (LED is the loudest reference).
        //  blockDc          : remove the DC offset that asymmetric clipping adds.
        float thresholdPos = 1.0f;
        float thresholdNeg = 1.0f;
        float knee = 1.0f;
        float bleed = 0.0f;
        float makeup = 1.0f;
        bool  blockDc = false;
    };

    static ModeTuning getModeTuning (Mode mode)
    {
        switch (mode)
        {
            // Germanium: asymmetric shunt-to-ground (2 diodes up / 1 down).
            // Lowest Vf, soft Ge knee; unequal halves -> strong even harmonics.
            // Shunt topology => no bleed; DC-block the asymmetric offset.
            case Mode::germanium:  return { 0.60f, 0.30f, 2.5f, 0.00f, 1.8f, true };

            // Silicon: anti-parallel diodes in the op-amp feedback loop (TS-style).
            // Mid Vf, softest knee, generous bleed => smooth, dynamic, never
            // fully saturates.
            case Mode::silicon:    return { 0.70f, 0.70f, 1.5f, 0.12f, 1.4f, false };

            // LED: high-Vf clipping in a feedback loop (Bluesbreaker / OCD).
            // Clips loud and late with the sharpest knee => open but hard crunch.
            // Loudest mode => reference level, no makeup.
            case Mode::led:        return { 1.70f, 1.70f, 5.0f, 0.06f, 1.0f, false };

            case Mode::clean:
            default:               return { 1.0f, 1.0f, 1.0f, 0.0f, 1.0f, false };
        }
    }

    static float applyTransferFunction (float x, const ModeTuning& tuning)
    {
        const auto threshold = (x >= 0.0f) ? tuning.thresholdPos : tuning.thresholdNeg;
        const auto a = std::abs (x) / juce::jmax (0.05f, threshold);
        // Soft-knee saturator that asymptotes to +/-threshold; knee sets hardness.
        const auto clipped = x / std::pow (1.0f + std::pow (a, tuning.knee), 1.0f / tuning.knee);
        return clipped + tuning.bleed * x;
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
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> driveDb;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> preHpfCutoffHz;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> preHpfResonance;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> postLpfCutoffHz;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> postLpfResonance;
    std::array<juce::dsp::StateVariableTPTFilter<float>, 2> preHpf;
    std::array<juce::dsp::StateVariableTPTFilter<float>, 2> postLpf;
    std::array<float, 2> dcBlockerX1 { { 0.0f, 0.0f } };
    std::array<float, 2> dcBlockerY1 { { 0.0f, 0.0f } };
    std::unique_ptr<juce::dsp::Oversampling<float>> oversampling;
};
