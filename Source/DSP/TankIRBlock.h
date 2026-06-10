#pragma once

#include <JuceHeader.h>

class TankIRBlock
{
public:
    void prepare (double sampleRate, int maximumBlockSize)
    {
        currentSampleRate = sampleRate;

        juce::dsp::ProcessSpec spec;
        spec.sampleRate = sampleRate;
        spec.maximumBlockSize = static_cast<juce::uint32> (maximumBlockSize);
        spec.numChannels = 1;

        convolution.prepare (spec);
        convolution.reset();
    }

    void reset()
    {
        convolution.reset();
    }

    void process (juce::AudioBuffer<float>& monoBuffer, int numSamples)
    {
        juce::dsp::AudioBlock<float> block (monoBuffer);
        auto subBlock = block.getSubBlock (0, static_cast<size_t> (numSamples));
        juce::dsp::ProcessContextReplacing<float> context (subBlock);
        convolution.process (context);
    }

    bool loadImpulseResponse (const juce::File& file)
    {
        if (! file.existsAsFile())
            return false;

        convolution.loadImpulseResponse (file,
                                         juce::dsp::Convolution::Stereo::no,
                                         juce::dsp::Convolution::Trim::yes,
                                         0,
                                         juce::dsp::Convolution::Normalise::yes);

        loadedPath = file.getFullPathName();
        return true;
    }

    bool loadImpulseResponse (juce::AudioBuffer<float>&& buffer, double sampleRate)
    {
        convolution.loadImpulseResponse (std::move (buffer),
                                         sampleRate,
                                         juce::dsp::Convolution::Stereo::no,
                                         juce::dsp::Convolution::Trim::yes,
                                         juce::dsp::Convolution::Normalise::yes);

        loadedPath.clear();
        return true;
    }

    const juce::String& getLoadedPath() const
    {
        return loadedPath;
    }

private:
    juce::dsp::Convolution convolution;
    double currentSampleRate = 44100.0;
    juce::String loadedPath;
};
