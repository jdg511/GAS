import re, sys

def load(p):
    b = open(p, 'rb').read()
    crlf = b'\r\n' in b
    s = b.decode('utf-8').replace('\r\n', '\n')
    return s, crlf

def save(p, s, crlf):
    if crlf:
        s = s.replace('\n', '\r\n')
    open(p, 'wb').write(s.encode('utf-8'))

def rep(s, old, new, count=1):
    n = s.count(old)
    assert n == count, f"expected {count} match(es), got {n} for:\n{old[:120]}"
    return s.replace(old, new)

def cut_between(s, start, end, new):
    i = s.index(start); j = s.index(end, i) + len(end)
    return s[:i] + new + s[j:]

# ============================================================ PluginProcessor.h
p = 'Source/PluginProcessor.h'; s, crlf = load(p)

s = rep(s, """    /** Where the Drive + clipping/dynamics circuit sits in the chain. */
    enum class CircuitPlacement
    {
        /** Inside the wet path, after the tanks and crossfade. Original spot:
            the circuit only ever sees reverb, never the dry signal. */
        wetPath = 0,

        /** Straight after Input Level, before the dry/wet split, so it colours
            everything the plugin hears including the dry path. */
        input,

        /** After the wet/dry mixer and immediately before Output Level, so it
            works on the finished blend. */
        output
    };""",
"""    /** Where the Drive + clipping/dynamics circuit sits in the chain. In every
        position the circuit is wet-side only: the dry path never passes through it. */
    enum class CircuitPlacement
    {
        /** Inside the wet path, after the tanks and before the feedback block.
            Original spot. */
        wetPath = 0,

        /** Straight after Input Level on the wet side of the dry/wet split, so
            it colours what is fed into the tanks but not the dry signal. */
        input,

        /** At the very end of the wet path, after the feedback block and right
            before the wet/dry mixer. */
        output
    };""")

s = rep(s, "    bool shouldConvertMonoSourceToStereo() const;\n", "    bool isMegaverbEnabled() const;\n")
s = rep(s, "    bool isCrossfadeAvailableForCurrentLayout() const;\n", "")
s = rep(s, '    static constexpr auto crossfadeAmountParameterID = "crossfadeAmount";\n', "")
s = rep(s, '    static constexpr auto preHpfResonanceParameterID = "preHpfResonance";\n', "")
s = rep(s, '    static constexpr auto postLpfResonanceParameterID = "postLpfResonance";\n', "")
s = rep(s, '    static constexpr auto monoSourceToStereoParameterID = "monoSourceToStereo";\n',
           '    static constexpr auto megaverbParameterID = "megaverb";\n')
s = rep(s, """    static constexpr float sanitizeClampGain = 3.9811f;
""", """    static constexpr float sanitizeClampGain = 3.9811f;

    /** Fixed Q for the circuit's pre-HPF and post-LPF: 1/sqrt(2), a Butterworth
        response. The Q knobs were removed 2026-09-12. */
    static constexpr float filterQ = 0.70710678f;
""")
s = rep(s, "    bool isMonoSourceWithoutStereoConversion() const;\n    bool detectMonoExternalInput (int numSamples) const;\n", "")
s = rep(s, "    void applyWetPredelay (int numSamples);\n", "")
s = rep(s, """    FilterClipperBlock::Parameters getFilterClipperParameters() const;
""", """    FilterClipperBlock::Parameters getFilterClipperParameters() const;

    /** Runs one complete reverb path (primary predelay -> main tank -> Ext
        Reverb Tanks routing) on a mono input, leaving the result in channel 0
        of `primary`. `secondary` is scratch. Returns the Ext-meter peak (the
        level fed into the ext tank), or 0 when routing is Off. */
    float processTankPath (const float* input,
                           juce::AudioBuffer<float>& primary,
                           juce::AudioBuffer<float>& secondary,
                           juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& primaryPredelay,
                           juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& secondaryPredelay,
                           TankIRBlock& tank,
                           TankIRBlock& tankSecondary,
                           const float* primaryDelaySamples,
                           const float* secondaryDelaySamples,
                           Ir2RoutingMode routing,
                           float extTankMix,
                           int numSamples);
""")
s = rep(s, "    std::atomic<bool> lastMonoSourceWithoutStereoConversion { false };\n",
           "    bool lastMegaverb = false;\n")
save(p, s, crlf)

# ============================================================ ModularFxChain.h
p = 'Source/DSP/ModularFxChain.h'; s, crlf = load(p)
s = rep(s, '#include "StereoTankCrossfadeBlock.h"\n', "")
s = rep(s, "        stereoTankCrossfade.prepare (sampleRate, maximumBlockSize);\n", "")
s = rep(s, "        stereoTankCrossfade.reset();\n", "")
s = rep(s, "    StereoTankCrossfadeBlock stereoTankCrossfade;\n", "")
save(p, s, crlf)

# ============================================================ PluginProcessor.cpp
p = 'Source/PluginProcessor.cpp'; s, crlf = load(p)

# reset(): track megaverb
s = rep(s, "    lastIr2RoutingMode = getIr2RoutingMode();\n    inputGainSmoothed.setCurrentAndTargetValue (",
           "    lastIr2RoutingMode = getIr2RoutingMode();\n    lastMegaverb = isMegaverbEnabled();\n    inputGainSmoothed.setCurrentAndTargetValue (")

# mono fold + mode switch reset, replacing the dead mono-detection line
s = rep(s, """    // The plugin always stays on its stereo processing path.
    // The optional mono-to-stereo toggle is handled when copying mono input in buildExternalInput().
    lastMonoSourceWithoutStereoConversion.store (false, std::memory_order_relaxed);
""", """    // MEGAVERB (replaces the old mono mode). Switching modes re-routes the
    // whole tank section, so flush the tanks, predelays and feedback so the old
    // routing's tail does not bleed into the new one.
    const auto megaverb = isMegaverbEnabled();

    if (megaverb != lastMegaverb)
    {
        chain.leftTank.reset();
        chain.rightTank.reset();
        chain.leftTankSecondary.reset();
        chain.rightTankSecondary.reset();
        wetPredelayLeft.reset();
        wetPredelayRight.reset();
        secondaryLeftTankPredelay.reset();
        secondaryRightTankPredelay.reset();
        chain.feedback.reset();
        feedbackReturnBuffer.clear();
        lastMegaverb = megaverb;
    }

    if (megaverb)
    {
        // Fold L+R down to one mono stream (0.5 * (L + R): identical channels
        // come through at unity). Done before the dry tap, so in MEGAVERB the
        // dry signal is that same mono fold on both outputs.
        auto* left = externalInputBuffer.getWritePointer (0);
        auto* right = externalInputBuffer.getWritePointer (1);

        for (int sample = 0; sample < numSamples; ++sample)
        {
            const auto mono = 0.5f * (left[sample] + right[sample]);
            left[sample] = mono;
            right[sample] = mono;
        }
    }
""")

# the tank section: from predelay modulation through the (removed) crossfade
new_tanks = """    updatePredelayModulation (numSamples);

    const auto ir2RoutingMode = getIr2RoutingMode();
    const auto extTankMix = parameters.getRawParameterValue (extTankMixParameterID)->load();

    if (ir2RoutingMode != lastIr2RoutingMode)
    {
        secondaryLeftTankPredelay.reset();
        secondaryRightTankPredelay.reset();
        monoLeftSecondaryBuffer.clear();
        monoRightSecondaryBuffer.clear();
        lastIr2RoutingMode = ir2RoutingMode;
    }

    // predelayModulationBuffer lanes: 0 = primary L, 2 = primary R,
    // 3 = ext L, 4 = ext R (lane 1 is the feedback predelay, used below).
    const auto* primaryLeftDelay    = predelayModulationBuffer.getReadPointer (0);
    const auto* primaryRightDelay   = predelayModulationBuffer.getReadPointer (2);
    const auto* secondaryLeftDelay  = predelayModulationBuffer.getReadPointer (3);
    const auto* secondaryRightDelay = predelayModulationBuffer.getReadPointer (4);

    float extMeter = 0.0f;

    if (megaverb)
    {
        // MEGAVERB: the single mono stream runs the WHOLE left reverb path
        // (predelay L -> main tank L -> Ext routing with ext tank L), and that
        // result is then fed into the START of the right reverb path and runs
        // all of it too (predelay R -> main tank R -> Ext routing with ext tank
        // R). Off / Series / Parallel applies identically on both passes. The
        // R-path output is the wet signal (dual mono), so the feedback block
        // below returns the END of the R path to the START of the L path.
        extMeter = juce::jmax (extMeter,
            processTankPath (wetInputBaseBuffer.getReadPointer (0), monoLeftBuffer, monoLeftSecondaryBuffer,
                             wetPredelayLeft, secondaryLeftTankPredelay, chain.leftTank, chain.leftTankSecondary,
                             primaryLeftDelay, secondaryLeftDelay, ir2RoutingMode, extTankMix, numSamples));

        extMeter = juce::jmax (extMeter,
            processTankPath (monoLeftBuffer.getReadPointer (0), monoRightBuffer, monoRightSecondaryBuffer,
                             wetPredelayRight, secondaryRightTankPredelay, chain.rightTank, chain.rightTankSecondary,
                             primaryRightDelay, secondaryRightDelay, ir2RoutingMode, extTankMix, numSamples));

        wetStereoBuffer.copyFrom (0, 0, monoRightBuffer, 0, 0, numSamples);
        wetStereoBuffer.copyFrom (1, 0, monoRightBuffer, 0, 0, numSamples);
    }
    else
    {
        // Stereo: the L and R reverb paths run side by side, each fed by its
        // own input channel plus its own feedback return.
        extMeter = juce::jmax (extMeter,
            processTankPath (wetInputBaseBuffer.getReadPointer (0), monoLeftBuffer, monoLeftSecondaryBuffer,
                             wetPredelayLeft, secondaryLeftTankPredelay, chain.leftTank, chain.leftTankSecondary,
                             primaryLeftDelay, secondaryLeftDelay, ir2RoutingMode, extTankMix, numSamples));

        extMeter = juce::jmax (extMeter,
            processTankPath (wetInputBaseBuffer.getReadPointer (1), monoRightBuffer, monoRightSecondaryBuffer,
                             wetPredelayRight, secondaryRightTankPredelay, chain.rightTank, chain.rightTankSecondary,
                             primaryRightDelay, secondaryRightDelay, ir2RoutingMode, extTankMix, numSamples));

        wetStereoBuffer.copyFrom (0, 0, monoLeftBuffer, 0, 0, numSamples);
        wetStereoBuffer.copyFrom (1, 0, monoRightBuffer, 0, 0, numSamples);
    }

    // Ext Tank meter: the very last thing before audio enters the Ext Reverb
    // Tanks (after the ext predelay, and after the +6 dB gain in Series).
    // Reads empty when the Ext Reverb Tanks are Off.
    extTankMeterPeak.store (extMeter, std::memory_order_relaxed);
"""
s = cut_between(s, "    updatePredelayModulation (numSamples);\n",
                   "    chain.stereoTankCrossfade.process (wetStereoBuffer, numSamples);\n", new_tanks)

# accessor rename + remove crossfade availability
s = rep(s, """bool TheGreatAmericanSpringAudioProcessor::shouldConvertMonoSourceToStereo() const
{
    return parameters.getRawParameterValue (monoSourceToStereoParameterID)->load() >= 0.5f;
}""", """bool TheGreatAmericanSpringAudioProcessor::isMegaverbEnabled() const
{
    return parameters.getRawParameterValue (megaverbParameterID)->load() >= 0.5f;
}""")
s = rep(s, """bool TheGreatAmericanSpringAudioProcessor::isCrossfadeAvailableForCurrentLayout() const
{
    return ! isMonoSourceWithoutStereoConversion();
}

""", "")

# parameter layout
s = rep(s, """    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { crossfadeAmountParameterID, 1 },
                                                              "Crossfade Amount",
                                                              juce::NormalisableRange<float> (0.0f, 1.0f, 0.0001f),
                                                              0.2f));

""", "")
s = rep(s, """    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { preHpfResonanceParameterID, 1 },
                                                              "HPF Q",
                                                              juce::NormalisableRange<float> (0.25f, 8.0f, 0.001f, 0.5f),
                                                              0.707f));

""", "")
s = rep(s, """    layout.add (std::make_unique<juce::AudioParameterFloat> (juce::ParameterID { postLpfResonanceParameterID, 1 },
                                                              "LPF Q",
                                                              juce::NormalisableRange<float> (0.25f, 8.0f, 0.001f, 0.5f),
                                                              0.707f));

""", "")
s = rep(s, """    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { monoSourceToStereoParameterID, 1 },
                                                            "Mono Source To Stereo",
                                                            false));""",
"""    // MEGAVERB replaces the old "Mono Source To Stereo" mode: L+R are folded to
    // mono and run the left reverb path then the right reverb path in series.
    layout.add (std::make_unique<juce::AudioParameterBool> (juce::ParameterID { megaverbParameterID, 1 },
                                                            "MEGAVERB",
                                                            false));""")

# presets
s = rep(s, "    setParameterPlainValue (preHpfResonanceParameterID, 1.0f);      // Q = 1\n", "", count=2)
s = rep(s, "    setParameterPlainValue (postLpfResonanceParameterID, 1.0f);     // Q = 1\n", "", count=2)
s = rep(s, "    setParameterPlainValue (crossfadeAmountParameterID, 0.0f);      // 0\n", "")
s = rep(s, "    setParameterPlainValue (crossfadeAmountParameterID, 0.25f);     // 25%\n", "")
s = rep(s, "    setParameterPlainValue (monoSourceToStereoParameterID, 0.0f);\n",
           "    setParameterPlainValue (megaverbParameterID, 0.0f);             // Stereo\n", count=2)

# playback: a mono file always feeds both channels now
s = rep(s, """        const auto sourceRight0 = playbackBuffer.getNumChannels() > 1 ? playbackBuffer.getSample (1, baseIndex)
                                                                       : shouldConvertMonoSourceToStereo() ? sourceLeft0 : 0.0f;
        const auto sourceRight1 = playbackBuffer.getNumChannels() > 1 ? playbackBuffer.getSample (1, nextIndex)
                                                                       : shouldConvertMonoSourceToStereo() ? sourceLeft1 : 0.0f;""",
"""        const auto sourceRight0 = playbackBuffer.getNumChannels() > 1 ? playbackBuffer.getSample (1, baseIndex) : sourceLeft0;
        const auto sourceRight1 = playbackBuffer.getNumChannels() > 1 ? playbackBuffer.getSample (1, nextIndex) : sourceLeft1;""")

# buildExternalInput: mono host input feeds both channels
s = rep(s, """    if (getTotalNumInputChannels() > 1 && hostBuffer.getNumChannels() > 1)
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
}""",
"""    // A mono host input is always presented to the plugin on both channels.
    if (getTotalNumInputChannels() > 1 && hostBuffer.getNumChannels() > 1)
        externalInputBuffer.copyFrom (1, 0, hostBuffer, 1, 0, numSamples);
    else
        externalInputBuffer.copyFrom (1, 0, hostBuffer, 0, 0, numSamples);

    wetAfterFeedbackBuffer.clear();
    loadPlaybackIntoBuffer (wetAfterFeedbackBuffer, numSamples);

    externalInputBuffer.addFrom (0, 0, wetAfterFeedbackBuffer, 0, 0, numSamples);
    externalInputBuffer.addFrom (1, 0, wetAfterFeedbackBuffer, 1, 0, numSamples);
}""")

# remove mono detection helpers and applyWetPredelay; add processTankPath
i = s.index("bool TheGreatAmericanSpringAudioProcessor::isMonoSourceWithoutStereoConversion() const\n")
j = s.index("void TheGreatAmericanSpringAudioProcessor::updatePredelayModulation (int numSamples)\n")
new_helper = """float TheGreatAmericanSpringAudioProcessor::processTankPath (const float* input,
                                                              juce::AudioBuffer<float>& primary,
                                                              juce::AudioBuffer<float>& secondary,
                                                              juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& primaryPredelay,
                                                              juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Linear>& secondaryPredelay,
                                                              TankIRBlock& tank,
                                                              TankIRBlock& tankSecondary,
                                                              const float* primaryDelaySamples,
                                                              const float* secondaryDelaySamples,
                                                              Ir2RoutingMode routing,
                                                              float extTankMix,
                                                              int numSamples)
{
    // Primary predelay (LFO-modulated) into channel 0 of `primary`.
    auto* out = primary.getWritePointer (0);

    for (int sample = 0; sample < numSamples; ++sample)
    {
        primaryPredelay.pushSample (0, input[sample]);
        out[sample] = primaryPredelay.popSample (0, primaryDelaySamples[sample]);
    }

    float extPeak = 0.0f;

    if (routing == Ir2RoutingMode::parallel)
    {
        // Parallel: the ext tank branches from the path input, BEFORE the
        // primary predelay, and runs alongside the main tank. In hardware this
        // is the 9EB2C1B / 9EB3C1B tank path beside the 4AB1C1B path.
        secondary.copyFrom (0, 0, input, numSamples);
        applySecondaryTankPredelay (secondary, secondaryPredelay, secondaryDelaySamples, numSamples);

        // Ext Tank meter tap: last point before audio enters the ext tank.
        extPeak = secondary.getMagnitude (0, 0, numSamples);

        tank.process (primary, numSamples);
        tankSecondary.process (secondary, numSamples);

        // Additive blend: main tank stays at full level, ext tank is summed on
        // top scaled from silent (Mix 0) to full (Mix 100%).
        primary.addFrom (0, 0, secondary, 0, 0, numSamples, extTankMix);
    }
    else if (routing == Ir2RoutingMode::series)
    {
        tank.process (primary, numSamples);

        // Keep the full-level main-tank signal aside, then cascade a copy
        // through the ext predelay, +6 dB makeup gain and the ext tank.
        secondary.copyFrom (0, 0, primary, 0, 0, numSamples);
        applySecondaryTankPredelay (primary, secondaryPredelay, secondaryDelaySamples, numSamples);

        // +6 dB makeup gain between the two tanks (Series only) to compensate
        // for the level drop from cascading the second reverb tank.
        primary.applyGain (0, 0, numSamples, juce::Decibels::decibelsToGain (6.0f));

        // Ext Tank meter tap: last point before audio enters the ext tank.
        extPeak = primary.getMagnitude (0, 0, numSamples);

        tankSecondary.process (primary, numSamples);

        // Same additive pot meaning as Parallel: main tank at full level, the
        // cascaded ext-tank signal summed on top scaled by Mix.
        primary.applyGain (0, 0, numSamples, extTankMix);
        primary.addFrom (0, 0, secondary, 0, 0, numSamples, 1.0f);
    }
    else
    {
        tank.process (primary, numSamples);
    }

    return extPeak;
}

"""
s = s[:i] + new_helper + s[j:]

# fixed Butterworth Q
s = rep(s, "    filterParameters.preHpfResonance = parameters.getRawParameterValue (preHpfResonanceParameterID)->load();\n",
           "    filterParameters.preHpfResonance = filterQ;\n")
s = rep(s, "    filterParameters.postLpfResonance = parameters.getRawParameterValue (postLpfResonanceParameterID)->load();\n",
           "    filterParameters.postLpfResonance = filterQ;\n")

assert "stereoTankCrossfade" not in s and "monoSourceToStereo" not in s and "MonoSourceWithout" not in s, "leftover refs in processor"
save(p, s, crlf)

# ============================================================ PluginEditor.h
p = 'Source/PluginEditor.h'; s, crlf = load(p)
s = rep(s, "    juce::ToggleButton monoSourceToStereoButton;\n", "    juce::ToggleButton megaverbButton;\n")
s = rep(s, "    juce::Label preHpfResonanceLabel;\n    juce::Slider preHpfResonanceSlider;\n", "")
s = rep(s, "    juce::Label postLpfResonanceLabel;\n    juce::Slider postLpfResonanceSlider;\n", "")
s = rep(s, "    juce::Label crossfadeAmountLabel;\n    juce::Slider crossfadeAmountSlider;\n", "")
s = rep(s, "    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> preHpfResonanceAttachment;\n", "")
s = rep(s, "    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> postLpfResonanceAttachment;\n", "")
s = rep(s, "    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> crossfadeAmountAttachment;\n", "")
s = rep(s, "    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> monoSourceToStereoAttachment;\n",
           "    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> megaverbAttachment;\n")
save(p, s, crlf)

# ============================================================ PluginEditor.cpp
p = 'Source/PluginEditor.cpp'; s, crlf = load(p)
s = rep(s, '    configureRotarySlider (preHpfResonanceSlider, preHpfResonanceLabel, "HPF Q", "");\n', "")
s = rep(s, '    configureRotarySlider (postLpfResonanceSlider, postLpfResonanceLabel, "LPF Q", "");\n', "")
s = rep(s, '    configureRotarySlider (crossfadeAmountSlider, crossfadeAmountLabel, "Crossfade", " %");\n', "")
s = rep(s, """    preHpfResonanceAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::preHpfResonanceParameterID, preHpfResonanceSlider);
""", "")
s = rep(s, """    postLpfResonanceAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::postLpfResonanceParameterID, postLpfResonanceSlider);
""", "")
s = rep(s, """    crossfadeAmountAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::crossfadeAmountParameterID, crossfadeAmountSlider);
""", "")
s = rep(s, """    monoSourceToStereoButton.setButtonText ("Mono Source To Stereo");
    content.addAndMakeVisible (monoSourceToStereoButton);
    monoSourceToStereoAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::monoSourceToStereoParameterID, monoSourceToStereoButton);""",
"""    megaverbButton.setButtonText ("MEGAVERB (mono)");
    megaverbButton.setTooltip ("Off = Stereo: L and R reverb paths run side by side. "
                               "On = MEGAVERB: L+R are folded to mono, run the whole Left reverb path, then the whole "
                               "Right reverb path in series (same Off/Series/Parallel ext setting on both), and the "
                               "feedback returns the end of the Right path to the start of the Left path.");
    content.addAndMakeVisible (megaverbButton);
    megaverbAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::megaverbParameterID, megaverbButton);""")
s = rep(s, "        monoSourceToStereoButton.setBounds (row.removeFromLeft (260));\n",
           "        megaverbButton.setBounds (row.removeFromLeft (260));\n")
s = rep(s, """        auto row1 = centreRow (knobs.removeFromTop (kh + 22), kw * 7 + kg * 6);
        knobs.removeFromTop (4);
        auto row2 = centreRow (knobs.removeFromTop (kh + 22), kw * 5 + kg * 4);

        layoutKnob (row1.removeFromLeft (kw), inputLevelLabel,       inputLevelSlider);       row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), modeLabel,             modeSlider);             row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), driveLabel,            driveSlider);            row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), preHpfCutoffLabel,     preHpfCutoffSlider);     row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), preHpfResonanceLabel,  preHpfResonanceSlider);  row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), postLpfCutoffLabel,    postLpfCutoffSlider);    row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), postLpfResonanceLabel, postLpfResonanceSlider);

        layoutKnob (row2.removeFromLeft (kw), crossfadeAmountLabel,  crossfadeAmountSlider);  row2.removeFromLeft (kg);
        layoutKnob (row2.removeFromLeft (kw), extTankMixLabel,       extTankMixSlider);       row2.removeFromLeft (kg);""",
"""        // Q knobs and Crossfade were removed 2026-09-12 (Q fixed at 0.707,
        // crossfade gone from the plugin), so rows are 5 and 4 knobs wide.
        auto row1 = centreRow (knobs.removeFromTop (kh + 22), kw * 5 + kg * 4);
        knobs.removeFromTop (4);
        auto row2 = centreRow (knobs.removeFromTop (kh + 22), kw * 4 + kg * 3);

        layoutKnob (row1.removeFromLeft (kw), inputLevelLabel,       inputLevelSlider);       row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), modeLabel,             modeSlider);             row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), driveLabel,            driveSlider);            row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), preHpfCutoffLabel,     preHpfCutoffSlider);     row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kw), postLpfCutoffLabel,    postLpfCutoffSlider);

        layoutKnob (row2.removeFromLeft (kw), extTankMixLabel,       extTankMixSlider);       row2.removeFromLeft (kg);""")
s = rep(s, """    for (auto* label : { &driveLabel, &preHpfCutoffLabel, &preHpfResonanceLabel, &postLpfCutoffLabel,
                         &postLpfResonanceLabel, &crossfadeAmountLabel, &extTankMixLabel, &feedbackAmountLabel, &wetDryLabel,""",
"""    for (auto* label : { &driveLabel, &preHpfCutoffLabel, &postLpfCutoffLabel,
                         &extTankMixLabel, &feedbackAmountLabel, &wetDryLabel,""")
s = rep(s, """    for (auto* slider : { &modeSlider, &driveSlider, &preHpfCutoffSlider, &preHpfResonanceSlider, &postLpfCutoffSlider,
                          &postLpfResonanceSlider, &crossfadeAmountSlider, &extTankMixSlider, &feedbackAmountSlider, &wetDrySlider,""",
"""    for (auto* slider : { &modeSlider, &driveSlider, &preHpfCutoffSlider, &postLpfCutoffSlider,
                          &extTankMixSlider, &feedbackAmountSlider, &wetDrySlider,""")
s = rep(s, "    monoSourceToStereoButton.setEnabled (true);\n    monoSourceToStereoButton.setAlpha (1.0f);\n",
           "    megaverbButton.setEnabled (true);\n    megaverbButton.setAlpha (1.0f);\n")
assert "monoSourceToStereo" not in s and "Resonance" not in s and "crossfade" not in s.lower(), "leftover refs in editor"
save(p, s, crlf)
print("MEGAVERB patch applied")
