
#pragma once

#include <JuceHeader.h>

#include "DynamicsModels.h"

/** One board node running out of op-amp rail, oversampled.

    Clipping is a nonlinearity, and a nonlinearity makes harmonics. At the base sample
    rate the ones above Nyquist have nowhere to go and fold back down into the audio
    band as aliasing, which is a sound the real circuit cannot make: hardware harmonics
    just carry on up and roll off. Running the saturation at a multiple of the sample
    rate moves those harmonics above the audio band before the downsampling filter
    removes them, so what is left is the harmonic content the board would actually
    produce.

    4x is the default and matches the oversampling the tube, tape and Tube Screamer
    stages already use. The factor is exposed so it can be traded against CPU.
*/
class RailSaturator
{
public:
    /** Oversampling factors offered to the user, in parameter order. */
    static constexpr int factorOrderForChoice (int choiceIndex) noexcept
    {
        // 0 = Off (1x), 1 = 2x, 2 = 4x, 3 = 8x. The order is the power of two.
        // Clamped by hand because juce::jlimit is not constexpr in this JUCE version.
        return choiceIndex < 0 ? 0 : (choiceIndex > 3 ? 3 : choiceIndex);
    }

    static constexpr int defaultChoiceIndex = 2;   // 4x

    void prepare (double sampleRate, int maximumBlockSize, int numChannels, int factorOrder)
    {
        juce::ignoreUnused (sampleRate);

        channels = juce::jmax (1, numChannels);
        order = juce::jlimit (0, 3, factorOrder);

        if (order == 0)
        {
            // Off: the curve is applied in place, so there is nothing to build and no
            // latency to account for.
            oversampling.reset();
            return;
        }

        // useIntegerLatency: JUCE adds its own fractional trim so the reported delay is
        // a whole number of samples. That keeps the host's compensation exact and lets
        // other stages match it with a plain delay line instead of an interpolator.
        oversampling = std::make_unique<juce::dsp::Oversampling<float>> (
            static_cast<size_t> (channels),
            static_cast<size_t> (order),
            juce::dsp::Oversampling<float>::filterHalfBandPolyphaseIIR,
            true,
            true);

        oversampling->initProcessing (static_cast<size_t> (juce::jmax (1, maximumBlockSize)));
        oversampling->reset();
    }

    void reset()
    {
        if (oversampling != nullptr)
            oversampling->reset();
    }

    /** Samples of delay this node adds. Zero when oversampling is off. */
    float getLatencyInSamples() const
    {
        return oversampling != nullptr ? oversampling->getLatencyInSamples() : 0.0f;
    }

    int getFactorOrder() const noexcept { return order; }

    /** Applies the rail curve to the first `channels` channels of `buffer`. */
    void process (juce::AudioBuffer<float>& buffer, int numSamples, float rail)
    {
        const auto usable = juce::jmin (channels, buffer.getNumChannels());

        if (usable <= 0 || numSamples <= 0)
            return;

        if (oversampling == nullptr)
        {
            for (int channel = 0; channel < usable; ++channel)
            {
                auto* samples = buffer.getWritePointer (channel);

                for (int sample = 0; sample < numSamples; ++sample)
                    samples[sample] = gas::dynamics::saturateAtRail (samples[sample], rail);
            }

            return;
        }

        // The oversampler was built for exactly `channels` channels, so hand it that
        // many and no more.
        juce::dsp::AudioBlock<float> block (buffer.getArrayOfWritePointers(),
                                            static_cast<size_t> (usable),
                                            size_t (0),
                                            static_cast<size_t> (numSamples));

        auto upsampled = oversampling->processSamplesUp (block);

        for (size_t channel = 0; channel < upsampled.getNumChannels(); ++channel)
        {
            auto* samples = upsampled.getChannelPointer (channel);

            for (size_t sample = 0; sample < upsampled.getNumSamples(); ++sample)
                samples[sample] = gas::dynamics::saturateAtRail (samples[sample], rail);
        }

        oversampling->processSamplesDown (block);
    }

private:
    std::unique_ptr<juce::dsp::Oversampling<float>> oversampling;
    int channels = 2;
    int order = 2;
};
