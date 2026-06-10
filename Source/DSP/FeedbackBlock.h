#pragma once

#include <JuceHeader.h>

class FeedbackBlock
{
public:
    void prepare (double sampleRate, int maximumBlockSize)
    {
        feedbackAmount.reset (sampleRate, 0.05);
        feedbackAmount.setCurrentAndTargetValue (0.0f);
        lastLeftSample = 0.0f;
        lastRightSample = 0.0f;

        juce::dsp::ProcessSpec monoSpec;
        monoSpec.sampleRate = sampleRate;
        monoSpec.maximumBlockSize = static_cast<juce::uint32> (juce::jmax (1, maximumBlockSize));
        monoSpec.numChannels = 1;

        feedbackPredelayLeft.prepare (monoSpec);
        feedbackPredelayRight.prepare (monoSpec);
    }

    void reset()
    {
        feedbackAmount.setCurrentAndTargetValue (feedbackAmount.getTargetValue());
        lastLeftSample = 0.0f;
        lastRightSample = 0.0f;
        feedbackPredelayLeft.reset();
        feedbackPredelayRight.reset();
    }

    void setFeedbackAmount (float normalizedAmount)
    {
        feedbackAmount.setTargetValue (juce::jlimit (0.0f, 1.0f, normalizedAmount));
    }

    void setFeedbackPhaseInverted (bool shouldInvert)
    {
        feedbackPhase = shouldInvert ? -1.0f : 1.0f;
    }

    void process (const juce::AudioBuffer<float>& inputWet,
                  juce::AudioBuffer<float>& outputWet,
                  juce::AudioBuffer<float>& feedbackReturn,
                  const float* predelaySamplesPerSample,
                  int numSamples)
    {
        outputWet.copyFrom (0, 0, inputWet, 0, 0, numSamples);
        outputWet.copyFrom (1, 0, inputWet, 1, 0, numSamples);

        auto* feedbackLeft = feedbackReturn.getWritePointer (0);
        auto* feedbackRight = feedbackReturn.getWritePointer (1);
        const auto* wetLeft = inputWet.getReadPointer (0);
        const auto* wetRight = inputWet.getReadPointer (1);

        auto delayedLeft = lastLeftSample;
        auto delayedRight = lastRightSample;

        for (int sample = 0; sample < numSamples; ++sample)
        {
            feedbackPredelayLeft.pushSample (0, delayedLeft);
            feedbackPredelayRight.pushSample (0, delayedRight);

            const auto amount = feedbackAmount.getNextValue();
            const auto predelaySamples = predelaySamplesPerSample != nullptr ? juce::jmax (0.0f, predelaySamplesPerSample[sample]) : 0.0f;
            feedbackLeft[sample] = feedbackPredelayLeft.popSample (0, predelaySamples) * amount * feedbackPhase;
            feedbackRight[sample] = feedbackPredelayRight.popSample (0, predelaySamples) * amount * feedbackPhase;

            delayedLeft = wetLeft[sample];
            delayedRight = wetRight[sample];
        }

        lastLeftSample = delayedLeft;
        lastRightSample = delayedRight;
    }

private:
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> feedbackAmount;
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear> feedbackPredelayLeft { 16384 };
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear> feedbackPredelayRight { 16384 };
    float lastLeftSample = 0.0f;
    float lastRightSample = 0.0f;
    float feedbackPhase = 1.0f;
};
