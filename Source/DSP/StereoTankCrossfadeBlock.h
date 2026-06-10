#pragma once

#include <JuceHeader.h>

class StereoTankCrossfadeBlock
{
public:
    void prepare (double sampleRate, int)
    {
        crossfade.reset (sampleRate, 0.02);
        crossfade.setCurrentAndTargetValue (0.0f);
    }

    void reset()
    {
        crossfade.setCurrentAndTargetValue (crossfade.getTargetValue());
    }

    void setCrossfadeAmount (float newAmountNormalized)
    {
        crossfade.setTargetValue (juce::jlimit (0.0f, 1.0f, newAmountNormalized));
    }

    void process (juce::AudioBuffer<float>& stereoBuffer, int numSamples)
    {
        auto* left = stereoBuffer.getWritePointer (0);
        auto* right = stereoBuffer.getWritePointer (1);

        for (int sample = 0; sample < numSamples; ++sample)
        {
            const auto amount = crossfade.getNextValue();
            const auto leftIn = left[sample];
            const auto rightIn = right[sample];

            const auto ownAmount = 1.0f - amount;
            left[sample] = (leftIn * ownAmount) + (rightIn * amount);
            right[sample] = (rightIn * ownAmount) + (leftIn * amount);
        }
    }

private:
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> crossfade;
};
