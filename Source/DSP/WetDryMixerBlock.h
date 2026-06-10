#pragma once

#include <JuceHeader.h>

class WetDryMixerBlock
{
public:
    void prepare (double sampleRate, int)
    {
        mix.reset (sampleRate, 0.02);
        mix.setCurrentAndTargetValue (1.0f);
    }

    void reset()
    {
        mix.setCurrentAndTargetValue (mix.getTargetValue());
    }

    void setWetAmount (float normalizedWet)
    {
        mix.setTargetValue (juce::jlimit (0.0f, 1.0f, normalizedWet));
    }

    void process (const juce::AudioBuffer<float>& dryInput,
                  const juce::AudioBuffer<float>& wetInput,
                  juce::AudioBuffer<float>& output,
                  int numSamples)
    {
        auto* outLeft = output.getWritePointer (0);
        auto* outRight = output.getNumChannels() > 1 ? output.getWritePointer (1) : nullptr;
        const auto* dryLeft = dryInput.getReadPointer (0);
        const auto* dryRight = dryInput.getReadPointer (1);
        const auto* wetLeft = wetInput.getReadPointer (0);
        const auto* wetRight = wetInput.getReadPointer (1);

        for (int sample = 0; sample < numSamples; ++sample)
        {
            const auto wet = mix.getNextValue();
            const auto dry = 1.0f - wet;
            outLeft[sample] = (dryLeft[sample] * dry) + (wetLeft[sample] * wet);

            if (outRight != nullptr)
                outRight[sample] = (dryRight[sample] * dry) + (wetRight[sample] * wet);
        }
    }

private:
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> mix;
};
