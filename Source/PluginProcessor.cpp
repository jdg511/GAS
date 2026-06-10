#include <BinaryData.h>

#include "PluginProcessor.h"
#include "PluginEditor.h"

#if JUCE_WINDOWS
 #include <windows.h>
#endif

#include <array>

namespace
{
constexpr auto projectSpringIrDirectoryPath = R"(C:\Users\Jason\source\repos\GAS\Spring IRs)";
constexpr double randomPredelayLfoFrequencyHz = 0.3;
constexpr double randomPredelayMinimumMilliseconds = 28.0;
constexpr double randomPredelayMaximumMilliseconds = 36.0;
constexpr double randomPredelaySmoothingSeconds = 1.25;
constexpr double secondaryLeftTankPredelayMilliseconds = 41.0;
constexpr double secondaryRightTankPredelayMilliseconds = 31.0;
constexpr float fallbackImpulse = 1.0f;
constexpr auto defaultLeftTank1IrFileName = "GBS-L.wav";
constexpr auto defaultRightTank1IrFileName = "GBS-R.wav";
constexpr auto defaultLeftTank2IrFileName = "GAS-L.wav";
constexpr auto defaultRightTank2IrFileName = "GAS-R.wav";

struct EmbeddedPlaybackSource
{
    const char* displayPath;
    const void* data;
    int dataSize;
};

const auto& getEmbeddedPlaybackSources()
{
    static const std::array<EmbeddedPlaybackSource, 3> sources {{
        { "Make Reverb Great Again-mono.mp3", BinaryData::Make_Reverb_Great_Againmono_mp3, BinaryData::Make_Reverb_Great_Againmono_mp3Size },
        { "Its a Shame-stereo.mp3", BinaryData::Its_a_Shamestereo_mp3, BinaryData::Its_a_Shamestereo_mp3Size },
        { "Zombie Remix-stereo.mp3", BinaryData::Zombie_Remixstereo_mp3, BinaryData::Zombie_Remixstereo_mp3Size }
    }};

    return sources;
}
}

TheGreatAmericanSpringAudioProcessor::TheGreatAmericanSpringAudioProcessor()
    : AudioProcessor (BusesProperties()
                        .withInput ("Input", juce::AudioChannelSet::stereo(), true)
                        .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      parameters (*this, nullptr, "Parameters", createParameterLayout())
{
    audioFormatManager.registerBasicFormats();
    refreshAvailableSpringIRs();
    applyDefaultGasSettings();
    playbackFilePath = getEmbeddedPlaybackSources().front().displayPath;
    playbackActive = false;
}

TheGreatAmericanSpringAudioProcessor::~TheGreatAmericanSpringAudioProcessor() = default;

const juce::String TheGreatAmericanSpringAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool TheGreatAmericanSpringAudioProcessor::acceptsMidi() const
{
    return false;
}

bool TheGreatAmericanSpringAudioProcessor::producesMidi() const
{
    return false;
}

bool TheGreatAmericanSpringAudioProcessor::isMidiEffect() const
{
    return false;
}

double TheGreatAmericanSpringAudioProcessor::getTailLengthSeconds() const
{
    return 8.0;
}

int TheGreatAmericanSpringAudioProcessor::getNumPrograms()
{
    return 1;
}

int TheGreatAmericanSpringAudioProcessor::getCurrentProgram()
{
    return 0;
}

void TheGreatAmericanSpringAudioProcessor::setCurrentProgram (int index)
{
    juce::ignoreUnused (index);
}

const juce::String TheGreatAmericanSpringAudioProcessor::getProgramName (int index)
{
    juce::ignoreUnused (index);
    return {};
}

void TheGreatAmericanSpringAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
    juce::ignoreUnused (index, newName);
}

void TheGreatAmericanSpringAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    currentSampleRate = sampleRate;
    currentMaximumBlockSize = juce::jmax (1, samplesPerBlock);
    wetPredelayTargetMilliseconds = juce::jmap (predelayRandom.nextFloat(),
                                                static_cast<float> (randomPredelayMinimumMilliseconds),
                                                static_cast<float> (randomPredelayMaximumMilliseconds));
    wetPredelayMillisecondsSmoothed.reset (currentSampleRate, randomPredelaySmoothingSeconds);
    wetPredelayMillisecondsSmoothed.setCurrentAndTargetValue (wetPredelayTargetMilliseconds);
    predelayLfoPhase = 0.0;
    wetPredelaySamples = wetPredelayTargetMilliseconds * 0.001f * static_cast<float> (currentSampleRate);
    secondaryLeftPredelaySamples = static_cast<float> (secondaryLeftTankPredelayMilliseconds * 0.001 * currentSampleRate);
    secondaryRightPredelaySamples = static_cast<float> (secondaryRightTankPredelayMilliseconds * 0.001 * currentSampleRate);

    resizeProcessingBuffers (currentMaximumBlockSize);

    juce::dsp::ProcessSpec monoSpec;
    monoSpec.sampleRate = sampleRate;
    monoSpec.maximumBlockSize = static_cast<juce::uint32> (currentMaximumBlockSize);
    monoSpec.numChannels = 1;

    wetPredelayLeft.prepare (monoSpec);
    wetPredelayRight.prepare (monoSpec);
    secondaryLeftTankPredelay.prepare (monoSpec);
    secondaryRightTankPredelay.prepare (monoSpec);
    secondaryLeftTankPredelay.setDelay (secondaryLeftPredelaySamples);
    secondaryRightTankPredelay.setDelay (secondaryRightPredelaySamples);

    chain.prepare (sampleRate, currentMaximumBlockSize);
    reset();

    loadTankIRFromCurrentPath (TankSlot::left1);
    loadTankIRFromCurrentPath (TankSlot::right1);
    loadTankIRFromCurrentPath (TankSlot::left2);
    loadTankIRFromCurrentPath (TankSlot::right2);

    loadSelectedPlaybackSource();

    isPrepared = true;
}

void TheGreatAmericanSpringAudioProcessor::releaseResources()
{
    isPrepared = false;
}

void TheGreatAmericanSpringAudioProcessor::reset()
{
    chain.reset();

    wetPredelayLeft.reset();
    wetPredelayRight.reset();
    wetPredelayMillisecondsSmoothed.setCurrentAndTargetValue (wetPredelayTargetMilliseconds);
    predelayLfoPhase = 0.0;
    secondaryLeftTankPredelay.reset();
    secondaryRightTankPredelay.reset();
    secondaryLeftTankPredelay.setDelay (secondaryLeftPredelaySamples);
    secondaryRightTankPredelay.setDelay (secondaryRightPredelaySamples);
    lastIr2RoutingMode = getIr2RoutingMode();

    externalInputBuffer.clear();
    dryTapBuffer.clear();
    wetInputBaseBuffer.clear();
    wetStereoBuffer.clear();
    wetAfterFeedbackBuffer.clear();
    feedbackReturnBuffer.clear();
    monoLeftBuffer.clear();
    monoRightBuffer.clear();
    monoLeftSecondaryBuffer.clear();
    monoRightSecondaryBuffer.clear();

    playbackReadPosition = 0.0;
}

bool TheGreatAmericanSpringAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    const auto input = layouts.getMainInputChannelSet();
    const auto output = layouts.getMainOutputChannelSet();

    return (input == juce::AudioChannelSet::mono() || input == juce::AudioChannelSet::stereo())
        && (output == juce::AudioChannelSet::mono() || output == juce::AudioChannelSet::stereo());
}

void TheGreatAmericanSpringAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer,
                                                           juce::MidiBuffer& midiMessages)
{
    juce::ignoreUnused (midiMessages);
    juce::ScopedNoDenormals noDenormals;

    const auto numSamples = buffer.getNumSamples();
    jassert (numSamples <= currentMaximumBlockSize);

    for (auto channel = getTotalNumInputChannels(); channel < getTotalNumOutputChannels(); ++channel)
        buffer.clear (channel, 0, numSamples);

    buildExternalInput (buffer, numSamples);
    const auto forceMonoLeftOnly = isMonoSourceWithoutStereoConversion();

    dryTapBuffer.copyFrom (0, 0, externalInputBuffer, 0, 0, numSamples);
    dryTapBuffer.copyFrom (1, 0, externalInputBuffer, 1, 0, numSamples);

    wetInputBaseBuffer.copyFrom (0, 0, externalInputBuffer, 0, 0, numSamples);
    wetInputBaseBuffer.copyFrom (1, 0, externalInputBuffer, 1, 0, numSamples);

    wetInputBaseBuffer.addFrom (0, 0, feedbackReturnBuffer, 0, 0, numSamples);
    wetInputBaseBuffer.addFrom (1, 0, feedbackReturnBuffer, 1, 0, numSamples);

    updatePredelayModulation (numSamples);
    applyWetPredelay (numSamples);

    monoLeftBuffer.copyFrom (0, 0, wetStereoBuffer, 0, 0, numSamples);
    monoRightBuffer.copyFrom (0, 0, wetStereoBuffer, 1, 0, numSamples);

    const auto ir2RoutingMode = getIr2RoutingMode();
    const auto ir2Series = ir2RoutingMode == Ir2RoutingMode::series;
    const auto ir2Parallel = ir2RoutingMode == Ir2RoutingMode::parallel;
    const auto extTankMix = parameters.getRawParameterValue (extTankMixParameterID)->load();

    if (ir2RoutingMode != lastIr2RoutingMode)
    {
        secondaryLeftTankPredelay.reset();
        secondaryRightTankPredelay.reset();
        monoLeftSecondaryBuffer.clear();
        monoRightSecondaryBuffer.clear();
        lastIr2RoutingMode = ir2RoutingMode;
    }

    if (ir2Parallel)
    {
        monoLeftSecondaryBuffer.copyFrom (0, 0, wetStereoBuffer, 0, 0, numSamples);
        monoRightSecondaryBuffer.copyFrom (0, 0, wetStereoBuffer, 1, 0, numSamples);
        applySecondaryTankPredelay (monoLeftSecondaryBuffer, secondaryLeftTankPredelay, secondaryLeftPredelaySamples, numSamples);
        applySecondaryTankPredelay (monoRightSecondaryBuffer, secondaryRightTankPredelay, secondaryRightPredelaySamples, numSamples);
    }

    chain.leftTank.process (monoLeftBuffer, numSamples);
    chain.rightTank.process (monoRightBuffer, numSamples);

    if (ir2Parallel)
    {
        chain.leftTankSecondary.process (monoLeftSecondaryBuffer, numSamples);
        chain.rightTankSecondary.process (monoRightSecondaryBuffer, numSamples);

        const auto extGain = 0.5f * extTankMix;
        monoLeftBuffer.applyGain (0, 0, numSamples, 1.0f - extGain);
        monoRightBuffer.applyGain (0, 0, numSamples, 1.0f - extGain);
        monoLeftBuffer.addFrom (0, 0, monoLeftSecondaryBuffer, 0, 0, numSamples, extGain);
        monoRightBuffer.addFrom (0, 0, monoRightSecondaryBuffer, 0, 0, numSamples, extGain);
    }
    else if (ir2Series)
    {
        monoLeftSecondaryBuffer.copyFrom (0, 0, monoLeftBuffer, 0, 0, numSamples);
        monoRightSecondaryBuffer.copyFrom (0, 0, monoRightBuffer, 0, 0, numSamples);
        applySecondaryTankPredelay (monoLeftBuffer, secondaryLeftTankPredelay, secondaryLeftPredelaySamples, numSamples);
        applySecondaryTankPredelay (monoRightBuffer, secondaryRightTankPredelay, secondaryRightPredelaySamples, numSamples);
        chain.leftTankSecondary.process (monoLeftBuffer, numSamples);
        chain.rightTankSecondary.process (monoRightBuffer, numSamples);

        monoLeftBuffer.applyGain (0, 0, numSamples, extTankMix);
        monoRightBuffer.applyGain (0, 0, numSamples, extTankMix);
        monoLeftBuffer.addFrom (0, 0, monoLeftSecondaryBuffer, 0, 0, numSamples, 1.0f - extTankMix);
        monoRightBuffer.addFrom (0, 0, monoRightSecondaryBuffer, 0, 0, numSamples, 1.0f - extTankMix);
    }

    wetStereoBuffer.copyFrom (0, 0, monoLeftBuffer, 0, 0, numSamples);
    wetStereoBuffer.copyFrom (1, 0, monoRightBuffer, 0, 0, numSamples);

    chain.stereoTankCrossfade.setCrossfadeAmount (
        forceMonoLeftOnly ? 0.0f : parameters.getRawParameterValue (crossfadeAmountParameterID)->load());

    chain.stereoTankCrossfade.process (wetStereoBuffer, numSamples);

    chain.filterClipper.setParameters (getFilterClipperParameters());
    chain.filterClipper.process (wetStereoBuffer, numSamples);
    sanitizeBuffer (wetStereoBuffer, numSamples);

    chain.feedback.setFeedbackAmount (
        parameters.getRawParameterValue (feedbackAmountParameterID)->load());
    chain.feedback.setFeedbackPhaseInverted (isFeedbackPhaseInverted());

    chain.feedback.process (wetStereoBuffer,
                            wetAfterFeedbackBuffer,
                            feedbackReturnBuffer,
                            predelayModulationBuffer.getReadPointer (1),
                            numSamples);
    sanitizeBuffer (wetAfterFeedbackBuffer, numSamples);
    sanitizeBuffer (feedbackReturnBuffer, numSamples);

    chain.wetDryMixer.setWetAmount (
        parameters.getRawParameterValue (wetDryParameterID)->load());

    chain.wetDryMixer.process (dryTapBuffer,
                               wetAfterFeedbackBuffer,
                               buffer,
                               numSamples);

    if (forceMonoLeftOnly && buffer.getNumChannels() > 1)
        buffer.clear (1, 0, numSamples);

    sanitizeBuffer (buffer, numSamples);
}

bool TheGreatAmericanSpringAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* TheGreatAmericanSpringAudioProcessor::createEditor()
{
    return new TheGreatAmericanSpringAudioProcessorEditor (*this);
}

void TheGreatAmericanSpringAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    auto state = parameters.copyState();
    state.setProperty (getTankIrPathPropertyName (TankSlot::left1), leftTank1IrPath, nullptr);
    state.setProperty (getTankIrPathPropertyName (TankSlot::right1), rightTank1IrPath, nullptr);
    state.setProperty (getTankIrPathPropertyName (TankSlot::left2), leftTank2IrPath, nullptr);
    state.setProperty (getTankIrPathPropertyName (TankSlot::right2), rightTank2IrPath, nullptr);
    state.setProperty ("playbackFilePath", playbackFilePath, nullptr);

    if (auto xml = state.createXml())
        copyXmlToBinary (*xml, destData);
}

void TheGreatAmericanSpringAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    if (auto xmlState = getXmlFromBinary (data, sizeInBytes))
    {
        auto restoredState = juce::ValueTree::fromXml (*xmlState);

        if (restoredState.hasType (parameters.state.getType()))
        {
            const auto restoredIr2Routing = restoredState.getProperty (x2TanksParameterID);

            if (restoredIr2Routing.isBool())
                restoredState.setProperty (x2TanksParameterID,
                                           static_cast<bool> (restoredIr2Routing) ? 2 : 0,
                                           nullptr);

            parameters.replaceState (restoredState);
            applyDefaultGasSettings();

            playbackFilePath = restoredState.getProperty ("playbackFilePath").toString();

            if (playbackFilePath.isEmpty())
                playbackFilePath = getEmbeddedPlaybackSources().front().displayPath;

            refreshAvailableSpringIRs();
            assignDefaultTankIRs();
            playbackActive = false;

            if (isPrepared)
            {
                loadTankIRFromCurrentPath (TankSlot::left1);
                loadTankIRFromCurrentPath (TankSlot::right1);
                loadTankIRFromCurrentPath (TankSlot::left2);
                loadTankIRFromCurrentPath (TankSlot::right2);
                loadSelectedPlaybackSource();
            }

            sendChangeMessage();
        }
    }
}

bool TheGreatAmericanSpringAudioProcessor::loadTankImpulseResponseFile (TankSlot slot, const juce::File& file)
{
    if (! file.existsAsFile())
        return false;

    getTankIrPath (slot) = file.getFullPathName();

    if (! isPrepared)
        return true;

    const auto loaded = getTankBlock (slot).loadImpulseResponse (file);

    if (loaded)
        sendChangeMessage();

    return loaded;
}

juce::String TheGreatAmericanSpringAudioProcessor::getTankImpulseResponseDisplayName (TankSlot slot) const
{
    const auto& fullPath = getTankIrPath (slot);

    if (fullPath.isEmpty())
        return "Fallback Dirac IR";

    const auto file = juce::File (fullPath);
    return file.existsAsFile() ? file.getFileName() : "Missing file";
}

juce::String TheGreatAmericanSpringAudioProcessor::getTankSlotName (TankSlot slot) const
{
    switch (slot)
    {
        case TankSlot::left1:  return "Left Main Tanks";
        case TankSlot::right1: return "Right Main Tanks";
        case TankSlot::left2:  return "Left Ext Reverb Tanks";
        case TankSlot::right2: return "Right Ext Reverb Tanks";
    }

    jassertfalse;
    return {};
}

juce::File TheGreatAmericanSpringAudioProcessor::getSpringIrDirectory() const
{
    const auto searchDirectories = getSpringIrSearchDirectories();

    for (const auto& directory : searchDirectories)
    {
        if (directory.isDirectory())
            return directory;
    }

    return searchDirectories.isEmpty() ? juce::File {} : searchDirectories.getFirst();
}

bool TheGreatAmericanSpringAudioProcessor::isX2Enabled() const
{
    return getIr2RoutingMode() != Ir2RoutingMode::off;
}

TheGreatAmericanSpringAudioProcessor::Ir2RoutingMode TheGreatAmericanSpringAudioProcessor::getIr2RoutingMode() const
{
    return toIr2RoutingMode (parameters.getRawParameterValue (x2TanksParameterID)->load());
}

bool TheGreatAmericanSpringAudioProcessor::isFeedbackPhaseInverted() const
{
    return parameters.getRawParameterValue (feedbackPhaseInvertParameterID)->load() >= 0.5f;
}

bool TheGreatAmericanSpringAudioProcessor::shouldConvertMonoSourceToStereo() const
{
    return parameters.getRawParameterValue (monoSourceToStereoParameterID)->load() >= 0.5f;
}

bool TheGreatAmericanSpringAudioProcessor::shouldShowUnavailableTankControls() const
{
    return parameters.getRawParameterValue (showUnavailableTankControlsParameterID)->load() >= 0.5f;
}

bool TheGreatAmericanSpringAudioProcessor::isCrossfadeAvailableForCurrentLayout() const
{
    return ! isMonoSourceWithoutStereoConversion();
}

juce::String TheGreatAmericanSpringAudioProcessor::getIr2RoutingDisplayName() const
{
    switch (getIr2RoutingMode())
    {
        case Ir2RoutingMode::off:      return "Off";
        case Ir2RoutingMode::series:   return "Series";
        case Ir2RoutingMode::parallel: return "Parallel";
    }

    jassertfalse;
    return "Off";
}

bool TheGreatAmericanSpringAudioProcessor::loadPlaybackFile (const juce::File& file)
{
    if (! file.existsAsFile())
        return false;

    std::unique_ptr<juce::AudioFormatReader> reader (audioFormatManager.createReaderFor (file));

    if (reader == nullptr)
        return false;

    juce::AudioBuffer<float> newBuffer (juce::jmax (1, static_cast<int> (reader->numChannels)),
                                        static_cast<int> (reader->lengthInSamples));

    if (! reader->read (newBuffer.getArrayOfWritePointers(),
                        newBuffer.getNumChannels(),
                        0,
                        newBuffer.getNumSamples()))
    {
        return false;
    }

    playbackBuffer = std::move (newBuffer);
    playbackSourceSampleRate = reader->sampleRate;
    playbackFilePath = file.getFullPathName();
    playbackReadPosition = 0.0;
    playbackActive = false;
    sendChangeMessage();
    return true;
}

void TheGreatAmericanSpringAudioProcessor::setPlaybackActive (bool shouldPlay)
{
    if (! hasPlaybackFile())
        return;

    if (shouldPlay && ! playbackActive)
        playbackReadPosition = 0.0;

    playbackActive = shouldPlay;
    sendChangeMessage();
}

bool TheGreatAmericanSpringAudioProcessor::isPlaybackActive() const
{
    return playbackActive;
}

bool TheGreatAmericanSpringAudioProcessor::hasPlaybackFile() const
{
    return playbackBuffer.getNumSamples() > 0;
}

juce::StringArray TheGreatAmericanSpringAudioProcessor::getPlaybackSourceDisplayNames() const
{
    juce::StringArray names;

    for (const auto& source : getEmbeddedPlaybackSources())
        names.add (juce::File (juce::String (source.displayPath)).getFileName());

    return names;
}

int TheGreatAmericanSpringAudioProcessor::getSelectedPlaybackSourceIndex() const
{
    return getPlaybackSourceIndexForPath (playbackFilePath);
}

bool TheGreatAmericanSpringAudioProcessor::setPlaybackSourceIndex (int index)
{
    if (! juce::isPositiveAndBelow (index, static_cast<int> (getEmbeddedPlaybackSources().size())))
        return false;

    playbackFilePath = getEmbeddedPlaybackSources()[static_cast<size_t> (index)].displayPath;

    if (! isPrepared)
    {
        sendChangeMessage();
        return true;
    }

    const auto loaded = loadSelectedPlaybackSource();

    if (loaded)
        sendChangeMessage();

    return loaded;
}

juce::String TheGreatAmericanSpringAudioProcessor::getPlaybackFileDisplayName() const
{
    if (playbackFilePath.isEmpty())
        return "No playback source loaded";

    return juce::File (playbackFilePath).getFileName();
}

juce::AudioProcessorValueTreeState::ParameterLayout TheGreatAmericanSpringAudioProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { crossfadeAmountParameterID, 1 },
                                                              "Crossfade Amount",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.2f));

    layout.add (std::make_unique<juce::AudioParameterChoice> (juce::ParameterID { modeParameterID, 1 },
                                                               "Mode",
                                                               juce::StringArray { "Clean", "Silicon", "LED", "Germanium" },
                                                               0));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { driveParameterID, 1 },
                                                              "Drive",
                                                              juce::NormalisableRange<float> (0.0f, 30.0f, 0.01f),
                                                              6.0f));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { preHpfCutoffParameterID, 1 },
                                                              "HPF Cutoff",
                                                              juce::NormalisableRange<float> (1.0f, 4000.0f, 0.01f, 0.35f),
                                                              120.0f));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { preHpfResonanceParameterID, 1 },
                                                              "HPF Q",
                                                              juce::NormalisableRange<float> (0.25f, 8.0f, 0.001f, 0.5f),
                                                              0.707f));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { postLpfCutoffParameterID, 1 },
                                                              "LPF Cutoff",
                                                              juce::NormalisableRange<float> (500.0f, 20000.0f, 0.01f, 0.35f),
                                                              16000.0f));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { postLpfResonanceParameterID, 1 },
                                                              "LPF Q",
                                                              juce::NormalisableRange<float> (0.25f, 8.0f, 0.001f, 0.5f),
                                                              0.707f));

    layout.add (std::make_unique<juce::AudioParameterChoice> (juce::ParameterID { x2TanksParameterID, 1 },
                                                               "Ext Reverb Tanks",
                                                               juce::StringArray { "Off", "Series", "Parallel" },
                                                               2));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { extTankMixParameterID, 1 },
                                                              "Ext Reverb Tanks Amount",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              1.0f));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { feedbackAmountParameterID, 1 },
                                                              "Feedback",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.2f));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { feedbackPhaseInvertParameterID, 1 },
                                                            "Feedback Phase Invert",
                                                            false));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { wetDryParameterID, 1 },
                                                              "Wet/Dry",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.5f));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { monoSourceToStereoParameterID, 1 },
                                                            "Mono Source To Stereo",
                                                            false));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { showUnavailableTankControlsParameterID, 1 },
                                                            "Will not be available in real life",
                                                            false));

    return layout;
}

void TheGreatAmericanSpringAudioProcessor::refreshAvailableSpringIRs()
{
    availableSpringIRs.clear();

    for (const auto& springDirectory : getSpringIrSearchDirectories())
    {
        if (! springDirectory.isDirectory())
            continue;

        for (const auto& extension : { "*.wav", "*.aif", "*.aiff", "*.flac" })
        {
            juce::Array<juce::File> matches;
            springDirectory.findChildFiles (matches, juce::File::findFiles, false, extension);

            for (const auto& file : matches)
                availableSpringIRs.addIfNotAlreadyThere (file);
        }
    }
}

void TheGreatAmericanSpringAudioProcessor::assignRandomTankIRsIfNeeded()
{
    if (availableSpringIRs.isEmpty())
        return;

    juce::Random random;

    const auto findAvailableIrByName = [this] (const juce::String& fileName)
    {
        for (const auto& candidate : availableSpringIRs)
        {
            if (candidate.getFileName().equalsIgnoreCase (fileName) && candidate.existsAsFile())
                return candidate;
        }

        return juce::File {};
    };

    const auto assignPreferredOrRandomIfEmpty = [this, &random, &findAvailableIrByName] (TankSlot slot, const juce::String& preferredFileName)
    {
        if (! getTankIrPath (slot).isEmpty())
            return;

        if (const auto preferredFile = findAvailableIrByName (preferredFileName); preferredFile.existsAsFile())
        {
            getTankIrPath (slot) = preferredFile.getFullPathName();
            return;
        }

        getTankIrPath (slot) = availableSpringIRs[random.nextInt (availableSpringIRs.size())].getFullPathName();
    };

    assignPreferredOrRandomIfEmpty (TankSlot::left1, defaultLeftTank1IrFileName);
    assignPreferredOrRandomIfEmpty (TankSlot::right1, defaultRightTank1IrFileName);
    assignPreferredOrRandomIfEmpty (TankSlot::left2, defaultLeftTank2IrFileName);
    assignPreferredOrRandomIfEmpty (TankSlot::right2, defaultRightTank2IrFileName);
}

void TheGreatAmericanSpringAudioProcessor::assignDefaultTankIRs()
{
    leftTank1IrPath.clear();
    rightTank1IrPath.clear();
    leftTank2IrPath.clear();
    rightTank2IrPath.clear();
    assignRandomTankIRsIfNeeded();
}

void TheGreatAmericanSpringAudioProcessor::setParameterPlainValue (const juce::String& parameterID, float plainValue)
{
    if (auto* parameter = parameters.getParameter (parameterID))
    {
        if (auto* ranged = dynamic_cast<juce::RangedAudioParameter*> (parameter))
            ranged->setValueNotifyingHost (ranged->convertTo0to1 (plainValue));
    }
}

void TheGreatAmericanSpringAudioProcessor::applyDefaultGasSettings()
{
    setParameterPlainValue (modeParameterID, 0.0f);
    setParameterPlainValue (driveParameterID, 6.0f);
    setParameterPlainValue (preHpfCutoffParameterID, 120.0f);
    setParameterPlainValue (preHpfResonanceParameterID, 0.707f);
    setParameterPlainValue (postLpfCutoffParameterID, 16000.0f);
    setParameterPlainValue (postLpfResonanceParameterID, 0.707f);
    setParameterPlainValue (x2TanksParameterID, 2.0f);
    setParameterPlainValue (extTankMixParameterID, 1.0f);
    setParameterPlainValue (crossfadeAmountParameterID, 0.2f);
    setParameterPlainValue (feedbackAmountParameterID, 0.2f);
    setParameterPlainValue (feedbackPhaseInvertParameterID, 0.0f);
    setParameterPlainValue (wetDryParameterID, 0.5f);
    setParameterPlainValue (monoSourceToStereoParameterID, 0.0f);
    setParameterPlainValue (showUnavailableTankControlsParameterID, 0.0f);
    assignDefaultTankIRs();
}

bool TheGreatAmericanSpringAudioProcessor::loadTankIRFromCurrentPath (TankSlot slot)
{
    const auto file = resolveSpringIrFile (getTankIrPath (slot));

    if (file.existsAsFile())
    {
        getTankIrPath (slot) = file.getFullPathName();
        return getTankBlock (slot).loadImpulseResponse (file);
    }

    loadFallbackTankIR (slot);
    return false;
}

juce::File TheGreatAmericanSpringAudioProcessor::getCurrentModuleBinaryFile() const
{
#if JUCE_WINDOWS
    HMODULE moduleHandle = nullptr;

    if (GetModuleHandleExW (GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS
                                | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            reinterpret_cast<LPCWSTR> (&createPluginFilter),
                            &moduleHandle) != 0)
    {
        std::array<wchar_t, 32768> modulePath {};
        const auto pathLength = GetModuleFileNameW (moduleHandle, modulePath.data(), static_cast<DWORD> (modulePath.size()));

        if (pathLength > 0)
            return juce::File (juce::String (modulePath.data()));
    }
#endif

    return juce::File::getSpecialLocation (juce::File::currentExecutableFile);
}

juce::Array<juce::File> TheGreatAmericanSpringAudioProcessor::getSpringIrSearchDirectories() const
{
    juce::Array<juce::File> directories;

    const auto moduleBinary = getCurrentModuleBinaryFile();
    const auto moduleDirectory = moduleBinary.getParentDirectory();
    const auto contentsDirectory = moduleDirectory.getParentDirectory();

    directories.addIfNotAlreadyThere (moduleDirectory.getChildFile ("Spring IRs"));

    if (contentsDirectory.getFileName().equalsIgnoreCase ("Contents"))
        directories.addIfNotAlreadyThere (contentsDirectory.getChildFile ("Resources").getChildFile ("Spring IRs"));

    directories.addIfNotAlreadyThere (juce::File (projectSpringIrDirectoryPath));

    return directories;
}

juce::File TheGreatAmericanSpringAudioProcessor::resolveSpringIrFile (const juce::String& storedPath) const
{
    if (storedPath.isEmpty())
        return {};

    const auto directFile = juce::File (storedPath);

    if (directFile.existsAsFile())
        return directFile;

    const auto targetName = directFile.getFileName();

    if (targetName.isEmpty())
        return {};

    for (const auto& candidate : availableSpringIRs)
    {
        if (candidate.getFileName().equalsIgnoreCase (targetName) && candidate.existsAsFile())
            return candidate;
    }

    for (const auto& directory : getSpringIrSearchDirectories())
    {
        const auto candidate = directory.getChildFile (targetName);

        if (candidate.existsAsFile())
            return candidate;
    }

    return directFile;
}

juce::Array<juce::File> TheGreatAmericanSpringAudioProcessor::getPlaybackSearchDirectories() const
{
    juce::Array<juce::File> directories;

    const auto moduleBinary = getCurrentModuleBinaryFile();
    const auto moduleDirectory = moduleBinary.getParentDirectory();
    const auto contentsDirectory = moduleDirectory.getParentDirectory();

    directories.addIfNotAlreadyThere (moduleDirectory.getChildFile ("Playback"));
    directories.addIfNotAlreadyThere (moduleDirectory.getChildFile ("Playback Audio"));

    if (contentsDirectory.getFileName().equalsIgnoreCase ("Contents"))
    {
        directories.addIfNotAlreadyThere (contentsDirectory.getChildFile ("Resources").getChildFile ("Playback"));
        directories.addIfNotAlreadyThere (contentsDirectory.getChildFile ("Resources").getChildFile ("Playback Audio"));
    }

    directories.addIfNotAlreadyThere (juce::File (R"(C:\Users\Jason\Music\Chris Sebastian)"));

    return directories;
}

juce::File TheGreatAmericanSpringAudioProcessor::resolvePlaybackFile (const juce::String& storedPath) const
{
    if (storedPath.isEmpty())
        return {};

    const auto directFile = juce::File (storedPath);

    if (directFile.existsAsFile())
        return directFile;

    const auto targetName = directFile.getFileName();

    if (targetName.isEmpty())
        return {};

    for (const auto& directory : getPlaybackSearchDirectories())
    {
        const auto candidate = directory.getChildFile (targetName);

        if (candidate.existsAsFile())
            return candidate;
    }

    return directFile;
}

void TheGreatAmericanSpringAudioProcessor::loadFallbackTankIR (TankSlot slot)
{
    juce::AudioBuffer<float> fallbackBuffer (1, 1);
    fallbackBuffer.setSample (0, 0, fallbackImpulse);
    getTankBlock (slot).loadImpulseResponse (std::move (fallbackBuffer), currentSampleRate);
}

juce::String TheGreatAmericanSpringAudioProcessor::getTankIrPathPropertyName (TankSlot slot)
{
    switch (slot)
    {
        case TankSlot::left1:  return "leftTank1IrPath";
        case TankSlot::right1: return "rightTank1IrPath";
        case TankSlot::left2:  return "leftTank2IrPath";
        case TankSlot::right2: return "rightTank2IrPath";
    }

    jassertfalse;
    return {};
}

juce::String& TheGreatAmericanSpringAudioProcessor::getTankIrPath (TankSlot slot)
{
    switch (slot)
    {
        case TankSlot::left1:  return leftTank1IrPath;
        case TankSlot::right1: return rightTank1IrPath;
        case TankSlot::left2:  return leftTank2IrPath;
        case TankSlot::right2: return rightTank2IrPath;
    }

    jassertfalse;
    return leftTank1IrPath;
}

const juce::String& TheGreatAmericanSpringAudioProcessor::getTankIrPath (TankSlot slot) const
{
    switch (slot)
    {
        case TankSlot::left1:  return leftTank1IrPath;
        case TankSlot::right1: return rightTank1IrPath;
        case TankSlot::left2:  return leftTank2IrPath;
        case TankSlot::right2: return rightTank2IrPath;
    }

    jassertfalse;
    return leftTank1IrPath;
}

TankIRBlock& TheGreatAmericanSpringAudioProcessor::getTankBlock (TankSlot slot)
{
    switch (slot)
    {
        case TankSlot::left1:  return chain.leftTank;
        case TankSlot::right1: return chain.rightTank;
        case TankSlot::left2:  return chain.leftTankSecondary;
        case TankSlot::right2: return chain.rightTankSecondary;
    }

    jassertfalse;
    return chain.leftTank;
}

const TankIRBlock& TheGreatAmericanSpringAudioProcessor::getTankBlock (TankSlot slot) const
{
    switch (slot)
    {
        case TankSlot::left1:  return chain.leftTank;
        case TankSlot::right1: return chain.rightTank;
        case TankSlot::left2:  return chain.leftTankSecondary;
        case TankSlot::right2: return chain.rightTankSecondary;
    }

    jassertfalse;
    return chain.leftTank;
}

void TheGreatAmericanSpringAudioProcessor::resizeProcessingBuffers (int samplesPerBlock)
{
    externalInputBuffer.setSize (2, samplesPerBlock);
    dryTapBuffer.setSize (2, samplesPerBlock);
    wetInputBaseBuffer.setSize (2, samplesPerBlock);
    wetStereoBuffer.setSize (2, samplesPerBlock);
    wetAfterFeedbackBuffer.setSize (2, samplesPerBlock);
    feedbackReturnBuffer.setSize (2, samplesPerBlock);
    predelayModulationBuffer.setSize (2, samplesPerBlock);
    monoLeftBuffer.setSize (1, samplesPerBlock);
    monoRightBuffer.setSize (1, samplesPerBlock);
    monoLeftSecondaryBuffer.setSize (1, samplesPerBlock);
    monoRightSecondaryBuffer.setSize (1, samplesPerBlock);

    externalInputBuffer.clear();
    dryTapBuffer.clear();
    wetInputBaseBuffer.clear();
    wetStereoBuffer.clear();
    wetAfterFeedbackBuffer.clear();
    feedbackReturnBuffer.clear();
    predelayModulationBuffer.clear();
    monoLeftBuffer.clear();
    monoRightBuffer.clear();
    monoLeftSecondaryBuffer.clear();
    monoRightSecondaryBuffer.clear();
}

void TheGreatAmericanSpringAudioProcessor::loadPlaybackIntoBuffer (juce::AudioBuffer<float>& targetBuffer, int numSamples)
{
    targetBuffer.clear();

    if (! playbackActive || playbackBuffer.getNumSamples() == 0 || currentSampleRate <= 0.0)
        return;

    const auto positionIncrement = playbackSourceSampleRate / currentSampleRate;
    auto* left = targetBuffer.getWritePointer (0);
    auto* right = targetBuffer.getWritePointer (1);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        const auto baseIndex = static_cast<int> (playbackReadPosition);
        const auto nextIndex = juce::jmin (baseIndex + 1, playbackBuffer.getNumSamples() - 1);

        if (baseIndex >= playbackBuffer.getNumSamples())
        {
            playbackActive = false;
            break;
        }

        const auto fraction = static_cast<float> (playbackReadPosition - static_cast<double> (baseIndex));
        const auto sourceLeft0 = playbackBuffer.getSample (0, baseIndex);
        const auto sourceLeft1 = playbackBuffer.getSample (0, nextIndex);
        const auto sourceRight0 = playbackBuffer.getNumChannels() > 1 ? playbackBuffer.getSample (1, baseIndex)
                                                                       : shouldConvertMonoSourceToStereo() ? sourceLeft0 : 0.0f;
        const auto sourceRight1 = playbackBuffer.getNumChannels() > 1 ? playbackBuffer.getSample (1, nextIndex)
                                                                       : shouldConvertMonoSourceToStereo() ? sourceLeft1 : 0.0f;

        left[sample] = juce::jmap (fraction, sourceLeft0, sourceLeft1);
        right[sample] = juce::jmap (fraction, sourceRight0, sourceRight1);
        playbackReadPosition += positionIncrement;
    }

    if (playbackReadPosition >= static_cast<double> (playbackBuffer.getNumSamples()))
        playbackActive = false;
}

bool TheGreatAmericanSpringAudioProcessor::loadPlaybackSourceFromMemory (const void* data,
                                                                           int dataSize,
                                                                           const juce::String& displayName)
{
    auto inputStream = std::make_unique<juce::MemoryInputStream> (data, static_cast<size_t> (dataSize), false);
    std::unique_ptr<juce::AudioFormatReader> reader (audioFormatManager.createReaderFor (std::move (inputStream)));

    if (reader == nullptr)
        return false;

    juce::AudioBuffer<float> newBuffer (juce::jmax (1, static_cast<int> (reader->numChannels)),
                                        static_cast<int> (reader->lengthInSamples));

    if (! reader->read (newBuffer.getArrayOfWritePointers(),
                        newBuffer.getNumChannels(),
                        0,
                        newBuffer.getNumSamples()))
    {
        return false;
    }

    playbackBuffer = std::move (newBuffer);
    playbackSourceSampleRate = reader->sampleRate;
    playbackFilePath = displayName;
    playbackReadPosition = 0.0;
    playbackActive = false;
    return true;
}

bool TheGreatAmericanSpringAudioProcessor::loadSelectedPlaybackSource()
{
    auto sourceIndex = getSelectedPlaybackSourceIndex();

    if (sourceIndex < 0)
    {
        playbackFilePath = getEmbeddedPlaybackSources().front().displayPath;
        sourceIndex = 0;
    }

    const auto& source = getEmbeddedPlaybackSources()[static_cast<size_t> (sourceIndex)];
    return loadPlaybackSourceFromMemory (source.data, source.dataSize, source.displayPath);
}

int TheGreatAmericanSpringAudioProcessor::getPlaybackSourceIndexForPath (const juce::String& sourcePath) const
{
    const auto sourceFileName = juce::File (sourcePath).getFileName();

    for (size_t index = 0; index < getEmbeddedPlaybackSources().size(); ++index)
    {
        const auto& source = getEmbeddedPlaybackSources()[index];
        const auto candidatePath = juce::String (source.displayPath);

        if (sourcePath.equalsIgnoreCase (candidatePath))
            return static_cast<int> (index);

        if (sourceFileName.isNotEmpty()
            && sourceFileName.equalsIgnoreCase (juce::File (candidatePath).getFileName()))
        {
            return static_cast<int> (index);
        }
    }

    return -1;
}

void TheGreatAmericanSpringAudioProcessor::buildExternalInput (juce::AudioBuffer<float>& hostBuffer, int numSamples)
{
    externalInputBuffer.copyFrom (0, 0, hostBuffer, 0, 0, numSamples);

    if (getTotalNumInputChannels() > 1 && hostBuffer.getNumChannels() > 1)
        externalInputBuffer.copyFrom (1, 0, hostBuffer, 1, 0, numSamples);
    else if (shouldConvertMonoSourceToStereo())
        externalInputBuffer.copyFrom (1, 0, hostBuffer, 0, 0, numSamples);
    else
        externalInputBuffer.clear (1, 0, numSamples);

    wetAfterFeedbackBuffer.clear();
    loadPlaybackIntoBuffer (wetAfterFeedbackBuffer, numSamples);

    externalInputBuffer.addFrom (0, 0, wetAfterFeedbackBuffer, 0, 0, numSamples);

    if (! isMonoSourceWithoutStereoConversion())
        externalInputBuffer.addFrom (1, 0, wetAfterFeedbackBuffer, 1, 0, numSamples);
}

bool TheGreatAmericanSpringAudioProcessor::isMonoSourceWithoutStereoConversion() const
{
    return getTotalNumInputChannels() == 1 && ! shouldConvertMonoSourceToStereo();
}

void TheGreatAmericanSpringAudioProcessor::applyWetPredelay (int numSamples)
{
    auto* wetLeft = wetInputBaseBuffer.getWritePointer (0);
    auto* wetRight = wetInputBaseBuffer.getWritePointer (1);
    auto* delayedLeft = wetStereoBuffer.getWritePointer (0);
    auto* delayedRight = wetStereoBuffer.getWritePointer (1);
    const auto* wetDelaySamplesPerSample = predelayModulationBuffer.getReadPointer (0);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        wetPredelayLeft.pushSample (0, wetLeft[sample]);
        wetPredelayRight.pushSample (0, wetRight[sample]);
        delayedLeft[sample] = wetPredelayLeft.popSample (0, wetDelaySamplesPerSample[sample]);
        delayedRight[sample] = wetPredelayRight.popSample (0, wetDelaySamplesPerSample[sample]);
    }
}

void TheGreatAmericanSpringAudioProcessor::updatePredelayModulation (int numSamples)
{
    auto* wetDelaySamples = predelayModulationBuffer.getWritePointer (0);
    auto* feedbackDelaySamples = predelayModulationBuffer.getWritePointer (1);
    const auto phaseIncrement = randomPredelayLfoFrequencyHz / currentSampleRate;

    for (int sample = 0; sample < numSamples; ++sample)
    {
        predelayLfoPhase += phaseIncrement;

        while (predelayLfoPhase >= 1.0)
        {
            predelayLfoPhase -= 1.0;
            wetPredelayTargetMilliseconds = juce::jmap (predelayRandom.nextFloat(),
                                                        static_cast<float> (randomPredelayMinimumMilliseconds),
                                                        static_cast<float> (randomPredelayMaximumMilliseconds));
            wetPredelayMillisecondsSmoothed.setTargetValue (wetPredelayTargetMilliseconds);
        }

        const auto wetDelayMilliseconds = wetPredelayMillisecondsSmoothed.getNextValue();
        const auto wetDelay = wetDelayMilliseconds * 0.001f * static_cast<float> (currentSampleRate);

        wetDelaySamples[sample] = wetDelay;
        feedbackDelaySamples[sample] = wetDelay / 3.0f;
    }
}

void TheGreatAmericanSpringAudioProcessor::sanitizeBuffer (juce::AudioBuffer<float>& buffer, int numSamples) const
{
    for (int channel = 0; channel < buffer.getNumChannels(); ++channel)
    {
        auto* samples = buffer.getWritePointer (channel);

        for (int sample = 0; sample < numSamples; ++sample)
        {
            auto value = samples[sample];

            if (! std::isfinite (value))
                value = 0.0f;

            samples[sample] = juce::jlimit (-8.0f, 8.0f, value);
        }
    }
}

void TheGreatAmericanSpringAudioProcessor::applySecondaryTankPredelay (
    juce::AudioBuffer<float>& monoBuffer,
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& delayLine,
    float delaySamples,
    int numSamples)
{
    auto* samples = monoBuffer.getWritePointer (0);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        delayLine.pushSample (0, samples[sample]);
        samples[sample] = delayLine.popSample (0, delaySamples);
    }
}

FilterClipperBlock::Parameters TheGreatAmericanSpringAudioProcessor::getFilterClipperParameters() const
{
    FilterClipperBlock::Parameters filterParameters;
    filterParameters.mode = toFilterClipperMode (
        juce::roundToInt (parameters.getRawParameterValue (modeParameterID)->load()));
    filterParameters.driveDb = parameters.getRawParameterValue (driveParameterID)->load();
    filterParameters.preHpfCutoffHz = parameters.getRawParameterValue (preHpfCutoffParameterID)->load();
    filterParameters.preHpfResonance = parameters.getRawParameterValue (preHpfResonanceParameterID)->load();
    filterParameters.postLpfCutoffHz = parameters.getRawParameterValue (postLpfCutoffParameterID)->load();
    filterParameters.postLpfResonance = parameters.getRawParameterValue (postLpfResonanceParameterID)->load();
    return filterParameters;
}

FilterClipperBlock::Mode TheGreatAmericanSpringAudioProcessor::toFilterClipperMode (int modeIndex)
{
    switch (modeIndex)
    {
        case 0:  return FilterClipperBlock::Mode::clean;
        case 1:  return FilterClipperBlock::Mode::silicon;
        case 2:  return FilterClipperBlock::Mode::led;
        case 3:  return FilterClipperBlock::Mode::germanium;
        default: break;
    }

    return FilterClipperBlock::Mode::clean;
}

TheGreatAmericanSpringAudioProcessor::Ir2RoutingMode TheGreatAmericanSpringAudioProcessor::toIr2RoutingMode (float parameterValue)
{
    switch (juce::jlimit (0, 2, juce::roundToInt (parameterValue)))
    {
        case 1:  return Ir2RoutingMode::series;
        case 2:  return Ir2RoutingMode::parallel;
        case 0:
        default: break;
    }

    return Ir2RoutingMode::off;
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new TheGreatAmericanSpringAudioProcessor();
}
