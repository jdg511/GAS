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

    /** The three-position source switch (Rev C). */
    enum class StereoMode
    {
        stereo = 0,       // L and R each run their own path, feedback stays in its channel
        monoToStereo,     // a mono source is copied to both channels, then as Stereo
        megaverb          // feedback crosses over: L path -> R path -> L path ...
    };

    using Dynamics = DirtDynamicsBlock::Dynamics;

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
    StereoMode getStereoMode() const;
    bool shouldConvertMonoSourceToStereo() const;
    bool isMegaverbEngaged() const;
    bool shouldShowUnavailableTankControls() const;
    bool isInputTubeEngaged() const;
    bool isOutputTapeEngaged() const;
    bool isDirtEngaged() const;
    Dynamics getDynamics() const;
    juce::String getSignalChainDescription() const;

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

    // Plugin-only trims (not on the PCB)
    static constexpr auto preInputLevelParameterID = "preInputLevel";
    static constexpr auto postOutputLevelParameterID = "postOutputLevel";
    // Board controls
    static constexpr auto inputLevelParameterID = "inputLevel";          // "Vol", pull for Tube
    static constexpr auto inputTubeParameterID = "inputTube";
    static constexpr auto gainParameterID = "gain";                      // "Gain", pull for Dirt
    static constexpr auto dirtParameterID = "dirt";
    static constexpr auto dynamicsParameterID = "fbDynamics";            // Comp / Off / Limit
    static constexpr auto outputTapeParameterID = "outputTape";          // Output knob, pull for Tape
    static constexpr auto stereoModeParameterID = "stereoMode";          // Stereo / Mono > Stereo / MEGAVERB
    static constexpr auto preHpfCutoffParameterID = "preHpfCutoff";
    static constexpr auto postLpfCutoffParameterID = "postLpfCutoff";
    static constexpr auto x2TanksParameterID = "x2Tanks";
    static constexpr auto extTankMixParameterID = "extTankMix";
    static constexpr auto feedbackAmountParameterID = "feedbackAmount";
    static constexpr auto feedbackPhaseInvertParameterID = "feedbackPhaseInvert";
    static constexpr auto wetDryParameterID = "wetDry";
    static constexpr auto outputLevelParameterID = "outputLevel";
    static constexpr auto showUnavailableTankControlsParameterID = "showUnavailableTankControls";

    // Every level knob in Rev C (Pre Input, Vol, Gain, Output, Post Output) is
    // the same -18 .. +18 dB pot stage. sanitizeBuffer() still hard-clamps at
    // +-sanitizeClampGain (+12 dBFS, the +/-15 V rails).
    static constexpr float levelMinDb = -18.0f;
    static constexpr float levelMaxDb = 18.0f;

    /** Absolute sample ceiling applied by sanitizeBuffer(), as linear gain.
        3.9811f is +12 dBFS (was 8.0f, about +18 dBFS, before 2026-09-12). */
    static constexpr float sanitizeClampGain = 3.9811f;

    /** Fixed Q for the circuit's pre-HPF and post-LPF: 1/sqrt(2), a Butterworth
        response. The Q knobs were removed 2026-09-12. */
    static constexpr float filterQ = 0.70710678f;

    /** Floor of the level meters. Anything quieter reads as empty. */
    static constexpr float meterFloorDb = -48.0f;

    /** Peak level in dBFS at the three metering points (plugin only, none on
        the PCB). Input: straight after the Vol (Solid State / Tube) knob on the
        wet path. Wet: straight after the Gain / Dirt / Comp-Limit circuit, just
        before the signal heads down the feedback path. Output: the absolute
        last thing before audio leaves the plugin. */
    float getInputMeterDb() const noexcept
    {
        return juce::Decibels::gainToDecibels (inputMeterPeak.load (std::memory_order_relaxed), meterFloorDb);
    }

    float getWetMeterDb() const noexcept
    {
        return juce::Decibels::gainToDecibels (wetMeterPeak.load (std::memory_order_relaxed), meterFloorDb);
    }

    /** Gain reduction of the Comp / Limit circuit in dB (0 when Off). */
    float getGainReductionDb() const noexcept { return chain.dirtDynamics.getGainReductionDb(); }

    float getOutputMeterDb() const noexcept
    {
        return juce::Decibels::gainToDecibels (outputMeterPeak.load (std::memory_order_relaxed), meterFloorDb);
    }


    void setParameterPlainValue (const juce::String& parameterID, float plainValue);

    bool loadPreset (int presetIndex);
    juce::StringArray getPresetNames() const;
    bool saveUserPreset (const juce::String& presetName);

private:
    juce::ValueTree createStateTree();
    void migrateLegacyState (juce::ValueTree& restoredState);
    void resetLevelSmoothers();
    bool applyPresetState (juce::ValueTree restoredState, const juce::String& presetName);
    juce::File getUserPresetDirectory() const;
    juce::Array<juce::File> getUserPresetFiles() const;
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
    static void applySmoothedGain (juce::AudioBuffer<float>& target,
                                   juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear>& smoothedGain,
                                   int numSamples);
    void applySecondaryTankPredelay (juce::AudioBuffer<float>& monoBuffer,
                                       juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& delayLine,
                                       const float* delaySamplesPerSample,
                                       int numSamples);
    DirtDynamicsBlock::Parameters getDirtDynamicsParameters() const;

    static Ir2RoutingMode toIr2RoutingMode (float parameterValue);
    static StereoMode toStereoMode (float parameterValue);
    static Dynamics toDynamics (float parameterValue);

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
    // Four independent predelay lanes, each wandering within its own range.
    // In the simulation, predelay + convolution act as the spring-tank model:
    //   0 = primary L, 1 = primary R   -> hardware target: 4AB1C1B / 4AB1C1B
    //   2 = 2nd-tank L, 3 = 2nd-tank R -> hardware target: 9EB2C1B / 9EB3C1B
    std::array<juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear>, 4> predelayMsSmoothed;
    std::array<float, 4> predelayTargetMs { { 25.0f, 25.0f, 36.0f, 36.0f } };
    juce::Random predelayRandom;
    // Input and output trims, smoothed on the audio thread so knob moves and
    // host automation never step the gain and click.
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> preInputGainSmoothed { 1.0f };
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> inputGainSmoothed { 1.0f };
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> outputGainSmoothed { 1.0f };
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> postOutputGainSmoothed { 1.0f };

    // Metering taps, written on the audio thread and polled by the editor.
    std::atomic<float> inputMeterPeak { 0.0f };
    std::atomic<float> wetMeterPeak { 0.0f };
    std::atomic<float> outputMeterPeak { 0.0f };
    Ir2RoutingMode lastIr2RoutingMode = Ir2RoutingMode::off;
    StereoMode lastStereoMode = StereoMode::stereo;
    std::atomic<bool> lastMonoSourceWithoutStereoConversion { false };
    bool playbackActive = false;
    bool isPrepared = false;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TheGreatAmericanSpringAudioProcessor)
};
