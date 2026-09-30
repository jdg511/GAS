#pragma once

#include "PluginProcessor.h"

//==============================================================================
/** A self-contained Art Nouveau wordmark for the plugin title.

    Draws the title in a decorative typeface (chosen at runtime from the fonts
    available on the host machine) with a hand-drawn whiplash flourish beneath
    it. Owns no state beyond its current theme colours and typeface, so it can
    be retheme'd cheaply by the editor.
*/
class ArtNouveauTitle final : public juce::Component
{
public:
    ArtNouveauTitle() { setInterceptsMouseClicks (false, false); }

    void setStyle (juce::Colour primaryColour,
                   juce::Colour accentColour,
                   const juce::String& typeface)
    {
        textColour     = primaryColour;
        flourishColour = accentColour;
        typefaceName   = typeface;
        repaint();
    }

    void paint (juce::Graphics& g) override
    {
        auto bounds = getLocalBounds().toFloat();

        // Reserve the lower strip for the flourish, the rest for the lettering.
        auto flourishArea = bounds.removeFromBottom (juce::jmax (16.0f, bounds.getHeight() * 0.26f));
        auto textArea     = bounds;

        auto font = juce::Font (juce::FontOptions (typefaceName,
                                                   textArea.getHeight() * 0.50f,
                                                   juce::Font::plain))
                        .withExtraKerningFactor (0.07f);
        g.setFont (font);

        // drawFittedText scales the lettering down to fit the band, so the
        // wordmark never overruns its bounds regardless of the chosen face.
        const auto textBox = textArea.toNearestInt();

        // Soft drop shadow for depth.
        g.setColour (juce::Colours::black.withAlpha (0.40f));
        g.drawFittedText (titleText, textBox.translated (0, 2), juce::Justification::centred, 1, 1.0f);

        g.setColour (textColour);
        g.drawFittedText (titleText, textBox, juce::Justification::centred, 1, 1.0f);

        // ── Whiplash flourish ────────────────────────────────────────────────
        const auto cx = flourishArea.getCentreX();
        const auto cy = flourishArea.getCentreY();
        const auto reach = juce::jmin (flourishArea.getWidth() * 0.42f, 230.0f);

        g.setColour (flourishColour.withAlpha (0.9f));

        juce::Path flourish;
        // Left sweep
        flourish.startNewSubPath (cx - 9.0f, cy);
        flourish.cubicTo (cx - reach * 0.35f, cy + 5.0f,
                          cx - reach * 0.6f,  cy - 6.0f,
                          cx - reach,         cy);
        // Right sweep (mirror)
        flourish.startNewSubPath (cx + 9.0f, cy);
        flourish.cubicTo (cx + reach * 0.35f, cy + 5.0f,
                          cx + reach * 0.6f,  cy - 6.0f,
                          cx + reach,         cy);
        g.strokePath (flourish, juce::PathStrokeType (1.5f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // Centre medallion + end dots
        g.fillEllipse (juce::Rectangle<float> (9.0f, 9.0f).withCentre ({ cx, cy }));
        g.setColour (flourishColour.withAlpha (0.65f));
        g.fillEllipse (juce::Rectangle<float> (5.0f, 5.0f).withCentre ({ cx - reach, cy }));
        g.fillEllipse (juce::Rectangle<float> (5.0f, 5.0f).withCentre ({ cx + reach, cy }));
    }

private:
    juce::String titleText { "The Great American Spring reverb Rev C" };
    juce::String typefaceName { "Georgia" };
    juce::Colour textColour { juce::Colours::white };
    juce::Colour flourishColour { juce::Colours::white };
};

//==============================================================================
/** A simple peak level meter, 0 dBFS down to the processor's meter floor.

    The processor publishes a raw block peak; the ballistics live here so the
    audio thread only does one atomic store. Rise is instant so transients are
    never missed, fall is eased so the bar stays readable, and the last peak is
    held briefly as a thin marker.
*/
class LevelMeter final : public juce::Component,
                         public juce::SettableTooltipClient
{
public:
    void setTrackColours (juce::Colour background, juce::Colour fill, juce::Colour outline, juce::Colour peakMarker)
    {
        trackColour = background;
        barColour = fill;
        borderColour = outline;
        markerColour = peakMarker;
        repaint();
    }

    /** Feed a fresh reading, in dBFS. Call from a timer, not the audio thread. */
    void setLevelDb (float newLevelDb)
    {
        const auto clamped = juce::jlimit (floorDb, 6.0f, newLevelDb);

        levelDb = clamped > levelDb ? clamped                       // instant attack
                                    : levelDb + (clamped - levelDb) * 0.30f;

        if (clamped >= peakDb)
        {
            peakDb = clamped;
            peakHoldTicks = 22;
        }
        else if (peakHoldTicks > 0)
        {
            --peakHoldTicks;
        }
        else
        {
            peakDb += (clamped - peakDb) * 0.10f;
        }

        repaint();
    }

    void paint (juce::Graphics& g) override
    {
        auto bounds = getLocalBounds().toFloat();

        g.setColour (trackColour);
        g.fillRoundedRectangle (bounds, 2.0f);

        const auto proportionFor = [this] (float db)
        {
            return juce::jlimit (0.0f, 1.0f, (juce::jmin (db, 0.0f) - floorDb) / (0.0f - floorDb));
        };

        auto bar = bounds.reduced (1.0f);
        const auto fullWidth = bar.getWidth();

        // Bar turns warm as it approaches full scale, so clipping is obvious.
        const auto hot = levelDb > -6.0f;
        g.setColour (hot ? barColour.contrasting (0.25f) : barColour);
        g.fillRoundedRectangle (bar.withWidth (fullWidth * proportionFor (levelDb)), 1.5f);

        if (peakDb > floorDb + 0.5f)
        {
            const auto x = bar.getX() + fullWidth * proportionFor (peakDb);
            g.setColour (markerColour);
            g.fillRect (juce::Rectangle<float> (juce::jmin (x, bar.getRight() - 1.5f), bar.getY(), 1.5f, bar.getHeight()));
        }

        g.setColour (borderColour);
        g.drawRoundedRectangle (bounds.reduced (0.5f), 2.0f, 1.0f);
    }

private:
    float floorDb = -48.0f;
    float levelDb = -48.0f;
    float peakDb = -48.0f;
    int   peakHoldTicks = 0;

    juce::Colour trackColour { juce::Colours::black.withAlpha (0.35f) };
    juce::Colour barColour { juce::Colours::orange };
    juce::Colour borderColour { juce::Colours::white.withAlpha (0.4f) };
    juce::Colour markerColour { juce::Colours::white };
};

//==============================================================================
/** The Left channel's signal path, drawn as monospace rows.

    A monospace face is the whole point: the processor hands over rows whose
    columns already line up, so the feedback arrows sit directly over their taps
    and the Parallel tank names sit directly over and under the summing point. The
    type size is chosen to fit the widest row, so MEGAVERB's extra "to R" and
    "from R" text shrinks the block rather than running off the edge.
*/
class SignalPathDisplay final : public juce::Component
{
public:
    void setRows (const juce::StringArray& newRows)
    {
        if (rows == newRows)
            return;

        rows = newRows;
        repaint();
    }

    void setTextColour (juce::Colour colour)
    {
        textColour = colour;
        repaint();
    }

    void paint (juce::Graphics& g) override
    {
        if (rows.isEmpty() || getWidth() <= 0)
            return;

        int widestRow = 0;

        for (const auto& row : rows)
            widestRow = juce::jmax (widestRow, row.length());

        if (widestRow == 0)
            return;

        auto font = monoFont (maximumSize);
        const auto characterWidth = juce::GlyphArrangement::getStringWidth (font, "0");

        if (characterWidth <= 0.0f)
            return;

        // Character width scales with the type size, so the fitting size is one
        // division rather than a search.
        const auto widthAtMaximum = characterWidth * (float) widestRow;
        auto size = maximumSize;

        if (widthAtMaximum > (float) getWidth())
            size = juce::jmax (minimumSize, maximumSize * (float) getWidth() / widthAtMaximum);

        font = monoFont (size);
        g.setFont (font);
        g.setColour (textColour);

        const auto blockWidth = juce::GlyphArrangement::getStringWidth (font, "0") * (float) widestRow;
        const auto rowHeight = font.getHeight() * 1.05f;
        const auto blockHeight = rowHeight * (float) rows.size();

        auto x = ((float) getWidth() - blockWidth) * 0.5f;
        auto y = ((float) getHeight() - blockHeight) * 0.5f;

        for (const auto& row : rows)
        {
            g.drawText (row,
                        juce::Rectangle<float> (x, y, blockWidth, rowHeight),
                        juce::Justification::centredLeft,
                        false);
            y += rowHeight;
        }
    }

private:
    static juce::Font monoFont (float height)
    {
        return juce::Font (juce::FontOptions (juce::Font::getDefaultMonospacedFontName(),
                                             height,
                                             juce::Font::plain));
    }

    static constexpr float maximumSize = 11.5f;
    static constexpr float minimumSize = 7.5f;

    juce::StringArray rows;
    juce::Colour textColour { juce::Colours::white.withAlpha (0.75f) };
};

//==============================================================================
/** A rotary knob with a pull-out switch, like a push-pull pot on the board.

    Drag turns it as usual. A plain click (press and release without dragging)
    pulls the knob out or pushes it back in, which toggles the attached bool
    parameter. The pulled state is drawn by the LookAndFeel from the "pulled"
    property so the knob visibly sits proud of the panel when engaged.
*/
class PullKnobSlider final : public juce::Slider
{
public:
    std::function<void()> onPullToggle;

    void setPulled (bool shouldBePulled)
    {
        if (pulled == shouldBePulled)
            return;

        pulled = shouldBePulled;
        getProperties().set ("pulled", pulled);
        repaint();
    }

    bool isPulled() const noexcept { return pulled; }

    void mouseDown (const juce::MouseEvent& e) override
    {
        dragged = false;
        juce::Slider::mouseDown (e);
    }

    void mouseDrag (const juce::MouseEvent& e) override
    {
        if (e.getDistanceFromDragStart() > 3)
            dragged = true;

        juce::Slider::mouseDrag (e);
    }

    void mouseUp (const juce::MouseEvent& e) override
    {
        juce::Slider::mouseUp (e);

        if (! dragged && e.mods.isLeftButtonDown() && onPullToggle != nullptr
            && getLocalBounds().withTrimmedBottom (getTextBoxHeight()).contains (e.getPosition()))
        {
            onPullToggle();
        }
    }

private:
    bool pulled = false;
    bool dragged = false;
};

class TheGreatAmericanSpringAudioProcessorEditor final : public juce::AudioProcessorEditor,
                                                          private juce::ChangeListener,
                                                          private juce::Timer
{
public:
    enum class Theme
    {
        solar = 0,
        petal,
        cosmic
    };

    explicit TheGreatAmericanSpringAudioProcessorEditor (TheGreatAmericanSpringAudioProcessor&);
    ~TheGreatAmericanSpringAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;

    // The UI is authored once at this fixed logical size and then scaled to
    // whatever the window is dragged to, so nothing is ever clipped.
    static constexpr int baseEditorWidth = 920;
    // Rev C added the Tube / Dirt / Tape switch row (28 px + 8 px pad), so both heights grew by 36.
    // +14 over the single-bar layout: each meter point now stacks L over R.
    // +20 again for the signal path, now three monospace rows rather than one line.
    // The Oversampling row sits in the header's own spare space under the BYOIRs
    // toggle, so it costs neither height anything.
    static constexpr int baseCollapsedHeight = 764;
    static constexpr int baseExpandedHeight = 970;
    static constexpr double minEditorScale = 0.75;
    static constexpr double maxEditorScale = 2.50;

private:
    using TankSlot = TheGreatAmericanSpringAudioProcessor::TankSlot;

    // Lays the controls out inside `content` at the fixed logical size. The
    // editor's own resized() only picks the scale factor.
    void layoutContent();
    void updateSizeLimits();
    void applyEditorScale (double newScale);
    double readStoredEditorScale() const;
    void storeEditorScale (double scale) const;
    static double defaultEditorScaleForDisplay();

    void configureRotarySlider (juce::Slider& slider,
                                juce::Label& label,
                                const juce::String& labelText,
                                const juce::String& suffix);
    void chooseTankImpulseResponseFile (TankSlot slot);
    void refreshTankLabels();
    void refreshX2VisualState();
    void choosePlaybackFile();
    void refreshPlaybackLabel();
    void refreshPresetOptions();
    void promptToSaveUserPreset();
    void applyTheme (Theme newTheme);
    void refreshThemeButtons();
    void refreshLogoButton();
    void refreshOptionControls();
    void refreshPullStates();
    void refreshChainReadout();
    void configurePullKnob (PullKnobSlider& slider, const juce::String& parameterID);
    void updateExpandedTankControlsAnimation();
    void changeListenerCallback (juce::ChangeBroadcaster* source) override;
    void timerCallback() override;

    TheGreatAmericanSpringAudioProcessor& audioProcessor;

    // Declared before every control so it outlives them on destruction.
    // Everything visible lives inside this component; it carries the scale
    // transform. Clicks pass straight through to its children.
    juce::Component content;
    juce::ComponentBoundsConstrainer sizeConstrainer;
    double editorScale = 1.0;

    ArtNouveauTitle titleComponent;
    juce::Label subtitleLabel;
    SignalPathDisplay chainDescriptionDisplay;
    juce::Label ir2RoutingLabel;
    juce::ComboBox ir2RoutingComboBox;
    juce::Label feedbackPhaseLabel;
    juce::ToggleButton feedbackPhaseNormalButton;
    juce::ToggleButton feedbackPhaseInvertButton;
    juce::Label dynamicsLabel;
    juce::ToggleButton dynamicsCompButton;
    juce::ToggleButton dynamicsOffButton;
    juce::ToggleButton dynamicsLimitButton;
    juce::Label stereoModeLabel;
    juce::ToggleButton stereoButton;
    juce::ToggleButton monoToStereoButton;
    juce::ToggleButton megaverbButton;

    // Rev C panel switch row. The Vol / Gain / Output pulls became three mini toggles on the
    // control deck (TUBE, DIRT, TAPE), so the plugin shows them as two-position switches too.
    juce::Label tubeSwitchLabel;
    juce::ToggleButton tubeOffButton;
    juce::ToggleButton tubeOnButton;
    juce::Label dirtSwitchLabel;
    juce::ToggleButton dirtOffButton;
    juce::ToggleButton dirtOnButton;
    juce::Label tapeSwitchLabel;
    juce::ToggleButton tapeOffButton;
    juce::ToggleButton tapeOnButton;
    juce::ToggleButton showUnavailableTankControlsButton;
    juce::Label themeLabel;
    juce::ToggleButton solarThemeButton;
    juce::ToggleButton petalThemeButton;
    juce::ToggleButton cosmicThemeButton;
    juce::ImageButton logoButton;
    juce::Label presetLabel;
    juce::ComboBox presetComboBox;

    juce::Label preInputLevelLabel;
    juce::Slider preInputLevelSlider;
    juce::Label inputLevelLabel;
    PullKnobSlider inputLevelSlider;      // Vol, pull for Tube
    juce::Label gainLabel;
    PullKnobSlider gainSlider;            // Gain, pull for Dirt
    juce::Label preHpfCutoffLabel;
    juce::Slider preHpfCutoffSlider;
    juce::Label postLpfCutoffLabel;
    juce::Slider postLpfCutoffSlider;
    juce::Label extTankMixLabel;
    juce::Slider extTankMixSlider;
    juce::Label feedbackAmountLabel;
    juce::Slider feedbackAmountSlider;
    juce::Label wetDryLabel;
    juce::Slider wetDrySlider;
    juce::Label outputLevelLabel;
    PullKnobSlider outputLevelSlider;     // Output, pull for Tape
    juce::Label postOutputLevelLabel;
    juce::Slider postOutputLevelSlider;

    // Each tap gets its own Left and Right bar, with an "L" / "R" tag beside it.
    juce::Label inputMeterLabel;
    juce::Label inputMeterLabelL;
    LevelMeter inputMeterL;
    juce::Label inputMeterLabelR;
    LevelMeter inputMeterR;
    juce::Label wetMeterLabel;
    juce::Label wetMeterLabelL;
    LevelMeter wetMeterL;
    juce::Label wetMeterLabelR;
    LevelMeter wetMeterR;
    juce::Label outputMeterLabel;
    juce::Label outputMeterLabelL;
    LevelMeter outputMeterL;
    juce::Label outputMeterLabelR;
    LevelMeter outputMeterR;

    // Lives in the BYOIRs section: plugin-only, no equivalent on the board.
    juce::Label railOversamplingLabel;
    juce::ComboBox railOversamplingComboBox;

    juce::GroupComponent leftTankGroup;
    juce::Label leftTankLabel;
    juce::TextButton leftTankLoadButton;

    juce::GroupComponent rightTankGroup;
    juce::Label rightTankLabel;
    juce::TextButton rightTankLoadButton;

    juce::GroupComponent leftTank2Group;
    juce::Label leftTank2Label;
    juce::TextButton leftTank2LoadButton;

    juce::GroupComponent rightTank2Group;
    juce::Label rightTank2Label;
    juce::TextButton rightTank2LoadButton;

    juce::Label playbackLabel;
    juce::ComboBox playbackSourceComboBox;
    juce::TextButton loadPlaybackButton;
    juce::TextButton playbackToggleButton;

    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> ir2RoutingAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> gainAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> preInputLevelAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> postOutputLevelAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> preHpfCutoffAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> postLpfCutoffAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> railOversamplingAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> extTankMixAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> feedbackAmountAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> wetDryAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> inputLevelAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> outputLevelAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> showUnavailableTankControlsAttachment;
    std::unique_ptr<juce::LookAndFeel_V4> lookAndFeel;
    std::unique_ptr<juce::FileChooser> activeChooser;
    juce::Image solarBackground;
    juce::Image petalBackground;
    juce::Image cosmicBackground;
    juce::Image logoImage;
    Theme currentTheme = Theme::solar;
    int introThemeStep = 0;
    int introElapsedMs = 0;
    int animatedEditorHeight = 694;
    int targetEditorHeight = 694;
    juce::String currentPresetSelection { "GBS default" };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TheGreatAmericanSpringAudioProcessorEditor)
};
