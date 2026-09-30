#include <BinaryData.h>

#include "PluginProcessor.h"
#include "PluginEditor.h"

#if JUCE_WINDOWS
 #include <windows.h>
#endif

#include <algorithm>
#include <array>

namespace
{
constexpr auto projectSpringIrDirectoryPath = R"(C:\Users\Jason\source\repos\GAS\Spring IRs)";
constexpr double predelayLfoFrequencyHz = 0.3;
constexpr double predelaySmoothingSeconds = 1.25;
// Each tank gets its own predelay, wandering independently inside its OWN window.
// 2026-09-30: L and R used to share one window per pair (both short lanes 20-30, both
// long lanes 30-42). Giving every lane its own window decorrelates L from R as well as
// short from long, which widens the image instead of just varying it.
//
// Lane order is primary L, primary R, secondary L, secondary R, and matches the four
// predelays named on the signal-path diagram:
//   lane 0 = Predelay 1, short L, 20 to 30 ms
//   lane 1 = Predelay 3, short R, 22 to 35 ms
//   lane 2 = Predelay 2, long  L, 30 to 42 ms
//   lane 3 = Predelay 4, long  R, 25 to 40 ms
constexpr std::array<double, 4> predelayLaneMinMs { { 20.0, 22.0, 30.0, 25.0 } };
constexpr std::array<double, 4> predelayLaneMaxMs { { 30.0, 35.0, 42.0, 40.0 } };
constexpr float fallbackImpulse = 1.0f;
constexpr auto defaultLeftTank1IrFileName = "GBS-L.wav";
constexpr auto defaultRightTank1IrFileName = "GBS-R.wav";
constexpr auto defaultLeftTank2IrFileName = "GAS-L.wav";
constexpr auto defaultRightTank2IrFileName = "GAS-R.wav";
constexpr auto presetNameProperty = "presetName";

// ── The tank blend knob ──────────────────────────────────────────────────────
// 2026-09-30: the knob means different things in the two routings, so the law is
// per mode rather than one shared curve. In Off it does nothing at all.
//
// PARALLEL, "Short / Long Tank Mix": a true crossfade. Hard left is the short tanks
// alone, hard right the long tanks alone, and the two always sum to 100%.
//
// SERIES, "+ %Long Tank": one control, how much long tank gets added. 0% is the short
// tank and the dirt block on their own, 100% is all of it through the long tank. This
// is linear across the whole sweep. The old curve hit 100% at noon and did nothing
// above it, which was fine while a second Short% blend used the top half, but that
// blend is gone, so the top half would have been dead travel.
inline float parallelShortGainFor (float mix) noexcept
{
    return 1.0f - juce::jlimit (0.0f, 1.0f, mix);
}

inline float parallelLongGainFor (float mix) noexcept
{
    return juce::jlimit (0.0f, 1.0f, mix);
}

inline float seriesLongGainFor (float mix) noexcept
{
    return juce::jlimit (0.0f, 1.0f, mix);
}

// The routing the knob text should describe. processBlock and the routing parameter
// listener both keep this current, so the host's automation display matches the UI.
std::atomic<int> currentRoutingForText { 0 };   // 0 off, 1 series, 2 parallel

// The plain 0..1 mix controls read as whole percentages, so 0.5 shows as "50%" rather
// than the bare "0.50" the default formatter produced.
juce::String percentText (float normalised)
{
    return juce::String (juce::roundToInt (normalised * 100.0f)) + "%";
}

// ...and back again, so typing "50" or "50%" into the box lands on 0.5.
float percentValue (const juce::String& text)
{
    return juce::jlimit (0.0f, 1.0f, text.getFloatValue() / 100.0f);
}

// What the knob reads as, which depends on the routing it is sitting in. Off has no
// blend to make, Series shows how much long tank is being added, and Parallel shows
// the crossfade as the two halves that always add up to 100%.
juce::String shortLongMixText (float mix)
{
    const auto clamped = juce::jlimit (0.0f, 1.0f, mix);
    const auto longPercent = juce::roundToInt (clamped * 100.0f);

    switch (currentRoutingForText.load (std::memory_order_relaxed))
    {
        case 1:  return juce::String (longPercent) + "%";
        case 2:  return juce::String (100 - longPercent) + "% Short / "
                      + juce::String (longPercent) + "% Long";
        default: return "N/A";
    }
}

struct EmbeddedPlaybackSource
{
    const char* displayPath;
    const void* data;
    int dataSize;
};

const auto& getEmbeddedPlaybackSources()
{
    static const std::array<EmbeddedPlaybackSource, 30> sources {{
        { "Make Reverb Great Again-mono.mp3", BinaryData::Make_Reverb_Great_Againmono_mp3, BinaryData::Make_Reverb_Great_Againmono_mp3Size },
        { "Its a Shame-stereo.mp3", BinaryData::Its_a_Shamestereo_mp3, BinaryData::Its_a_Shamestereo_mp3Size },
        { "Zombie Remix-stereo.mp3", BinaryData::Zombie_Remixstereo_mp3, BinaryData::Zombie_Remixstereo_mp3Size },
        // NAM rig demo clips (guitar and bass, added 2026-09-12)
        { "arpeggio-deluxe-clean.mp3", BinaryData::arpeggiodeluxeclean_mp3, BinaryData::arpeggiodeluxeclean_mp3Size },
        { "arpeggio-dirty-punk.mp3", BinaryData::arpeggiodirtypunk_mp3, BinaryData::arpeggiodirtypunk_mp3Size },
        { "arpeggio-iconic-cleanish.mp3", BinaryData::arpeggioiconiccleanish_mp3, BinaryData::arpeggioiconiccleanish_mp3Size },
        { "arpeggio-quick-clean.mp3", BinaryData::arpeggioquickclean_mp3, BinaryData::arpeggioquickclean_mp3Size },
        { "arpeggio-warm-crunch.mp3", BinaryData::arpeggiowarmcrunch_mp3, BinaryData::arpeggiowarmcrunch_mp3Size },
        { "finger-bass-bite.mp3", BinaryData::fingerbassbite_mp3, BinaryData::fingerbassbite_mp3Size },
        { "finger-bass-clean-bright.mp3", BinaryData::fingerbasscleanbright_mp3, BinaryData::fingerbasscleanbright_mp3Size },
        { "finger-bass-growl.mp3", BinaryData::fingerbassgrowl_mp3, BinaryData::fingerbassgrowl_mp3Size },
        { "finger-bass-nice-warm.mp3", BinaryData::fingerbassnicewarm_mp3, BinaryData::fingerbassnicewarm_mp3Size },
        { "metal-5150.mp3", BinaryData::metal5150_mp3, BinaryData::metal5150_mp3Size },
        { "metal-blackstar.mp3", BinaryData::metalblackstar_mp3, BinaryData::metalblackstar_mp3Size },
        { "metal-dualrec.mp3", BinaryData::metaldualrec_mp3, BinaryData::metaldualrec_mp3Size },
        { "pick-bass-bite.mp3", BinaryData::pickbassbite_mp3, BinaryData::pickbassbite_mp3Size },
        { "pick-bass-clean-bright.mp3", BinaryData::pickbasscleanbright_mp3, BinaryData::pickbasscleanbright_mp3Size },
        { "pick-bass-growl.mp3", BinaryData::pickbassgrowl_mp3, BinaryData::pickbassgrowl_mp3Size },
        { "pick-bass-metalcore.mp3", BinaryData::pickbassmetalcore_mp3, BinaryData::pickbassmetalcore_mp3Size },
        { "pick-bass-rock-classic.mp3", BinaryData::pickbassrockclassic_mp3, BinaryData::pickbassrockclassic_mp3Size },
        { "power-chords-classic-hi-gain.mp3", BinaryData::powerchordsclassichigain_mp3, BinaryData::powerchordsclassichigain_mp3Size },
        { "power-chords-iconic-cleanish.mp3", BinaryData::powerchordsiconiccleanish_mp3, BinaryData::powerchordsiconiccleanish_mp3Size },
        { "power-chords-plexi.mp3", BinaryData::powerchordsplexi_mp3, BinaryData::powerchordsplexi_mp3Size },
        { "power-chords-punk-rock-rhythm.mp3", BinaryData::powerchordspunkrockrhythm_mp3, BinaryData::powerchordspunkrockrhythm_mp3Size },
        { "rhythm-chords-ac30-crunch.mp3", BinaryData::rhythmchordsac30crunch_mp3, BinaryData::rhythmchordsac30crunch_mp3Size },
        { "rhythm-chords-fender-clean.mp3", BinaryData::rhythmchordsfenderclean_mp3, BinaryData::rhythmchordsfenderclean_mp3Size },
        { "rhythm-chords-suhr-clean.mp3", BinaryData::rhythmchordssuhrclean_mp3, BinaryData::rhythmchordssuhrclean_mp3Size },
        { "solo-diezel.mp3", BinaryData::solodiezel_mp3, BinaryData::solodiezel_mp3Size },
        { "solo-fortin.mp3", BinaryData::solofortin_mp3, BinaryData::solofortin_mp3Size },
        { "solo-mesa.mp3", BinaryData::solomesa_mp3, BinaryData::solomesa_mp3Size }
    }};

    return sources;
}

juce::StringArray getFactoryPresetNames()
{
    return { "GBS default", "GAS default" };
}

juce::String sanitizePresetFileName (juce::String presetName)
{
    presetName = presetName.trim();
    presetName = presetName.retainCharacters ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-()");
    return presetName.trim();
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

    parameters.addParameterListener (railOversamplingParameterID, this);
    parameters.addParameterListener (x2TanksParameterID, this);

    // So the knob's text law is right before the first block of audio ever runs.
    currentRoutingForText.store (static_cast<int> (getIr2RoutingMode()), std::memory_order_relaxed);
}

TheGreatAmericanSpringAudioProcessor::~TheGreatAmericanSpringAudioProcessor()
{
    parameters.removeParameterListener (railOversamplingParameterID, this);
    parameters.removeParameterListener (x2TanksParameterID, this);
    cancelPendingUpdate();
}

void TheGreatAmericanSpringAudioProcessor::parameterChanged (const juce::String& parameterID, float newValue)
{
    // May arrive on the audio thread, so only flag it here.
    if (parameterID == railOversamplingParameterID)
        triggerAsyncUpdate();

    // Keeps the host's readout for the blend knob honest even with the transport
    // stopped, when processBlock is not running to do it.
    if (parameterID == x2TanksParameterID)
        currentRoutingForText.store (juce::jlimit (0, 2, juce::roundToInt (newValue)), std::memory_order_relaxed);
}

void TheGreatAmericanSpringAudioProcessor::handleAsyncUpdate()
{
    // Message thread. Suspending takes the callback lock, so the audio thread is not
    // inside processBlock while the oversamplers are torn down and rebuilt.
    suspendProcessing (true);
    rebuildRailSaturators();
    suspendProcessing (false);
}

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
    predelayLfoPhase = 0.0;
    for (int lane = 0; lane < 4; ++lane)
    {
        const auto minMs = predelayLaneMinMs[static_cast<size_t> (lane)];
        const auto maxMs = predelayLaneMaxMs[static_cast<size_t> (lane)];
        predelayTargetMs[lane] = juce::jmap (predelayRandom.nextFloat(),
                                             static_cast<float> (minMs),
                                             static_cast<float> (maxMs));
        predelayMsSmoothed[lane].reset (currentSampleRate, predelaySmoothingSeconds);
        predelayMsSmoothed[lane].setCurrentAndTargetValue (predelayTargetMs[lane]);
    }

    resizeProcessingBuffers (currentMaximumBlockSize);

    // Remembered so a change to the oversampling choice can re-prepare without waiting
    // for the host to call prepareToPlay again.
    preparedSampleRate = sampleRate;
    preparedBlockSize = currentMaximumBlockSize;
    rebuildRailSaturators();

    // 30 ms ramp: fast enough to feel immediate on the knob, slow enough that
    // a full-range jump stays click-free.
    for (auto* smoothed : { &preInputGainSmoothed, &inputGainSmoothed, &outputGainSmoothed, &postOutputGainSmoothed })
        smoothed->reset (sampleRate, 0.03);

    resetLevelSmoothers();

    juce::dsp::ProcessSpec monoSpec;
    monoSpec.sampleRate = sampleRate;
    monoSpec.maximumBlockSize = static_cast<juce::uint32> (currentMaximumBlockSize);
    monoSpec.numChannels = 1;

    wetPredelayLeft.prepare (monoSpec);
    wetPredelayRight.prepare (monoSpec);
    secondaryLeftTankPredelay.prepare (monoSpec);
    secondaryRightTankPredelay.prepare (monoSpec);

    chain.prepare (sampleRate, currentMaximumBlockSize);
    reset();

    // After chain.prepare, since the output stage only knows its delay once its own
    // oversampler exists.
    updateReportedLatency();

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
    secondaryLeftTankPredelay.reset();
    secondaryRightTankPredelay.reset();
    predelayLfoPhase = 0.0;
    for (int lane = 0; lane < 4; ++lane)
        predelayMsSmoothed[lane].setCurrentAndTargetValue (predelayTargetMs[lane]);
    lastIr2RoutingMode = getIr2RoutingMode();
    lastStereoMode = getStereoMode();
    resetLevelSmoothers();

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
    monoLeftSeriesBypassBuffer.clear();
    monoRightSeriesBypassBuffer.clear();

    for (auto* saturator : { &wetInputRail, &wetStereoRail, &wetAfterFeedbackRail, &feedbackReturnRail, &outputRail })
        saturator->reset();

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

    // Pre Input (plugin only, not on the PCB): the very first gain stage, ahead
    // of the dry / wet split, so both the host input and the built-in playback
    // source are trimmed before anything else sees them.
    preInputGainSmoothed.setTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (preInputLevelParameterID)->load()));
    applySmoothedGain (externalInputBuffer, preInputGainSmoothed, numSamples);

    lastMonoSourceWithoutStereoConversion.store (false, std::memory_order_relaxed);

    const auto stereoMode = getStereoMode();

    if (stereoMode != lastStereoMode)
    {
        // Switching Stereo / Mono > Stereo / MEGAVERB re-routes the feedback,
        // so flush the loop rather than let the old recirculation cross over.
        feedbackReturnBuffer.clear();
        chain.feedback.reset();
        lastStereoMode = stereoMode;
    }

    // Dry tap is split off here, straight after Pre Input. Everything below is
    // the wet path until the Wet/Dry mixer.
    dryTapBuffer.copyFrom (0, 0, externalInputBuffer, 0, 0, numSamples);
    dryTapBuffer.copyFrom (1, 0, externalInputBuffer, 1, 0, numSamples);

    // Vol (Solid State / Tube): the board's first knob on the wet path. The pot
    // stage sets the level into the tube, so the knob is also the tube's drive.
    const auto inputTube = isInputTubeEngaged();
    const auto outputTape = isOutputTapeEngaged();
    wetInputBaseBuffer.copyFrom (0, 0, externalInputBuffer, 0, 0, numSamples);
    wetInputBaseBuffer.copyFrom (1, 0, externalInputBuffer, 1, 0, numSamples);
    inputGainSmoothed.setTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (inputLevelParameterID)->load()));
    applySmoothedGain (wetInputBaseBuffer, inputGainSmoothed, numSamples);

    chain.inputStage.setEnabled (inputTube, false);
    chain.inputStage.process (wetInputBaseBuffer, numSamples);
    scrubBuffer (wetInputBaseBuffer, numSamples, 0.0f);
    wetInputRail.process (wetInputBaseBuffer, numSamples, opAmpRailGain);

    // MEGAVERB joins the crossed feedback to each channel BEFORE that channel's
    // In meter, so what leaves the Left path lands in the Right just ahead of the
    // R In meter and vice versa, and the meters show the sound ping-ponging
    // L > R > L. In Stereo and Mono > Stereo the feedback still returns after the
    // tap, so In reads only the fresh wet input. Addition is commutative and
    // nothing else sits between these two points, so this changes what the meters
    // read, not the audio.
    const auto showCrossedFeedbackOnInMeters = stereoMode == StereoMode::megaverb;

    if (showCrossedFeedbackOnInMeters)
    {
        wetInputBaseBuffer.addFrom (0, 0, feedbackReturnBuffer, 0, 0, numSamples);
        wetInputBaseBuffer.addFrom (1, 0, feedbackReturnBuffer, 1, 0, numSamples);
    }

    // Input meter: straight after the Solid State / Tube knob.
    inputMeterPeakL.store (wetInputBaseBuffer.getMagnitude (0, 0, numSamples), std::memory_order_relaxed);
    inputMeterPeakR.store (wetInputBaseBuffer.getMagnitude (1, 0, numSamples), std::memory_order_relaxed);

    if (! showCrossedFeedbackOnInMeters)
    {
        wetInputBaseBuffer.addFrom (0, 0, feedbackReturnBuffer, 0, 0, numSamples);
        wetInputBaseBuffer.addFrom (1, 0, feedbackReturnBuffer, 1, 0, numSamples);
    }

    chain.dirtDynamics.setParameters (getDirtDynamicsParameters());

    updatePredelayModulation (numSamples);
    applyWetPredelay (numSamples);

    monoLeftBuffer.copyFrom (0, 0, wetStereoBuffer, 0, 0, numSamples);
    monoRightBuffer.copyFrom (0, 0, wetStereoBuffer, 1, 0, numSamples);

    const auto ir2RoutingMode = getIr2RoutingMode();
    const auto ir2Series = ir2RoutingMode == Ir2RoutingMode::series;
    const auto ir2Parallel = ir2RoutingMode == Ir2RoutingMode::parallel;
    const auto extTankMix = parameters.getRawParameterValue (extTankMixParameterID)->load();

    // Keep the knob's text law in step with the routing it is sitting in, so the host's
    // automation readout says the same thing the on-screen knob does.
    currentRoutingForText.store (ir2Series ? 1 : (ir2Parallel ? 2 : 0), std::memory_order_relaxed);

    if (ir2RoutingMode != lastIr2RoutingMode)
    {
        secondaryLeftTankPredelay.reset();
        secondaryRightTankPredelay.reset();
        monoLeftSecondaryBuffer.clear();
        monoRightSecondaryBuffer.clear();
        monoLeftSeriesBypassBuffer.clear();
        monoRightSeriesBypassBuffer.clear();
        lastIr2RoutingMode = ir2RoutingMode;
    }

    if (ir2Parallel)
    {
        // Parallel: the secondary tank model branches from the dry wet input
        // before the primary-tank predelay. In hardware terms this maps to the
        // left 9EB2C1B and right 9EB3C1B tank path running alongside the
        // primary 4AB1C1B tank path.
        monoLeftSecondaryBuffer.copyFrom (0, 0, wetInputBaseBuffer, 0, 0, numSamples);
        monoRightSecondaryBuffer.copyFrom (0, 0, wetInputBaseBuffer, 1, 0, numSamples);
        applySecondaryTankPredelay (monoLeftSecondaryBuffer, secondaryLeftTankPredelay, predelayModulationBuffer.getReadPointer (3), numSamples);
        applySecondaryTankPredelay (monoRightSecondaryBuffer, secondaryRightTankPredelay, predelayModulationBuffer.getReadPointer (4), numSamples);
    }

    // 2026-09-30 (signal-path diagram v3): Series no longer blends the short tank
    // against a bypass, so there is nothing to hold here any more. The short tank is
    // always fully in circuit and the one knob is Long% only.

    chain.leftTank.process (monoLeftBuffer, numSamples);
    chain.rightTank.process (monoRightBuffer, numSamples);

    if (ir2Parallel)
    {
        chain.leftTankSecondary.process (monoLeftSecondaryBuffer, numSamples);
        chain.rightTankSecondary.process (monoRightSecondaryBuffer, numSamples);

        // "Short / Long Tank Mix": the two tanks run side by side and the knob
        // crossfades between them. Hard left is the short tanks alone, noon is half
        // and half, hard right is the long tanks alone. The two always sum to 100%.
        const auto parallelShortGain = parallelShortGainFor (extTankMix);
        const auto parallelLongGain  = parallelLongGainFor  (extTankMix);
        monoLeftBuffer.applyGain  (0, 0, numSamples, parallelShortGain);
        monoRightBuffer.applyGain (0, 0, numSamples, parallelShortGain);
        monoLeftBuffer.addFrom  (0, 0, monoLeftSecondaryBuffer,  0, 0, numSamples, parallelLongGain);
        monoRightBuffer.addFrom (0, 0, monoRightSecondaryBuffer, 0, 0, numSamples, parallelLongGain);
    }
    else if (ir2Series)
    {
        // Series, per signal-path diagram v3 (2026-09-30).
        //
        // The Gain / Dirt / Comp-Limit block sits HERE, right after the short tank and
        // BEFORE the Long% split, so both the long branch and the bypass go through it.
        // It used to sit after both tanks, which meant that with the knob hard left the
        // signal never reached the dirt or the compressor at all.
        //
        // Off and Parallel still run that block after their tanks, so it happens further
        // down for those two. That is why the call below is guarded on ir2Series.
        wetStereoBuffer.copyFrom (0, 0, monoLeftBuffer, 0, 0, numSamples);
        wetStereoBuffer.copyFrom (1, 0, monoRightBuffer, 0, 0, numSamples);

        chain.dirtDynamics.process (wetStereoBuffer, numSamples);
        scrubBuffer (wetStereoBuffer, numSamples, 0.0f);
        wetStereoRail.process (wetStereoBuffer, numSamples, opAmpRailGain);

        wetMeterPeakL.store (wetStereoBuffer.getMagnitude (0, 0, numSamples), std::memory_order_relaxed);
        wetMeterPeakR.store (wetStereoBuffer.getMagnitude (1, 0, numSamples), std::memory_order_relaxed);

        monoLeftBuffer.copyFrom  (0, 0, wetStereoBuffer, 0, 0, numSamples);
        monoRightBuffer.copyFrom (0, 0, wetStereoBuffer, 1, 0, numSamples);

        // The Long % split point: hold what arrives here so it can be blended against
        // the long-tank branch further down.
        monoLeftSecondaryBuffer.copyFrom (0, 0, monoLeftBuffer, 0, 0, numSamples);
        monoRightSecondaryBuffer.copyFrom (0, 0, monoRightBuffer, 0, 0, numSamples);

        applySecondaryTankPredelay (monoLeftBuffer, secondaryLeftTankPredelay, predelayModulationBuffer.getReadPointer (3), numSamples);
        applySecondaryTankPredelay (monoRightBuffer, secondaryRightTankPredelay, predelayModulationBuffer.getReadPointer (4), numSamples);

        // +6 dB makeup gain between the two tanks (Series only) to compensate
        // for the level drop from cascading the second reverb tank.
        const float interTankGain = juce::Decibels::decibelsToGain (6.0f);
        monoLeftBuffer.applyGain  (0, 0, numSamples, interTankGain);
        monoRightBuffer.applyGain (0, 0, numSamples, interTankGain);

        chain.leftTankSecondary.process (monoLeftBuffer, numSamples);
        chain.rightTankSecondary.process (monoRightBuffer, numSamples);

        // "+ %Long Tank": Long% of the long tank against (100 - Long%) of what was
        // held at the split. 0% is the short tank and the dirt block on their own,
        // 100% is all of it through the long tank, linear the whole way across.
        const auto seriesLongGain = seriesLongGainFor (extTankMix);
        monoLeftBuffer.applyGain  (0, 0, numSamples, seriesLongGain);
        monoRightBuffer.applyGain (0, 0, numSamples, seriesLongGain);
        monoLeftBuffer.addFrom  (0, 0, monoLeftSecondaryBuffer,  0, 0, numSamples, 1.0f - seriesLongGain);
        monoRightBuffer.addFrom (0, 0, monoRightSecondaryBuffer, 0, 0, numSamples, 1.0f - seriesLongGain);
    }

    wetStereoBuffer.copyFrom (0, 0, monoLeftBuffer, 0, 0, numSamples);
    wetStereoBuffer.copyFrom (1, 0, monoRightBuffer, 0, 0, numSamples);

    // Gain (pull for Dirt) + Comp / Off / Limit: wet path only, after the tanks
    // and before the feedback block, where the Rev B mode circuit sat.
    //
    // Series has already run this further up, between the short tank and the Long%
    // split, so it is skipped here for that mode. Off and Parallel run it now.
    if (! ir2Series)
    {
        chain.dirtDynamics.process (wetStereoBuffer, numSamples);
        scrubBuffer (wetStereoBuffer, numSamples, 0.0f);
        wetStereoRail.process (wetStereoBuffer, numSamples, opAmpRailGain);

        // Wet meter: straight after the circuit, just before the feedback path.
        wetMeterPeakL.store (wetStereoBuffer.getMagnitude (0, 0, numSamples), std::memory_order_relaxed);
        wetMeterPeakR.store (wetStereoBuffer.getMagnitude (1, 0, numSamples), std::memory_order_relaxed);
    }

    chain.feedback.setFeedbackAmount (
        parameters.getRawParameterValue (feedbackAmountParameterID)->load());
    chain.feedback.setFeedbackPhaseInverted (isFeedbackPhaseInverted());
    chain.feedback.setCrossCoupled (stereoMode == StereoMode::megaverb);

    chain.feedback.process (wetStereoBuffer,
                            wetAfterFeedbackBuffer,
                            feedbackReturnBuffer,
                            predelayModulationBuffer.getReadPointer (1),
                            numSamples);
    scrubBuffer (wetAfterFeedbackBuffer, numSamples, 0.0f);
    wetAfterFeedbackRail.process (wetAfterFeedbackBuffer, numSamples, opAmpRailGain);

    // Comp / Off / Limit, per signal-path diagram v4 (2026-09-30). It sits HERE, in the
    // feedback return leg between the Feedback block and the Fb In summer, so what it
    // holds down is the signal going back round the loop. Turn Fb up and the circuit
    // stops the recirculation running away, while the wet signal heading for the output
    // keeps whatever dynamics the tanks and the Dirt stage gave it. Both circuits now
    // start 6 dB earlier as well (kThresholdDbfs, -24 dBFS), so there is something to
    // grab with before the loop is already loud.
    chain.feedbackDynamics.setDynamics (getDynamics());
    chain.feedbackDynamics.process (feedbackReturnBuffer, numSamples);

    scrubBuffer (feedbackReturnBuffer, numSamples, 0.0f);
    feedbackReturnRail.process (feedbackReturnBuffer, numSamples, opAmpRailGain);

    chain.wetDryMixer.setWetAmount (
        parameters.getRawParameterValue (wetDryParameterID)->load());

    chain.wetDryMixer.process (dryTapBuffer,
                               wetAfterFeedbackBuffer,
                               buffer,
                               numSamples);

    // Output (pull for Tape): the board's last knob. The pot stage drives the
    // output circuits: the tube first when Vol is pulled, then the tape.
    outputGainSmoothed.setTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (outputLevelParameterID)->load()));
    applySmoothedGain (buffer, outputGainSmoothed, numSamples);

    if (buffer.getNumChannels() >= 2)
    {
        chain.outputStage.setEnabled (inputTube, outputTape);
        chain.outputStage.process (buffer, numSamples);
    }
    else
    {
        // Mono host bus: run the stage on a stereo scratch copy.
        wetAfterFeedbackBuffer.copyFrom (0, 0, buffer, 0, 0, numSamples);
        wetAfterFeedbackBuffer.copyFrom (1, 0, buffer, 0, 0, numSamples);
        chain.outputStage.setEnabled (inputTube, outputTape);
        chain.outputStage.process (wetAfterFeedbackBuffer, numSamples);
        buffer.copyFrom (0, 0, wetAfterFeedbackBuffer, 0, 0, numSamples);
    }

    // The board's output node, so it runs out of rail like every other one. Nothing
    // clamped here before, which let the output tube and tape stages overshoot past
    // what the real circuit could swing.
    scrubBuffer (buffer, numSamples, 0.0f);
    outputRail.process (buffer, numSamples, opAmpRailGain);

    // Post Output (plugin only, not on the PCB).
    postOutputGainSmoothed.setTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (postOutputLevelParameterID)->load()));
    applySmoothedGain (buffer, postOutputGainSmoothed, numSamples);

    scrubBuffer (buffer, numSamples, outputCeilingGain);

    // Output meter: the absolute last thing before audio leaves the plugin.
    // A mono host bus has no right channel, so it reads the left twice.
    const auto outRightChannel = buffer.getNumChannels() > 1 ? 1 : 0;
    outputMeterPeakL.store (buffer.getMagnitude (0, 0, numSamples), std::memory_order_relaxed);
    outputMeterPeakR.store (buffer.getMagnitude (outRightChannel, 0, numSamples), std::memory_order_relaxed);
}

void TheGreatAmericanSpringAudioProcessor::resetLevelSmoothers()
{
    preInputGainSmoothed.setCurrentAndTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (preInputLevelParameterID)->load()));
    inputGainSmoothed.setCurrentAndTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (inputLevelParameterID)->load()));
    outputGainSmoothed.setCurrentAndTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (outputLevelParameterID)->load()));
    postOutputGainSmoothed.setCurrentAndTargetValue (
        juce::Decibels::decibelsToGain (parameters.getRawParameterValue (postOutputLevelParameterID)->load()));
}

void TheGreatAmericanSpringAudioProcessor::applySmoothedGain (juce::AudioBuffer<float>& target,
                                                                juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear>& smoothedGain,
                                                                int numSamples)
{
    // Per-sample only while the ramp is actually moving; a settled knob falls
    // through to a single vectorised applyGain.
    if (smoothedGain.isSmoothing())
    {
        for (int sample = 0; sample < numSamples; ++sample)
        {
            const auto gain = smoothedGain.getNextValue();

            for (int channel = 0; channel < target.getNumChannels(); ++channel)
                target.getWritePointer (channel)[sample] *= gain;
        }
    }
    else
    {
        target.applyGain (0, numSamples, smoothedGain.getTargetValue());
    }
}

bool TheGreatAmericanSpringAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* TheGreatAmericanSpringAudioProcessor::createEditor()
{
    return new TheGreatAmericanSpringAudioProcessorEditor (*this);
}

juce::ValueTree TheGreatAmericanSpringAudioProcessor::createStateTree()
{
    auto state = parameters.copyState();
    state.setProperty (getTankIrPathPropertyName (TankSlot::left1), leftTank1IrPath, nullptr);
    state.setProperty (getTankIrPathPropertyName (TankSlot::right1), rightTank1IrPath, nullptr);
    state.setProperty (getTankIrPathPropertyName (TankSlot::left2), leftTank2IrPath, nullptr);
    state.setProperty (getTankIrPathPropertyName (TankSlot::right2), rightTank2IrPath, nullptr);
    state.setProperty ("playbackFilePath", playbackFilePath, nullptr);
    return state;
}

void TheGreatAmericanSpringAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    auto state = createStateTree();

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
            migrateLegacyState (restoredState);
            parameters.replaceState (restoredState);
            applyDefaultGasSettings();

            // Always reset playback to GBS default on startup
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

TheGreatAmericanSpringAudioProcessor::StereoMode TheGreatAmericanSpringAudioProcessor::getStereoMode() const
{
    return toStereoMode (parameters.getRawParameterValue (stereoModeParameterID)->load());
}

bool TheGreatAmericanSpringAudioProcessor::shouldConvertMonoSourceToStereo() const
{
    return getStereoMode() == StereoMode::monoToStereo;
}

bool TheGreatAmericanSpringAudioProcessor::isMegaverbEngaged() const
{
    return getStereoMode() == StereoMode::megaverb;
}

bool TheGreatAmericanSpringAudioProcessor::isInputTubeEngaged() const
{
    return parameters.getRawParameterValue (inputTubeParameterID)->load() >= 0.5f;
}

bool TheGreatAmericanSpringAudioProcessor::isOutputTapeEngaged() const
{
    return parameters.getRawParameterValue (outputTapeParameterID)->load() >= 0.5f;
}

bool TheGreatAmericanSpringAudioProcessor::isDirtEngaged() const
{
    return parameters.getRawParameterValue (dirtParameterID)->load() >= 0.5f;
}

TheGreatAmericanSpringAudioProcessor::Dynamics TheGreatAmericanSpringAudioProcessor::getDynamics() const
{
    return toDynamics (parameters.getRawParameterValue (dynamicsParameterID)->load());
}

juce::StringArray TheGreatAmericanSpringAudioProcessor::getSignalChainLines() const
{
    // The Left channel's path only, since Right mirrors it. Returned as rows meant
    // to be drawn in a monospace font: the row above the path carries the feedback
    // arrows (and, in Parallel, the short tank), the row below carries the long
    // tank, so the two tank pairs read one above the other.
    const auto megaverb = isMegaverbEngaged();
    const auto routing = getIr2RoutingMode();
    const auto parallel = routing == Ir2RoutingMode::parallel;
    const auto extTanksEngaged = routing != Ir2RoutingMode::off;

    juce::String path;
    int feedbackInCentre = -1;
    int feedbackOutCentre = -1;
    int tankCentre = -1;

    // Appends a stage and hands back the column its text starts at.
    const auto add = [&path] (const juce::String& stage)
    {
        if (path.isNotEmpty() && ! path.endsWithChar (' '))
            path << " > ";

        const auto column = path.length();
        path << stage;
        return column;
    };

    const auto centreOf = [] (int column, const juce::String& text)
    {
        return column + (text.length() - 1) / 2;
    };

    path << "L: ";

    // Same shape as the Out token further down, so both ends read alike: the knob names
    // whichever circuit it is driving rather than the circuit trailing after an arrow.
    add (isInputTubeEngaged() ? "In: Tube" : "In");

    // Square brackets are reserved for the meters, so the feedback taps go bare.
    // MEGAVERB names the other channel instead of saying In and Out, since "from R"
    // and "to R" already say which end of the loop you are looking at. The cross is
    // an outright swap, so the Left path's feedback goes only to the Right; the
    // "L & R" wording covers a future blend that also feeds its own channel.
    const juce::String crossedWith = FeedbackBlock::crossCoupledAlsoFeedsOwnChannel ? "L & R" : "R";
    const auto feedbackInToken  = megaverb ? "%Fb from " + crossedWith : juce::String ("Fb In");
    const auto feedbackOutToken = megaverb ? "%Fb to "   + crossedWith : juce::String ("Fb Out");

    const auto addFeedbackIn = [&]
    {
        feedbackInCentre = centreOf (add (feedbackInToken), feedbackInToken);
    };

    // MEGAVERB sums the crossed feedback before the In meter, so the meter shows the
    // ping-pong; every other mode meters the fresh input first.
    if (megaverb)
    {
        addFeedbackIn();
        add ("[L In]");
    }
    else
    {
        add ("[L In]");
        addFeedbackIn();
    }

    if (! extTanksEngaged)
    {
        add ("Short");
    }
    else if (parallel)
    {
        // The two pairs run side by side, so the path shows only the summing point
        // and the tank names sit on the rows above and below it.
        const juce::String token ("+");
        tankCentre = centreOf (add (token), token);
    }
    else
    {
        add ("Short");
        add ("Long");
    }

    add (isDirtEngaged() ? "Gain > Dirt" : "Gain");

    add ("[L Wet]");

    // Comp / Limit hangs off the feedback RETURN leg (signal-path diagram v4), not the
    // wet path, so it is named on the Fb Out token instead of sitting inline above. The
    // arrow above still centres on "Fb Out" alone, so it points at the tap, not the
    // circuit the tap feeds.
    const auto dynamicsToken = getDynamics() == Dynamics::comp  ? juce::String (" + Comp")
                             : getDynamics() == Dynamics::limit ? juce::String (" + Lim")
                                                                : juce::String();

    feedbackOutCentre = centreOf (add (feedbackOutToken + dynamicsToken), feedbackOutToken);

    add ("Wet/Dry");

    // The Out knob drives whichever output circuits are switched in, so they are named
    // ON the knob rather than strung out after it: "Out: Tube & Tape" with both in,
    // "Out: Tube" or "Out: Tape" with one, plain "Out" with neither.
    //
    // The tube at this end follows the In pull, not a switch of its own: pulling In puts
    // the J201 on BOTH ends (chain.outputStage.setEnabled (inputTube, outputTape)). The
    // audio has always done that; the readout used to name the tube only at the input,
    // which read as though the output tube had been dropped.
    const auto outTube = isInputTubeEngaged();
    const auto outTape = isOutputTapeEngaged();
    juce::String outputToken ("Out");

    if (outTube || outTape)
    {
        outputToken << ": ";

        if (outTube)
            outputToken << "Tube";

        if (outTube && outTape)
            outputToken << " & ";

        if (outTape)
            outputToken << "Tape";
    }

    add (outputToken);

    add ("[L Out]");

    // Centres text on a column. Placements run left to right, so truncating at the
    // start column never clips something already placed.
    const auto placeAt = [] (juce::String& row, int column, const juce::String& text)
    {
        if (column < 0)
            return;

        const auto start = juce::jmax (0, column - (text.length() - 1) / 2);
        row = row.paddedRight (' ', start).substring (0, start) + text;
    };

    juce::String above;
    placeAt (above, feedbackInCentre, juce::String::charToString (juce::juce_wchar (0x2193)));   // down into the path

    if (parallel)
        placeAt (above, tankCentre, "Short");

    placeAt (above, feedbackOutCentre, juce::String::charToString (juce::juce_wchar (0x2191))); // up out of the path

    juce::StringArray lines;
    lines.add (above);
    lines.add (path);

    if (parallel)
    {
        juce::String below;
        placeAt (below, tankCentre, "Long");
        lines.add (below);
    }

    return lines;
}

bool TheGreatAmericanSpringAudioProcessor::shouldShowUnavailableTankControls() const
{
    return parameters.getRawParameterValue (showUnavailableTankControlsParameterID)->load() >= 0.5f;
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
    {
        // Show "power-chords-plexi.mp3" as "Power Chords Plexi": drop the
        // extension, turn hyphens into spaces, capitalise each word.
        auto name = juce::File (juce::String (source.displayPath)).getFileNameWithoutExtension()
                        .replaceCharacter ('-', ' ').replaceCharacter ('_', ' ');
        juce::StringArray words;
        words.addTokens (name, " ", "");
        words.removeEmptyStrings();

        for (auto& word : words)
            word = word.substring (0, 1).toUpperCase() + word.substring (1);

        names.add (words.joinIntoString (" "));
    }

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

namespace
{
    /*  Rev C hardware convention (2026-09-21): both filter pots LOWER their corner frequency as the
        knob turns clockwise.  On the filter-pot riser each gang ties its CW end to the wiper, so the
        resistance in circuit rises clockwise, and in both Sallen-Key sections more resistance means a
        lower corner.  Clockwise therefore means less bass cut on the HPF and darker on the LPF.

        A JUCE rotary slider always runs its minimum at full counter-clockwise and its maximum at full
        clockwise, so to make the plugin turn the same way as the panel we reverse the normalised
        mapping: normalised 0 (full CCW) is the TOP of the frequency range and normalised 1 (full CW)
        is the bottom.  The parameter's value is still plain Hz, and the skewed feel of the original
        range is preserved, just mirrored.  */
    juce::NormalisableRange<float> reversedCutoffRange (float lo, float hi, float skew)
    {
        const juce::NormalisableRange<float> forward (lo, hi, 0.01f, skew);

        return juce::NormalisableRange<float> (
            lo, hi,
            [forward] (float, float, float norm)  { return forward.convertFrom0to1 (1.0f - norm); },
            [forward] (float, float, float value) { return 1.0f - forward.convertTo0to1 (value); },
            [forward] (float, float, float value) { return forward.snapToLegalValue (value); });
    }
}

juce::AudioProcessorValueTreeState::ParameterLayout TheGreatAmericanSpringAudioProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;

    // Every level knob is the same +/-18 dB pot stage, linear in dB, unity at centre.
    const auto levelRange = juce::NormalisableRange<float> (levelMinDb, levelMaxDb, 0.1f);

    // The two plugin-only trims are not board pots, so they run down to -48 dB.
    const auto pluginTrimRange = juce::NormalisableRange<float> (pluginTrimMinDb, levelMaxDb, 0.1f);

    // Plugin only (not on the PCB): the very first gain stage.
    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { preInputLevelParameterID, 1 },
                                                              "Pre Input",
                                                              pluginTrimRange,
                                                              0.0f));

    // In (Solid State / Tube): first knob on the wet path. Rev C moved the pull onto its own
    // TUBE mini toggle in the panel's switch row, so this is a plain knob plus a separate switch.
    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { inputLevelParameterID, 2 },
                                                              "In",
                                                              levelRange,
                                                              0.0f));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { inputTubeParameterID, 1 },
                                                            "Tube",
                                                            false));

    // Gain: level into the Tube Screamer and the Comp / Limit circuit. Rev C: DIRT is its own toggle.
    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { gainParameterID, 1 },
                                                              "Gain",
                                                              levelRange,
                                                              0.0f));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { dirtParameterID, 1 },
                                                            "Dirt",
                                                            false));

    layout.add (std::make_unique<juce::AudioParameterChoice> (juce::ParameterID { dynamicsParameterID, 1 },
                                                               "Feedback Dynamics",
                                                               DirtDynamicsBlock::getDynamicsNames(),
                                                               1));   // Off

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { preHpfCutoffParameterID, 1 },
                                                              "HPF Cutoff",
                                                              reversedCutoffRange (1.0f, 4000.0f, 0.35f),
                                                              120.0f));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { postLpfCutoffParameterID, 1 },
                                                              "LPF Cutoff",
                                                              reversedCutoffRange (500.0f, 20000.0f, 0.35f),
                                                              16000.0f));

    layout.add (std::make_unique<juce::AudioParameterChoice> (juce::ParameterID { x2TanksParameterID, 1 },
                                                               "Ext Reverb Tanks",
                                                               juce::StringArray { "Off", "Series", "Parallel" },
                                                               2));

    // Default sits at noon: half and half in Parallel, 50% long added in Series. The
    // name here is the generic one the host sees; the on-screen label changes per mode.
    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { extTankMixParameterID, 1 },
                                                              "Short/Long Reverb Mix",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.5f,
                                                              juce::AudioParameterFloatAttributes()
                                                                  .withStringFromValueFunction ([] (float value, int)
                                                                                                { return shortLongMixText (value); })));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { feedbackAmountParameterID, 1 },
                                                              "Feedback",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.2f,
                                                              juce::AudioParameterFloatAttributes()
                                                                  .withStringFromValueFunction ([] (float value, int) { return percentText (value); })
                                                                  .withValueFromStringFunction ([] (const juce::String& text) { return percentValue (text); })));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { feedbackPhaseInvertParameterID, 1 },
                                                            "Feedback Phase Invert",
                                                            false));

    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { wetDryParameterID, 1 },
                                                              "Wet/Dry",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.5f,
                                                              juce::AudioParameterFloatAttributes()
                                                                  .withStringFromValueFunction ([] (float value, int) { return percentText (value); })
                                                                  .withValueFromStringFunction ([] (const juce::String& text) { return percentValue (text); })));

    // Out: the board's last knob, after the Wet/Dry mix. Rev C: TAPE is its own toggle.
    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { outputLevelParameterID, 2 },
                                                              "Out",
                                                              levelRange,
                                                              0.0f));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { outputTapeParameterID, 1 },
                                                            "Tape",
                                                            false));

    // Plugin only (not on the PCB): the very last gain stage.
    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { postOutputLevelParameterID, 1 },
                                                              "Post Output",
                                                              pluginTrimRange,
                                                              0.0f));

    layout.add (std::make_unique<juce::AudioParameterChoice> (juce::ParameterID { stereoModeParameterID, 1 },
                                                               "Setting",
                                                               juce::StringArray { "Stereo", "Mono > Stereo", "MEGAVERB" },
                                                               0));

    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { showUnavailableTankControlsParameterID, 1 },
                                                            "BYOIRs (Bring your own impulse responses)",
                                                            false));

    // Plugin only. 4x matches what the tube, tape and Tube Screamer stages already run
    // at, and is the default; the rest is there to trade CPU against alias rejection.
    layout.add (std::make_unique<juce::AudioParameterChoice> (juce::ParameterID { railOversamplingParameterID, 1 },
                                                               "Oversampling",
                                                               juce::StringArray { "Off", "2x", "4x", "8x" },
                                                               RailSaturator::defaultChoiceIndex));

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
    // "GBS default" preset: everything solid state, dynamics off
    setParameterPlainValue (preInputLevelParameterID, 0.0f);
    setParameterPlainValue (inputTubeParameterID, 0.0f);
    setParameterPlainValue (gainParameterID, 0.0f);
    setParameterPlainValue (dirtParameterID, 0.0f);
    setParameterPlainValue (dynamicsParameterID, 1.0f);             // Off
    setParameterPlainValue (outputTapeParameterID, 0.0f);
    setParameterPlainValue (postOutputLevelParameterID, 0.0f);
    setParameterPlainValue (stereoModeParameterID, 0.0f);           // Stereo
    setParameterPlainValue (preHpfCutoffParameterID, 100.0f);       // 100 Hz
    setParameterPlainValue (postLpfCutoffParameterID, 12000.0f);    // 12 kHz
    setParameterPlainValue (x2TanksParameterID, 0.0f);              // Ext Reverb Tanks: Off
    setParameterPlainValue (extTankMixParameterID, 0.5f);           // 100% short / 100% long
    setParameterPlainValue (feedbackAmountParameterID, 0.1f);       // 10%
    setParameterPlainValue (feedbackPhaseInvertParameterID, 0.0f);  // Normal
    setParameterPlainValue (wetDryParameterID, 0.5f);               // 50%
    setParameterPlainValue (inputLevelParameterID, 0.0f);           // 0 dB (unity)
    setParameterPlainValue (outputLevelParameterID, 0.0f);          // 0 dB (unity)
    setParameterPlainValue (showUnavailableTankControlsParameterID, 0.0f);
    assignDefaultTankIRs();
}

void TheGreatAmericanSpringAudioProcessor::applyGasPresetSettings()
{
    // "GAS default" preset: same as GBS except where noted
    setParameterPlainValue (preInputLevelParameterID, 0.0f);
    setParameterPlainValue (inputTubeParameterID, 1.0f);            // Vol pulled: tube in and out
    setParameterPlainValue (gainParameterID, 0.0f);
    setParameterPlainValue (dirtParameterID, 1.0f);                 // Gain pulled: Tube Screamer
    setParameterPlainValue (dynamicsParameterID, 1.0f);             // Off
    setParameterPlainValue (outputTapeParameterID, 1.0f);           // Output pulled: tape
    setParameterPlainValue (postOutputLevelParameterID, 0.0f);
    setParameterPlainValue (stereoModeParameterID, 0.0f);           // Stereo
    setParameterPlainValue (preHpfCutoffParameterID, 250.0f);       // 250 Hz
    setParameterPlainValue (postLpfCutoffParameterID, 8000.0f);     // 8 kHz
    setParameterPlainValue (x2TanksParameterID, 1.0f);              // Series
    setParameterPlainValue (extTankMixParameterID, 0.5f);           // 100% short / 100% long
    setParameterPlainValue (feedbackAmountParameterID, 0.25f);      // 25%
    setParameterPlainValue (feedbackPhaseInvertParameterID, 0.0f);  // Normal
    setParameterPlainValue (wetDryParameterID, 0.5f);               // 50%
    setParameterPlainValue (inputLevelParameterID, 0.0f);           // 0 dB (unity)
    setParameterPlainValue (outputLevelParameterID, 0.0f);          // 0 dB (unity)
    setParameterPlainValue (showUnavailableTankControlsParameterID, 0.0f);
    assignDefaultTankIRs();
}

bool TheGreatAmericanSpringAudioProcessor::loadPreset (int index)
{
    const auto factoryPresetNames = getFactoryPresetNames();

    if (index == 0)
        applyDefaultGasSettings();   // GBS default
    else if (index == 1)
        applyGasPresetSettings();    // GAS default
    else
    {
        const auto userPresetFiles = getUserPresetFiles();
        const auto userPresetIndex = index - factoryPresetNames.size();

        if (! juce::isPositiveAndBelow (userPresetIndex, userPresetFiles.size()))
            return false;

        if (auto presetXml = juce::parseXML (userPresetFiles.getReference (userPresetIndex)))
        {
            const auto presetName = userPresetFiles.getReference (userPresetIndex).getFileNameWithoutExtension();
            return applyPresetState (juce::ValueTree::fromXml (*presetXml), presetName);
        }

        return false;
    }

    playbackFilePath = getEmbeddedPlaybackSources().front().displayPath;

    if (isPrepared)
    {
        loadTankIRFromCurrentPath (TankSlot::left1);
        loadTankIRFromCurrentPath (TankSlot::right1);
        loadTankIRFromCurrentPath (TankSlot::left2);
        loadTankIRFromCurrentPath (TankSlot::right2);
        loadSelectedPlaybackSource();
    }

    sendChangeMessage();
    return true;
}

juce::StringArray TheGreatAmericanSpringAudioProcessor::getPresetNames() const
{
    auto names = getFactoryPresetNames();

    for (const auto& presetFile : getUserPresetFiles())
        names.add (presetFile.getFileNameWithoutExtension());

    return names;
}

bool TheGreatAmericanSpringAudioProcessor::saveUserPreset (const juce::String& presetName)
{
    const auto fileName = sanitizePresetFileName (presetName);

    if (fileName.isEmpty())
        return false;

    const auto presetDirectory = getUserPresetDirectory();
    presetDirectory.createDirectory();

    auto state = createStateTree();
    state.setProperty (presetNameProperty, fileName, nullptr);

    if (auto xml = state.createXml())
        return xml->writeTo (presetDirectory.getChildFile (fileName + ".xml"));

    return false;
}

bool TheGreatAmericanSpringAudioProcessor::applyPresetState (juce::ValueTree restoredState,
                                                             const juce::String& presetName)
{
    if (! restoredState.hasType (parameters.state.getType()))
        return false;

    migrateLegacyState (restoredState);
    parameters.replaceState (restoredState);
    leftTank1IrPath = restoredState.getProperty (getTankIrPathPropertyName (TankSlot::left1)).toString();
    rightTank1IrPath = restoredState.getProperty (getTankIrPathPropertyName (TankSlot::right1)).toString();
    leftTank2IrPath = restoredState.getProperty (getTankIrPathPropertyName (TankSlot::left2)).toString();
    rightTank2IrPath = restoredState.getProperty (getTankIrPathPropertyName (TankSlot::right2)).toString();
    playbackFilePath = restoredState.getProperty ("playbackFilePath",
                                                  getEmbeddedPlaybackSources().front().displayPath).toString();
    playbackActive = false;

    if (isPrepared)
    {
        loadTankIRFromCurrentPath (TankSlot::left1);
        loadTankIRFromCurrentPath (TankSlot::right1);
        loadTankIRFromCurrentPath (TankSlot::left2);
        loadTankIRFromCurrentPath (TankSlot::right2);

        const auto playbackSourceIndex = getPlaybackSourceIndexForPath (playbackFilePath);

        if (playbackSourceIndex >= 0)
        {
            loadSelectedPlaybackSource();
        }
        else if (const auto restoredPlaybackFile = resolvePlaybackFile (playbackFilePath);
                 restoredPlaybackFile.existsAsFile())
        {
            loadPlaybackFile (restoredPlaybackFile);
        }
        else
        {
            loadSelectedPlaybackSource();
        }
    }

    juce::ignoreUnused (presetName);
    sendChangeMessage();
    return true;
}

void TheGreatAmericanSpringAudioProcessor::migrateLegacyState (juce::ValueTree& restoredState)
{
    // Pre-Rev-A states stored Ext Reverb Tanks as a bool.
    const auto restoredIr2Routing = restoredState.getProperty (x2TanksParameterID);

    if (restoredIr2Routing.isBool())
        restoredState.setProperty (x2TanksParameterID, static_cast<bool> (restoredIr2Routing) ? 2 : 0, nullptr);

    // Rev A / Rev B states: "Mono Source To Stereo" toggle becomes the Source
    // switch, and the old Mode / Drive controls map onto the Rev C pulls.
    const auto findParam = [&restoredState] (const juce::String& id) -> juce::ValueTree
    {
        return restoredState.getChildWithProperty ("id", id);
    };

    if (auto mono = findParam ("monoSourceToStereo"); mono.isValid() && ! findParam (stereoModeParameterID).isValid())
    {
        const auto converting = static_cast<float> (mono.getProperty ("value", 0.0f)) >= 0.5f;
        auto node = juce::ValueTree ("PARAM");
        node.setProperty ("id", stereoModeParameterID, nullptr);
        node.setProperty ("value", converting ? 1.0f : 0.0f, nullptr);
        restoredState.appendChild (node, nullptr);
    }

    if (auto mode = findParam ("mode"); mode.isValid() && ! findParam (dirtParameterID).isValid())
    {
        // Old Mode order: Clean, Tube, Tape, Tube Screamer, Opto, FET, VCA.
        const auto index = juce::roundToInt (static_cast<float> (mode.getProperty ("value", 0.0f)));
        const auto add = [&restoredState] (const juce::String& id, float value)
        {
            auto node = juce::ValueTree ("PARAM");
            node.setProperty ("id", id, nullptr);
            node.setProperty ("value", value, nullptr);
            restoredState.appendChild (node, nullptr);
        };

        add (inputTubeParameterID, index == 1 ? 1.0f : 0.0f);
        add (outputTapeParameterID, index == 2 ? 1.0f : 0.0f);
        add (dirtParameterID, index == 3 ? 1.0f : 0.0f);
        add (dynamicsParameterID, (index == 4 || index == 5) ? 0.0f : index == 6 ? 2.0f : 1.0f);
    }

    if (auto drive = findParam ("drive"); drive.isValid() && ! findParam (gainParameterID).isValid())
    {
        auto node = juce::ValueTree ("PARAM");
        node.setProperty ("id", gainParameterID, nullptr);
        node.setProperty ("value", juce::jlimit (levelMinDb, levelMaxDb, static_cast<float> (drive.getProperty ("value", 0.0f))), nullptr);
        restoredState.appendChild (node, nullptr);
    }
}

juce::File TheGreatAmericanSpringAudioProcessor::getUserPresetDirectory() const
{
    return juce::File::getSpecialLocation (juce::File::userApplicationDataDirectory)
        .getChildFile ("Illicit Apothecary")
        .getChildFile ("The Great American Spring")
        .getChildFile ("Presets");
}

juce::Array<juce::File> TheGreatAmericanSpringAudioProcessor::getUserPresetFiles() const
{
    juce::Array<juce::File> presetFiles;
    const auto presetDirectory = getUserPresetDirectory();

    if (! presetDirectory.isDirectory())
        return presetFiles;

    presetDirectory.findChildFiles (presetFiles, juce::File::findFiles, false, "*.xml");
    std::sort (presetFiles.begin(), presetFiles.end(),
               [] (const juce::File& a, const juce::File& b)
               {
                   return a.getFileNameWithoutExtension().compareIgnoreCase (b.getFileNameWithoutExtension()) < 0;
               });
    return presetFiles;
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
    predelayModulationBuffer.setSize (5, samplesPerBlock);
    monoLeftBuffer.setSize (1, samplesPerBlock);
    monoRightBuffer.setSize (1, samplesPerBlock);
    monoLeftSecondaryBuffer.setSize (1, samplesPerBlock);
    monoRightSecondaryBuffer.setSize (1, samplesPerBlock);
    monoLeftSeriesBypassBuffer.setSize (1, samplesPerBlock);
    monoRightSeriesBypassBuffer.setSize (1, samplesPerBlock);

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
    monoLeftSeriesBypassBuffer.clear();
    monoRightSeriesBypassBuffer.clear();
}

void TheGreatAmericanSpringAudioProcessor::loadPlaybackIntoBuffer (juce::AudioBuffer<float>& targetBuffer, int numSamples)
{
    targetBuffer.clear();

    if (! playbackActive || playbackBuffer.getNumSamples() == 0 || currentSampleRate <= 0.0)
        return;

    const auto positionIncrement = playbackSourceSampleRate / currentSampleRate;
    const auto sourceLength = playbackBuffer.getNumSamples();
    const auto sourceLengthDouble = static_cast<double> (sourceLength);
    auto* left = targetBuffer.getWritePointer (0);
    auto* right = targetBuffer.getWritePointer (1);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        // Loop: once the read head passes the end of the clip it wraps back to
        // the start, so a demo keeps playing until Stop is pressed.
        while (playbackReadPosition >= sourceLengthDouble)
            playbackReadPosition -= sourceLengthDouble;

        const auto baseIndex = static_cast<int> (playbackReadPosition);
        // The interpolation partner of the last sample is the first sample, so
        // the seam between loop passes is interpolated rather than stepped.
        const auto nextIndex = (baseIndex + 1) % sourceLength;

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
    return ! shouldConvertMonoSourceToStereo()
        && (getTotalNumInputChannels() == 1
            || lastMonoSourceWithoutStereoConversion.load (std::memory_order_relaxed));
}

bool TheGreatAmericanSpringAudioProcessor::detectMonoExternalInput (int numSamples) const
{
    if (shouldConvertMonoSourceToStereo())
        return false;

    if (getTotalNumInputChannels() == 1)
        return true;

    const auto* left = externalInputBuffer.getReadPointer (0);
    const auto* right = externalInputBuffer.getReadPointer (1);
    auto maximumDifference = 0.0f;
    auto maximumLeftMagnitude = 0.0f;
    auto maximumRightMagnitude = 0.0f;

    for (int sample = 0; sample < numSamples; ++sample)
    {
        maximumDifference = juce::jmax (maximumDifference, std::abs (left[sample] - right[sample]));
        maximumLeftMagnitude = juce::jmax (maximumLeftMagnitude, std::abs (left[sample]));
        maximumRightMagnitude = juce::jmax (maximumRightMagnitude, std::abs (right[sample]));
    }

    // Only flag as mono-L when the left channel carries actual signal but the right
    // is silent or identical. Pure silence on both channels (e.g. at startup / no
    // audio playing) must NOT be treated as mono-L or the right output gets muted.
    return maximumLeftMagnitude > 1.0e-7f
        && (maximumRightMagnitude <= 1.0e-7f || maximumDifference <= 1.0e-6f);
}

void TheGreatAmericanSpringAudioProcessor::applyWetPredelay (int numSamples)
{
    auto* wetLeft = wetInputBaseBuffer.getWritePointer (0);
    auto* wetRight = wetInputBaseBuffer.getWritePointer (1);
    auto* delayedLeft = wetStereoBuffer.getWritePointer (0);
    auto* delayedRight = wetStereoBuffer.getWritePointer (1);
    const auto* leftDelay  = predelayModulationBuffer.getReadPointer (0);   // primary L
    const auto* rightDelay = predelayModulationBuffer.getReadPointer (2);   // primary R

    for (int sample = 0; sample < numSamples; ++sample)
    {
        wetPredelayLeft.pushSample (0, wetLeft[sample]);
        wetPredelayRight.pushSample (0, wetRight[sample]);
        delayedLeft[sample]  = wetPredelayLeft.popSample (0, leftDelay[sample]);
        delayedRight[sample] = wetPredelayRight.popSample (0, rightDelay[sample]);
    }
}

void TheGreatAmericanSpringAudioProcessor::updatePredelayModulation (int numSamples)
{
    // predelayModulationBuffer channel map (per sample, in samples):
    //   0 = primary L (4AB1C1B), 1 = feedback, 2 = primary R (4AB1C1B),
    //   3 = 2nd L (9EB2C1B),    4 = 2nd R (9EB3C1B)
    auto* primaryLeftOut  = predelayModulationBuffer.getWritePointer (0);
    auto* feedbackOut     = predelayModulationBuffer.getWritePointer (1);
    auto* primaryRightOut = predelayModulationBuffer.getWritePointer (2);
    auto* secondaryLeftOut  = predelayModulationBuffer.getWritePointer (3);
    auto* secondaryRightOut = predelayModulationBuffer.getWritePointer (4);

    const auto phaseIncrement = predelayLfoFrequencyHz / currentSampleRate;
    const auto msToSamples = 0.001f * static_cast<float> (currentSampleRate);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        predelayLfoPhase += phaseIncrement;

        while (predelayLfoPhase >= 1.0)
        {
            predelayLfoPhase -= 1.0;

            // Pick a fresh, independent random target for each of the four lanes.
            for (int lane = 0; lane < 4; ++lane)
            {
                const auto minMs = predelayLaneMinMs[static_cast<size_t> (lane)];
                const auto maxMs = predelayLaneMaxMs[static_cast<size_t> (lane)];
                predelayTargetMs[lane] = juce::jmap (predelayRandom.nextFloat(),
                                                     static_cast<float> (minMs),
                                                     static_cast<float> (maxMs));
                predelayMsSmoothed[lane].setTargetValue (predelayTargetMs[lane]);
            }
        }

        const auto priL = predelayMsSmoothed[0].getNextValue() * msToSamples;
        const auto priR = predelayMsSmoothed[1].getNextValue() * msToSamples;
        const auto secL = predelayMsSmoothed[2].getNextValue() * msToSamples;
        const auto secR = predelayMsSmoothed[3].getNextValue() * msToSamples;

        primaryLeftOut[sample]    = priL;
        primaryRightOut[sample]   = priR;
        secondaryLeftOut[sample]  = secL;
        secondaryRightOut[sample] = secR;
        feedbackOut[sample]       = 0.5f * (priL + priR) / 3.0f;
    }
}

void TheGreatAmericanSpringAudioProcessor::scrubBuffer (juce::AudioBuffer<float>& buffer, int numSamples, float hardCeiling) const
{
    const auto clamping = hardCeiling > 0.0f;

    for (int channel = 0; channel < buffer.getNumChannels(); ++channel)
    {
        auto* samples = buffer.getWritePointer (channel);

        for (int sample = 0; sample < numSamples; ++sample)
        {
            auto value = samples[sample];

            if (! std::isfinite (value))
                value = 0.0f;

            samples[sample] = clamping ? juce::jlimit (-hardCeiling, hardCeiling, value) : value;
        }
    }
}

void TheGreatAmericanSpringAudioProcessor::rebuildRailSaturators()
{
    const auto choice = static_cast<int> (parameters.getRawParameterValue (railOversamplingParameterID)->load());
    const auto order = RailSaturator::factorOrderForChoice (choice);
    const auto outputChannels = juce::jmax (1, getTotalNumOutputChannels());

    // The four internal nodes are always stereo; the output node follows the host bus.
    for (auto* saturator : { &wetInputRail, &wetStereoRail, &wetAfterFeedbackRail, &feedbackReturnRail })
        saturator->prepare (preparedSampleRate, preparedBlockSize, 2, order);

    outputRail.prepare (preparedSampleRate, preparedBlockSize, outputChannels, order);

    updateReportedLatency();
}

void TheGreatAmericanSpringAudioProcessor::updateReportedLatency()
{
    // Both stages ask their oversamplers for integer latency, so this sum is already a
    // whole number and the rounding below only guards against float drift.
    const auto samples = chain.outputStage.getLatencyInSamples()
                       + outputRail.getLatencyInSamples();

    setLatencySamples (juce::roundToInt (samples));
}

void TheGreatAmericanSpringAudioProcessor::applySecondaryTankPredelay (
    juce::AudioBuffer<float>& monoBuffer,
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& delayLine,
    const float* delaySamplesPerSample,
    int numSamples)
{
    auto* samples = monoBuffer.getWritePointer (0);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        delayLine.pushSample (0, samples[sample]);
        samples[sample] = delayLine.popSample (0, delaySamplesPerSample[sample]);
    }
}

DirtDynamicsBlock::Parameters TheGreatAmericanSpringAudioProcessor::getDirtDynamicsParameters() const
{
    DirtDynamicsBlock::Parameters p;
    p.gainDb = parameters.getRawParameterValue (gainParameterID)->load();
    p.dirt = isDirtEngaged();
    // Always Off in the wet path. Signal-path diagram v4 (2026-09-30) moved the
    // Comp / Off / Limit circuit into the feedback return leg, so the switch now
    // drives chain.feedbackDynamics instead of this block.
    p.dynamics = DirtDynamicsBlock::Dynamics::off;
    p.preHpfCutoffHz = parameters.getRawParameterValue (preHpfCutoffParameterID)->load();
    p.postLpfCutoffHz = parameters.getRawParameterValue (postLpfCutoffParameterID)->load();
    p.filterQ = filterQ;
    return p;
}

TheGreatAmericanSpringAudioProcessor::StereoMode TheGreatAmericanSpringAudioProcessor::toStereoMode (float parameterValue)
{
    switch (juce::jlimit (0, 2, juce::roundToInt (parameterValue)))
    {
        case 1:  return StereoMode::monoToStereo;
        case 2:  return StereoMode::megaverb;
        case 0:
        default: return StereoMode::stereo;
    }
}

TheGreatAmericanSpringAudioProcessor::Dynamics TheGreatAmericanSpringAudioProcessor::toDynamics (float parameterValue)
{
    switch (juce::jlimit (0, 2, juce::roundToInt (parameterValue)))
    {
        case 0:  return Dynamics::comp;
        case 2:  return Dynamics::limit;
        case 1:
        default: return Dynamics::off;
    }
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
