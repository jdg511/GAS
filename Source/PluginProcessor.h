#pragma once

#include <atomic>

#include <JuceHeader.h>

#include <array>

#include "DSP/ModularFxChain.h"

class TheGreatAmericanSpringAudioProcessor final : public juce::AudioProcessor,
                                                    public juce::ChangeBroadcaster
{
public:
    enum class TankSlot
    {
        left1 = 0,
        right1,
        left2,
        right2
    };

    enum class Ir2RoutingMode
    {
        off = 0,
        series,
        parallel
    };

    TheGreatAmericanSpringAudioProcessor();
    ~TheGreatAmericanSpringAudioProcessor() override;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void reset() override;
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    using AudioProcessor::processBlock;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    const juce::String getName() const override;
    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram (int index) override;
    const juce::String getProgramName (int index) override;
    void changeProgramName (int index, const juce::String& newName) override;

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

    bool loadTankImpulseResponseFile (TankSlot slot, const juce::File& file);
    juce::String getTankImpulseResponseDisplayName (TankSlot slot) const;
    juce::String getTankSlotName (TankSlot slot) const;
    juce::File getSpringIrDirectory() const;
    bool isX2Enabled() const;
    Ir2RoutingMode getIr2RoutingMode() const;
    juce::String getIr2RoutingDisplayName() const;
    bool isFeedbackPhaseInverted() const;
    bool shouldConvertMonoSourceToStereo() const;
    bool shouldShowUnavailableTankControls() const;
    bool isCrossfadeAvailableForCurrentLayout() const;

    static constexpr auto inputModeParameterID = "inputMode";

    enum class InputMode { stereo = 0, monoL, monoR };
    InputMode getInputMode() const;

    bool loadPlaybackFile (const juce::File& file);
    void setPlaybackActive (bool shouldPlay);
    bool isPlaybackActive() const;
    bool hasPlaybackFile() const;
    juce::StringArray getPlaybackSourceDisplayNames() const;
    int getSelectedPlaybackSourceIndex() const;
    bool setPlaybackSourceIndex (int index);
    juce::String getPlaybackFileDisplayName() const;

    juce::AudioProcessorValueTreeState parameters;

    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    static constexpr auto crossfadeAmountParameterID = "crossfadeAmount";
    static constexpr auto modeParameterID = "mode";
    static constexpr auto driveParameterID = "drive";
    static constexpr auto preHpfCutoffParameterID = "preHpfCutoff";
    static constexpr auto preHpfResonanceParameterID = "preHpfResonance";
    static constexpr auto postLpfCutoffParameterID = "postLpfCutoff";
    static constexpr auto postLpfResonanceParameterID = "postLpfResonance";
    static constexpr auto x2TanksParameterID = "x2Tanks";
    static constexpr auto extTankMixParameterID = "extTankMix";
    static constexpr auto feedbackAmountParameterID = "feedbackAmount";
    static constexpr auto feedbackPhaseInvertParameterID = "feedbackPhaseInvert";
    static constexpr auto wetDryParameterID = "wetDry";
    static constexpr auto monoSourceToStereoParameterID = "monoSourceToStereo";
    static constexpr auto showUnavailableTankControlsParameterID = "showUnavailableTankControls";

    void setParameterPlainValue (const juce::String& parameterID, float plainValue);

    void loadPreset (int presetIndex);
    static juce::StringArray getPresetNames();

private:
    juce::File getCurrentModuleBinaryFile() const;
    juce::Array<juce::File> getSpringIrSearchDirectories() const;
    juce::File resolveSpringIrFile (const juce::String& storedPath) const;
    juce::Array<juce::File> getPlaybackSearchDirectories() const;
    juce::File resolvePlaybackFile (const juce::String& storedPath) const;
    void refreshAvailableSpringIRs();
    void assignRandomTankIRsIfNeeded();
    void applyDefaultGasSettings();
    void applyGasPresetSettings();
    void assignDefaultTankIRs();
    bool loadTankIRFromCurrentPath (TankSlot slot);
    void loadFallbackTankIR (TankSlot slot);
    static juce::String getTankIrPathPropertyName (TankSlot slot);
    juce::String& getTankIrPath (TankSlot slot);
    const juce::String& getTankIrPath (TankSlot slot) const;
    TankIRBlock& getTankBlock (TankSlot slot);
    const TankIRBlock& getTankBlock (TankSlot slot) const;

    void resizeProcessingBuffers (int samplesPerBlock);
    void loadPlaybackIntoBuffer (juce::AudioBuffer<float>& targetBuffer, int numSamples);
    void buildExternalInput (juce::AudioBuffer<float>& hostBuffer, int numSamples);
    bool loadPlaybackSourceFromMemory (const void* data, int dataSize, const juce::String& displayName);
    bool loadSelectedPlaybackSource();
    int getPlaybackSourceIndexForPath (const juce::String& sourcePath) const;
    bool isMonoSourceWithoutStereoConversion() const;
    bool detectMonoExternalInput (int numSamples) const;
    void updatePredelayModulation (int numSamples);
    void applyWetPredelay (int numSamples);
    void sanitizeBuffer (juce::AudioBuffer<float>& buffer, int numSamples) const;
    void applySecondaryTankPredelay (juce::AudioBuffer<float>& monoBuffer,
                                       juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& delayLine,
                                       const float* delaySamplesPerSample,
                                       int numSamples);
    FilterClipperBlock::Parameters getFilterClipperParameters() const;

    static FilterClipperBlock::Mode toFilterClipperMode (int modeIndex);
    static Ir2RoutingMode toIr2RoutingMode (float parameterValue);

    ModularFxChain chain;

    juce::AudioFormatManager audioFormatManager;
    juce::Array<juce::File> availableSpringIRs;

    juce::AudioBuffer<float> externalInputBuffer;
    juce::AudioBuffer<float> dryTapBuffer;
    juce::AudioBuffer<float> wetInputBaseBuffer;
    juce::AudioBuffer<float> wetStereoBuffer;
    juce::AudioBuffer<float> wetAfterFeedbackBuffer;
    juce::AudioBuffer<float> feedbackReturnBuffer;
    juce::AudioBuffer<float> predelayModulationBuffer;
    juce::AudioBuffer<float> monoLeftBuffer;
    juce::AudioBuffer<float> monoRightBuffer;
    juce::AudioBuffer<float> monoLeftSecondaryBuffer;
    juce::AudioBuffer<float> monoRightSecondaryBuffer;
    juce::AudioBuffer<float> playbackBuffer;

    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear> wetPredelayLeft { 16384 };
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear> wetPredelayRight { 16384 };
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear> secondaryLeftTankPredelay { 16384 };
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear> secondaryRightTankPredelay { 16384 };

    juce::String leftTank1IrPath;
    juce::String rightTank1IrPath;
    juce::String leftTank2IrPath;
    juce::String rightTank2IrPath;
    juce::String playbackFilePath;

    double currentSampleRate = 44100.0;
    double playbackSourceSampleRate = 44100.0;
    double playbackReadPosition = 0.0;
    double predelayLfoPhase = 0.0;
    int currentMaximumBlockSize = 512;
    // Four independent predelay lanes, each wandering within its own range:
    //   0 = primary L, 1 = primary R   (20-30 ms)
    //   2 = 2nd-tank L, 3 = 2nd-tank R (30-42 ms)
    std::array<juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear>, 4> predelayMsSmoothed;
    std::array<float, 4> predelayTargetMs { { 25.0f, 25.0f, 36.0f, 36.0f } };
    juce::Random predelayRandom;
    Ir2RoutingMode lastIr2RoutingMode = Ir2RoutingMode::off;
    std::atomic<bool> lastMonoSourceWithoutStereoConversion { false };
    bool playbackActive = false;
    bool isPrepared = false;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TheGreatAmericanSpringAudioProcessor)
};
