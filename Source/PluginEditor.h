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
    juce::String titleText { "The Great American Spring reverb" };
    juce::String typefaceName { "Georgia" };
    juce::Colour textColour { juce::Colours::white };
    juce::Colour flourishColour { juce::Colours::white };
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

private:
    using TankSlot = TheGreatAmericanSpringAudioProcessor::TankSlot;

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
    void updateExpandedTankControlsAnimation();
    void changeListenerCallback (juce::ChangeBroadcaster* source) override;
    void timerCallback() override;

    TheGreatAmericanSpringAudioProcessor& audioProcessor;

    ArtNouveauTitle titleComponent;
    juce::Label subtitleLabel;
    juce::Label modeLabel;
    juce::ComboBox modeComboBox;
    juce::Label ir2RoutingLabel;
    juce::ComboBox ir2RoutingComboBox;
    juce::Label feedbackPhaseLabel;
    juce::ToggleButton feedbackPhaseNormalButton;
    juce::ToggleButton feedbackPhaseInvertButton;
    juce::ToggleButton monoSourceToStereoButton;
    juce::ToggleButton showUnavailableTankControlsButton;
    juce::Label themeLabel;
    juce::ToggleButton solarThemeButton;
    juce::ToggleButton petalThemeButton;
    juce::ToggleButton cosmicThemeButton;
    juce::ImageButton logoButton;
    juce::Label presetLabel;
    juce::ComboBox presetComboBox;

    juce::Label driveLabel;
    juce::Slider driveSlider;
    juce::Label preHpfCutoffLabel;
    juce::Slider preHpfCutoffSlider;
    juce::Label preHpfResonanceLabel;
    juce::Slider preHpfResonanceSlider;
    juce::Label postLpfCutoffLabel;
    juce::Slider postLpfCutoffSlider;
    juce::Label postLpfResonanceLabel;
    juce::Slider postLpfResonanceSlider;
    juce::Label crossfadeAmountLabel;
    juce::Slider crossfadeAmountSlider;
    juce::Label extTankMixLabel;
    juce::Slider extTankMixSlider;
    juce::Label feedbackAmountLabel;
    juce::Slider feedbackAmountSlider;
    juce::Label wetDryLabel;
    juce::Slider wetDrySlider;

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

    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> modeAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> ir2RoutingAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> driveAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> preHpfCutoffAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> preHpfResonanceAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> postLpfCutoffAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> postLpfResonanceAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> crossfadeAmountAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> extTankMixAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> feedbackAmountAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> wetDryAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> monoSourceToStereoAttachment;
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
