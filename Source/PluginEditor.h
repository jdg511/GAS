#pragma once

#include "PluginProcessor.h"

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
    void applyTheme (Theme newTheme);
    void refreshThemeButtons();
    void refreshLogoButton();
    void refreshOptionControls();
    void updateExpandedTankControlsAnimation();
    void changeListenerCallback (juce::ChangeBroadcaster* source) override;
    void timerCallback() override;

    TheGreatAmericanSpringAudioProcessor& audioProcessor;

    juce::Label titleLabel;
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
    int animatedEditorHeight = 620;
    int targetEditorHeight = 620;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TheGreatAmericanSpringAudioProcessorEditor)
};
