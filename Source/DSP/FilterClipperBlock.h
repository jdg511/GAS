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
        float threshold = 1.0f;
        float knee = 1.0f;
        float leakage = 0.0f;
    };

    static ModeTuning getModeTuning (Mode mode)
    {
        switch (mode)
        {
            case Mode::clean:      return { 1.0f, 1.0f, 0.0f };
            case Mode::silicon:    return { 0.65f * juce::Decibels::decibelsToGain (-12.0f), 1.85f, 0.0f };
            case Mode::led:        return { 1.05f * juce::Decibels::decibelsToGain (-9.0f), 1.20f, 0.0f };
            case Mode::germanium:  return { 0.78f * juce::Decibels::decibelsToGain (-12.0f), 0.95f, 0.06f };
        }

        return {};
    }

    static float applyTransferFunction (float inputSample, const ModeTuning& tuning)
    {
        const auto scaled = inputSample / juce::jmax (0.05f, tuning.threshold);
        const auto softClipped = std::tanh (scaled * tuning.knee) * tuning.threshold;
        const auto leakageComponent = tuning.leakage * std::tanh ((inputSample + 0.03f) * 0.75f);
        return softClipped + leakageComponent;
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
    std::unique_ptr<juce::dsp::Oversampling<float>> oversampling;
};
