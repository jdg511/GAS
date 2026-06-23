#include <BinaryData.h>

#include "PluginEditor.h"

namespace
{
using Theme = TheGreatAmericanSpringAudioProcessorEditor::Theme;

struct ThemeStyle
{
    juce::String title;
    juce::String body;
    juce::Colour backgroundTop;
    juce::Colour backgroundBottom;
    juce::Colour panelTop;
    juce::Colour panelBottom;
    juce::Colour panelOutline;
    juce::Colour textPrimary;
    juce::Colour textSecondary;
    juce::Colour knobTrack;
    juce::Colour knobStart;
    juce::Colour knobEnd;
    juce::Colour knobBodyOuter;
    juce::Colour knobBodyInner;
    juce::Colour buttonOn;
    juce::Colour buttonOff;
    juce::Colour buttonOutline;
    juce::Colour radioFill;
    juce::Colour accentA;
    juce::Colour accentB;
    juce::Colour accentC;
    juce::String titleTypeface;
    juce::String bodyTypeface;
};

juce::Font makeFont (float height, int styleFlags, const juce::String& typefaceName)
{
    if (typefaceName.isNotEmpty())
        return juce::Font (juce::FontOptions (typefaceName, height, styleFlags));

    return juce::Font (juce::FontOptions (height, styleFlags));
}

ThemeStyle getThemeStyle (Theme theme)
{
    switch (theme)
    {
        case Theme::solar:
            return {
                "Solar Hymn",
                "Golden rain, clouds, and a luminous sun medallion",
                juce::Colour::fromRGB (32, 44, 58),
                juce::Colour::fromRGB (83, 102, 116),
                juce::Colour::fromRGB (43, 57, 71),
                juce::Colour::fromRGB (22, 31, 40),
                juce::Colour::fromRGB (216, 179, 106),
                juce::Colour::fromRGB (250, 238, 208),
                juce::Colour::fromRGB (206, 188, 150),
                juce::Colour::fromRGB (72, 85, 95),
                juce::Colour::fromRGB (233, 196, 116),
                juce::Colour::fromRGB (245, 225, 168),
                juce::Colour::fromRGB (148, 121, 74),
                juce::Colour::fromRGB (54, 66, 81),
                juce::Colour::fromRGB (162, 134, 88),
                juce::Colour::fromRGB (236, 212, 150),
                juce::Colour::fromRGB (64, 84, 102),
                juce::Colour::fromRGB (222, 184, 92),
                juce::Colour::fromRGB (246, 222, 160),
                juce::Colour::fromRGB (245, 235, 194),
                juce::Colour::fromRGB (130, 151, 166),
                "Segoe UI",
                "Georgia"
            };

        case Theme::petal:
            return {
                "Petal Nocturne",
                "Floral lunar sky with a soft halo at the center",
                juce::Colour::fromRGB (46, 67, 78),
                juce::Colour::fromRGB (98, 122, 119),
                juce::Colour::fromRGB (34, 52, 61),
                juce::Colour::fromRGB (19, 30, 37),
                juce::Colour::fromRGB (219, 171, 94),
                juce::Colour::fromRGB (252, 240, 211),
                juce::Colour::fromRGB (208, 188, 152),
                juce::Colour::fromRGB (72, 92, 99),
                juce::Colour::fromRGB (225, 175, 90),
                juce::Colour::fromRGB (246, 225, 171),
                juce::Colour::fromRGB (166, 122, 70),
                juce::Colour::fromRGB (48, 70, 77),
                juce::Colour::fromRGB (180, 144, 92),
                juce::Colour::fromRGB (240, 214, 147),
                juce::Colour::fromRGB (65, 98, 93),
                juce::Colour::fromRGB (229, 186, 102),
                juce::Colour::fromRGB (244, 226, 170),
                juce::Colour::fromRGB (251, 239, 213),
                juce::Colour::fromRGB (110, 142, 134),
                "Segoe UI",
                "Palatino Linotype"
            };

        case Theme::cosmic:
            return {
                "Cosmic Current",
                "Moonlit river with prismatic reflections through a night valley",
                juce::Colour::fromRGB (24, 35, 58),
                juce::Colour::fromRGB (66, 87, 112),
                juce::Colour::fromRGB (23, 36, 58),
                juce::Colour::fromRGB (12, 22, 36),
                juce::Colour::fromRGB (226, 198, 117),
                juce::Colour::fromRGB (249, 239, 211),
                juce::Colour::fromRGB (205, 214, 230),
                juce::Colour::fromRGB (73, 95, 129),
                juce::Colour::fromRGB (116, 205, 214),
                juce::Colour::fromRGB (245, 169, 84),
                juce::Colour::fromRGB (84, 118, 160),
                juce::Colour::fromRGB (28, 38, 54),
                juce::Colour::fromRGB (97, 160, 199),
                juce::Colour::fromRGB (239, 207, 124),
                juce::Colour::fromRGB (58, 81, 115),
                juce::Colour::fromRGB (105, 199, 213),
                juce::Colour::fromRGB (246, 175, 93),
                juce::Colour::fromRGB (247, 217, 123),
                juce::Colour::fromRGB (124, 151, 214),
                "Segoe UI",
                "Georgia"
            };
    }

    jassertfalse;
    return getThemeStyle (Theme::solar);
}

juce::Image loadImageFromBinaryData (const void* data, int size)
{
    return juce::ImageFileFormat::loadFrom (data, static_cast<size_t> (size));
}

juce::Image createLogoImage (const void* data, int size)
{
    constexpr int logoWidth = 352;
    constexpr int logoHeight = 112;
    juce::Image logo (juce::Image::ARGB, logoWidth, logoHeight, true);
    juce::Graphics graphics (logo);
    const auto destination = juce::Rectangle<float> (0.0f, 0.0f, static_cast<float> (logoWidth), static_cast<float> (logoHeight)).reduced (4.0f);

    if (auto image = loadImageFromBinaryData (data, size); image.isValid())
    {
        graphics.drawImageWithin (image,
                                  static_cast<int> (destination.getX()),
                                  static_cast<int> (destination.getY()),
                                  static_cast<int> (destination.getWidth()),
                                  static_cast<int> (destination.getHeight()),
                                  juce::RectanglePlacement::centred | juce::RectanglePlacement::onlyReduceInSize);
        return logo;
    }

    if (auto drawable = juce::Drawable::createFromImageData (data, static_cast<size_t> (size)))
        drawable->drawWithin (graphics, destination, juce::RectanglePlacement::centred | juce::RectanglePlacement::onlyReduceInSize, 1.0f);

    return logo;
}

struct ArtDirectedLookAndFeel final : juce::LookAndFeel_V4
{
    void setTheme (Theme newTheme)
    {
        theme = newTheme;
    }

    void drawRotarySlider (juce::Graphics& g,
                           int x,
                           int y,
                           int width,
                           int height,
                           float sliderPosProportional,
                           float rotaryStartAngle,
                           float rotaryEndAngle,
                           juce::Slider&) override
    {
        const auto style = getThemeStyle (theme);
        const auto bounds = juce::Rectangle<float> (static_cast<float> (x), static_cast<float> (y),
                                                    static_cast<float> (width), static_cast<float> (height)).reduced (8.0f, 4.0f);
        const auto radius = juce::jmin (bounds.getWidth(), bounds.getHeight()) * 0.5f;
        const auto centre = bounds.getCentre();
        const auto angle = rotaryStartAngle + sliderPosProportional * (rotaryEndAngle - rotaryStartAngle);
        const auto knobBounds = juce::Rectangle<float> (radius * 2.0f, radius * 2.0f).withCentre (centre);

        juce::ColourGradient bodyGradient (style.knobBodyOuter, knobBounds.getCentreX(), knobBounds.getY(),
                                           style.knobBodyInner, knobBounds.getCentreX(), knobBounds.getBottom(), false);
        g.setGradientFill (bodyGradient);
        g.fillEllipse (knobBounds);

        g.setColour (juce::Colours::black.withAlpha (0.35f));
        g.drawEllipse (knobBounds.expanded (1.5f), 1.8f);

        juce::Path ring;
        ring.addCentredArc (centre.x, centre.y, radius - 2.0f, radius - 2.0f, 0.0f, rotaryStartAngle, rotaryEndAngle, true);
        g.setColour (style.knobTrack);
        g.strokePath (ring, juce::PathStrokeType (6.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        juce::Path valueArc;
        valueArc.addCentredArc (centre.x, centre.y, radius - 2.0f, radius - 2.0f, 0.0f, rotaryStartAngle, angle, true);
        juce::ColourGradient arcGradient (style.knobStart, knobBounds.getX(), knobBounds.getBottom(),
                                          style.knobEnd, knobBounds.getRight(), knobBounds.getY(), false);
        g.setGradientFill (arcGradient);
        g.strokePath (valueArc, juce::PathStrokeType (7.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        juce::Path pointer;
        pointer.addRoundedRectangle (-2.2f, -radius * 0.6f, 4.4f, radius * 0.44f, 2.0f);
        g.setColour (style.textPrimary);
        g.fillPath (pointer, juce::AffineTransform::rotation (angle).translated (centre.x, centre.y));

        g.setColour (style.radioFill.withAlpha (0.95f));
        g.fillEllipse (juce::Rectangle<float> (10.0f, 10.0f).withCentre (centre));
        g.setColour (style.knobBodyInner);
        g.fillEllipse (juce::Rectangle<float> (4.2f, 4.2f).withCentre (centre));
    }

    void drawButtonBackground (juce::Graphics& g,
                               juce::Button& button,
                               const juce::Colour&,
                               bool shouldDrawButtonAsHighlighted,
                               bool shouldDrawButtonAsDown) override
    {
        const bool gasInverted = button.getProperties()["gasInverted"];
        if (gasInverted)
        {
            const auto style = getThemeStyle (theme);
            const auto bounds = button.getLocalBounds().toFloat().reduced (0.5f);
            auto base = style.panelBottom.brighter (0.18f);
            if (shouldDrawButtonAsDown)   base = base.darker (0.18f);
            else if (shouldDrawButtonAsHighlighted) base = base.brighter (0.14f);
            juce::ColourGradient fill (base.brighter (0.28f), bounds.getCentreX(), bounds.getY(),
                                       base.darker (0.28f), bounds.getCentreX(), bounds.getBottom(), false);
            g.setGradientFill (fill);
            g.fillRoundedRectangle (bounds, 7.0f);
            g.setColour (style.accentA.withAlpha (0.85f));
            g.drawRoundedRectangle (bounds, 7.0f, 1.4f);
            return;
        }

        if (button.getRadioGroupId() != 0)
            return;

        const auto style = getThemeStyle (theme);
        const auto bounds = button.getLocalBounds().toFloat().reduced (0.5f);
        auto base = button.getToggleState() ? style.buttonOn : style.buttonOff;

        if (shouldDrawButtonAsDown)
            base = base.darker (0.16f);
        else if (shouldDrawButtonAsHighlighted)
            base = base.brighter (0.12f);

        juce::ColourGradient fill (base.brighter (0.25f), bounds.getCentreX(), bounds.getY(),
                                   base.darker (0.35f), bounds.getCentreX(), bounds.getBottom(), false);
        g.setGradientFill (fill);
        g.fillRoundedRectangle (bounds, 8.0f);

        g.setColour (style.buttonOutline);
        g.drawRoundedRectangle (bounds, 8.0f, 1.4f);
    }

    void drawButtonText (juce::Graphics& g, juce::TextButton& button, bool, bool) override
    {
        const bool gasInverted = button.getProperties()["gasInverted"];
        if (gasInverted)
        {
            const auto style = getThemeStyle (theme);
            auto font = makeFont (12.0f, juce::Font::bold, style.bodyTypeface);
            g.setColour (style.accentA);
            g.setFont (font);
            g.drawFittedText (button.getButtonText(), button.getLocalBounds(), juce::Justification::centred, 1);
            return;
        }

        const auto style = getThemeStyle (theme);
        auto font = makeFont (12.5f, juce::Font::bold, style.bodyTypeface);
        g.setColour (style.textPrimary);
        g.setFont (font);
        g.drawFittedText (button.getButtonText(), button.getLocalBounds(), juce::Justification::centred, 1);
    }

    void drawToggleButton (juce::Graphics& g,
                           juce::ToggleButton& button,
                           bool shouldDrawButtonAsHighlighted,
                           bool shouldDrawButtonAsDown) override
    {
        const auto style = getThemeStyle (theme);

        if (button.getRadioGroupId() != 0)
        {
            auto area = button.getLocalBounds().toFloat();
            auto circle = juce::Rectangle<float> (10.0f, 10.0f).withCentre ({ area.getX() + 8.0f, area.getCentreY() });

            g.setColour (style.textPrimary.withAlpha (0.85f));
            g.drawEllipse (circle, 1.3f);

            if (button.getToggleState())
            {
                g.setColour (style.radioFill);
                g.fillEllipse (circle.reduced (2.3f));
            }

            auto font = makeFont (12.5f, juce::Font::bold, style.bodyTypeface);
            g.setFont (font);
            g.setColour (button.getToggleState() ? style.textPrimary : style.textSecondary);
            g.drawFittedText (button.getButtonText(), button.getLocalBounds().withTrimmedLeft (16), juce::Justification::centredLeft, 1);
            return;
        }

        auto area = button.getLocalBounds();
        auto switchBounds = area.removeFromLeft (38).toFloat().reduced (0.5f, 5.0f);
        auto fill = button.getToggleState() ? style.buttonOn : style.buttonOff;

        if (shouldDrawButtonAsDown)
            fill = fill.darker (0.15f);
        else if (shouldDrawButtonAsHighlighted)
            fill = fill.brighter (0.12f);

        juce::ColourGradient gradient (fill.brighter (0.26f), switchBounds.getCentreX(), switchBounds.getY(),
                                       fill.darker (0.4f), switchBounds.getCentreX(), switchBounds.getBottom(), false);
        g.setGradientFill (gradient);
        g.fillRoundedRectangle (switchBounds, switchBounds.getHeight() * 0.5f);

        g.setColour (style.buttonOutline);
        g.drawRoundedRectangle (switchBounds, switchBounds.getHeight() * 0.5f, 1.6f);

        const auto knobDiameter = switchBounds.getHeight() - 6.0f;
        auto knobBounds = juce::Rectangle<float> (knobDiameter, knobDiameter).withCentre (
            button.getToggleState()
                ? juce::Point<float> (switchBounds.getRight() - knobDiameter * 0.65f, switchBounds.getCentreY())
                : juce::Point<float> (switchBounds.getX() + knobDiameter * 0.65f, switchBounds.getCentreY()));

        juce::ColourGradient knobFill (style.textPrimary, knobBounds.getCentreX(), knobBounds.getY(),
                                       style.knobEnd, knobBounds.getCentreX(), knobBounds.getBottom(), false);
        g.setGradientFill (knobFill);
        g.fillEllipse (knobBounds);

        auto font = makeFont (12.0f, juce::Font::bold, style.bodyTypeface);
        g.setColour (style.textPrimary);
        g.setFont (font);
        g.drawFittedText (button.getButtonText(), area.withTrimmedLeft (4), juce::Justification::centredLeft, 1);
    }

    void drawComboBox (juce::Graphics& g, int width, int height, bool, int, int, int, int, juce::ComboBox&) override
    {
        const auto style = getThemeStyle (theme);
        const auto bounds = juce::Rectangle<float> (0.5f, 0.5f, static_cast<float> (width) - 1.0f, static_cast<float> (height) - 1.0f);

        juce::ColourGradient fill (style.panelTop.brighter (0.12f), bounds.getCentreX(), bounds.getY(),
                                   style.panelBottom.darker (0.08f), bounds.getCentreX(), bounds.getBottom(), false);
        g.setGradientFill (fill);
        g.fillRoundedRectangle (bounds, 8.0f);

        g.setColour (style.buttonOutline);
        g.drawRoundedRectangle (bounds, 8.0f, 1.4f);

        juce::Path arrow;
        const auto arrowX = static_cast<float> (width) - 18.0f;
        const auto arrowY = static_cast<float> (height) * 0.5f - 2.0f;
        arrow.startNewSubPath (arrowX - 5.0f, arrowY);
        arrow.lineTo (arrowX, arrowY + 5.5f);
        arrow.lineTo (arrowX + 5.0f, arrowY);

        g.setColour (style.textPrimary);
        g.strokePath (arrow, juce::PathStrokeType (1.8f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
    }

    juce::Font getComboBoxFont (juce::ComboBox&) override
    {
        const auto style = getThemeStyle (theme);
        return makeFont (13.5f, juce::Font::bold, style.bodyTypeface);
    }

private:
    Theme theme = Theme::solar;
};
}

TheGreatAmericanSpringAudioProcessorEditor::TheGreatAmericanSpringAudioProcessorEditor (TheGreatAmericanSpringAudioProcessor& processor)
    : AudioProcessorEditor (&processor), audioProcessor (processor)
{
    audioProcessor.addChangeListener (this);
    setOpaque (true);

    lookAndFeel = std::make_unique<ArtDirectedLookAndFeel>();
    setLookAndFeel (lookAndFeel.get());

    solarBackground = loadImageFromBinaryData (BinaryData::background_session_09_png, BinaryData::background_session_09_pngSize);
    petalBackground = loadImageFromBinaryData (BinaryData::background_session_08_png, BinaryData::background_session_08_pngSize);
    cosmicBackground = loadImageFromBinaryData (BinaryData::background_session_03_png, BinaryData::background_session_03_pngSize);
    logoImage = createLogoImage (BinaryData::illicit_apothecary_logo_svg, BinaryData::illicit_apothecary_logo_svgSize);

    addAndMakeVisible (logoButton);
    refreshLogoButton();

    titleLabel.setText ("The Great American Spring", juce::dontSendNotification);
    titleLabel.setJustificationType (juce::Justification::centred);
    addAndMakeVisible (titleLabel);

    subtitleLabel.setText ({}, juce::dontSendNotification);
    subtitleLabel.setJustificationType (juce::Justification::centred);

    modeLabel.setText ("Mode", juce::dontSendNotification);
    addAndMakeVisible (modeLabel);

    ir2RoutingLabel.setText ("Ext Reverb Tanks", juce::dontSendNotification);
    addAndMakeVisible (ir2RoutingLabel);

    feedbackPhaseLabel.setText ("Feedback Phase", juce::dontSendNotification);
    addAndMakeVisible (feedbackPhaseLabel);

    themeLabel.setText ("Art", juce::dontSendNotification);
    addAndMakeVisible (themeLabel);

    const auto configureThemeButton = [] (juce::ToggleButton& button, const juce::String& text)
    {
        button.setButtonText (text);
        button.setClickingTogglesState (true);
        button.setRadioGroupId (1001);
        button.setConnectedEdges (juce::Button::ConnectedOnRight | juce::Button::ConnectedOnLeft);
    };

    configureThemeButton (solarThemeButton, "Solar");
    configureThemeButton (petalThemeButton, "Petal");
    configureThemeButton (cosmicThemeButton, "Cosmic");

    feedbackPhaseNormalButton.setButtonText ("Normal");
    feedbackPhaseInvertButton.setButtonText ("Invert");
    feedbackPhaseNormalButton.setRadioGroupId (2001);
    feedbackPhaseInvertButton.setRadioGroupId (2001);
    feedbackPhaseNormalButton.onClick = [this]
    {
        audioProcessor.setParameterPlainValue (TheGreatAmericanSpringAudioProcessor::feedbackPhaseInvertParameterID, 0.0f);
        refreshOptionControls();
    };
    feedbackPhaseInvertButton.onClick = [this]
    {
        audioProcessor.setParameterPlainValue (TheGreatAmericanSpringAudioProcessor::feedbackPhaseInvertParameterID, 1.0f);
        refreshOptionControls();
    };
    addAndMakeVisible (feedbackPhaseNormalButton);
    addAndMakeVisible (feedbackPhaseInvertButton);

    solarThemeButton.onClick = [this] { introThemeStep = 3; applyTheme (Theme::solar); };
    petalThemeButton.onClick = [this] { introThemeStep = 3; applyTheme (Theme::petal); };
    cosmicThemeButton.onClick = [this] { introThemeStep = 3; applyTheme (Theme::cosmic); };

    addAndMakeVisible (solarThemeButton);
    addAndMakeVisible (petalThemeButton);
    addAndMakeVisible (cosmicThemeButton);

    modeComboBox.addItem ("Clean", 1);
    modeComboBox.addItem ("Silicon", 2);
    modeComboBox.addItem ("LED", 3);
    modeComboBox.addItem ("Germanium", 4);
    addAndMakeVisible (modeComboBox);

    modeAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::modeParameterID, modeComboBox);

    ir2RoutingComboBox.addItem ("Off", 1);
    ir2RoutingComboBox.addItem ("Series", 2);
    ir2RoutingComboBox.addItem ("Parallel", 3);
    ir2RoutingComboBox.setTooltip ("Route Left/Right Ext Reverb Tanks off, in series after Main Tanks, or in parallel with Main Tanks.");
    ir2RoutingComboBox.onChange = [this] { refreshX2VisualState(); };
    addAndMakeVisible (ir2RoutingComboBox);

    ir2RoutingAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::x2TanksParameterID, ir2RoutingComboBox);

    configureRotarySlider (driveSlider, driveLabel, "Drive", " dB");
    configureRotarySlider (preHpfCutoffSlider, preHpfCutoffLabel, "HPF Cutoff", " Hz");
    configureRotarySlider (preHpfResonanceSlider, preHpfResonanceLabel, "HPF Q", "");
    configureRotarySlider (postLpfCutoffSlider, postLpfCutoffLabel, "LPF Cutoff", " Hz");
    configureRotarySlider (postLpfResonanceSlider, postLpfResonanceLabel, "LPF Q", "");
    configureRotarySlider (crossfadeAmountSlider, crossfadeAmountLabel, "Crossfade", " %");
    configureRotarySlider (extTankMixSlider, extTankMixLabel, "Ext Tanks", " %");
    configureRotarySlider (feedbackAmountSlider, feedbackAmountLabel, "Feedback", " %");
    configureRotarySlider (wetDrySlider, wetDryLabel, "Wet/Dry", " %");

    driveAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::driveParameterID, driveSlider);
    preHpfCutoffAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::preHpfCutoffParameterID, preHpfCutoffSlider);
    preHpfResonanceAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::preHpfResonanceParameterID, preHpfResonanceSlider);
    postLpfCutoffAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::postLpfCutoffParameterID, postLpfCutoffSlider);
    postLpfResonanceAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::postLpfResonanceParameterID, postLpfResonanceSlider);
    crossfadeAmountAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::crossfadeAmountParameterID, crossfadeAmountSlider);
    extTankMixAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::extTankMixParameterID, extTankMixSlider);
    feedbackAmountAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::feedbackAmountParameterID, feedbackAmountSlider);
    wetDryAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::wetDryParameterID, wetDrySlider);

    addAndMakeVisible (leftTankGroup);
    addAndMakeVisible (rightTankGroup);
    addAndMakeVisible (leftTank2Group);
    addAndMakeVisible (rightTank2Group);

    const auto styleTankLabel = [this] (juce::Label& label)
    {
        label.setJustificationType (juce::Justification::centredLeft);
        label.setMinimumHorizontalScale (0.7f);
        addAndMakeVisible (label);
    };

    styleTankLabel (leftTankLabel);
    styleTankLabel (rightTankLabel);
    styleTankLabel (leftTank2Label);
    styleTankLabel (rightTank2Label);

    leftTankLoadButton.setButtonText ("Load Left Main...");
    leftTankLoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::left1); };
    addAndMakeVisible (leftTankLoadButton);

    rightTankLoadButton.setButtonText ("Load Right Main...");
    rightTankLoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::right1); };
    addAndMakeVisible (rightTankLoadButton);

    leftTank2LoadButton.setButtonText ("Load Left Ext...");
    leftTank2LoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::left2); };
    addAndMakeVisible (leftTank2LoadButton);

    rightTank2LoadButton.setButtonText ("Load Right Ext...");
    rightTank2LoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::right2); };
    addAndMakeVisible (rightTank2LoadButton);

    playbackLabel.setText ("Playback Source", juce::dontSendNotification);
    playbackLabel.setJustificationType (juce::Justification::centredLeft);
    addAndMakeVisible (playbackLabel);

    playbackSourceComboBox.addItemList (audioProcessor.getPlaybackSourceDisplayNames(), 1);
    playbackSourceComboBox.setTextWhenNothingSelected ("Select playback source");
    playbackSourceComboBox.onChange = [this]
    {
        const auto selectedIndex = playbackSourceComboBox.getSelectedItemIndex();

        if (selectedIndex >= 0)
        {
            audioProcessor.setPlaybackSourceIndex (selectedIndex);
            refreshPlaybackLabel();
        }
    };
    addAndMakeVisible (playbackSourceComboBox);

    loadPlaybackButton.setButtonText ("Add Audio...");
    loadPlaybackButton.onClick = [this] { choosePlaybackFile(); };
    addAndMakeVisible (loadPlaybackButton);

    playbackToggleButton.onClick = [this]
    {
        audioProcessor.setPlaybackActive (! audioProcessor.isPlaybackActive());
        refreshPlaybackLabel();
    };
    addAndMakeVisible (playbackToggleButton);

    for (auto* btn : std::initializer_list<juce::TextButton*> { &leftTankLoadButton, &rightTankLoadButton,
                                                                 &leftTank2LoadButton, &rightTank2LoadButton,
                                                                 &loadPlaybackButton, &playbackToggleButton })
    {
        btn->getProperties().set ("gasInverted", true);
    }

    monoLeftRightSwapButton.setButtonText ("Mono L/R Swap");
    addAndMakeVisible (monoLeftRightSwapButton);
    monoLeftRightSwapAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::monoLeftRightSwapParameterID, monoLeftRightSwapButton);

    monoSourceToStereoButton.setButtonText ("Mono Source To Stereo");
    monoSourceToStereoButton.onClick = [this] { refreshOptionControls(); };
    addAndMakeVisible (monoSourceToStereoButton);
    monoSourceToStereoAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::monoSourceToStereoParameterID, monoSourceToStereoButton);

    showUnavailableTankControlsButton.setButtonText ("Options not available in real life");
    showUnavailableTankControlsButton.onClick = [this]
    {
        targetEditorHeight = showUnavailableTankControlsButton.getToggleState() ? 800 : 640;
        refreshOptionControls();
        startTimerHz (30);
    };
    addAndMakeVisible (showUnavailableTankControlsButton);
    showUnavailableTankControlsAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::showUnavailableTankControlsParameterID, showUnavailableTankControlsButton);

    animatedEditorHeight = audioProcessor.shouldShowUnavailableTankControls() ? 800 : 640;
    targetEditorHeight = animatedEditorHeight;
    setSize (920, animatedEditorHeight);
    refreshTankLabels();
    refreshPlaybackLabel();
    refreshOptionControls();
    applyTheme (Theme::solar);
    refreshX2VisualState();
    startTimerHz (30);
}

TheGreatAmericanSpringAudioProcessorEditor::~TheGreatAmericanSpringAudioProcessorEditor()
{
    setLookAndFeel (nullptr);
    audioProcessor.removeChangeListener (this);
}

void TheGreatAmericanSpringAudioProcessorEditor::paint (juce::Graphics& graphics)
{
    const auto style = getThemeStyle (currentTheme);
    const auto bounds = getLocalBounds().toFloat();

    const auto& backgroundImage = currentTheme == Theme::solar ? solarBackground
                               : currentTheme == Theme::petal ? petalBackground
                                                              : cosmicBackground;

    graphics.fillAll (style.backgroundBottom);

    if (backgroundImage.isValid())
    {
        graphics.setImageResamplingQuality (juce::Graphics::highResamplingQuality);
        graphics.drawImageWithin (backgroundImage,
                                  0,
                                  0,
                                  getWidth(),
                                  getHeight(),
                                  juce::RectanglePlacement::stretchToFit);
    }
    else
    {
        juce::ColourGradient fallback (style.backgroundTop, bounds.getCentreX(), bounds.getY(),
                                       style.backgroundBottom, bounds.getCentreX(), bounds.getBottom(), false);
        graphics.setGradientFill (fallback);
        graphics.fillAll();
    }

    auto panel = bounds.reduced (14.0f, 12.0f);
    juce::ColourGradient panelFill (style.panelTop.withAlpha (0.78f), panel.getCentreX(), panel.getY(),
                                    style.panelBottom.withAlpha (0.90f), panel.getCentreX(), panel.getBottom(), false);
    graphics.setColour (juce::Colours::black.withAlpha (0.24f));
    graphics.fillRoundedRectangle (panel.translated (0.0f, 5.0f), 24.0f);
    graphics.setGradientFill (panelFill);
    graphics.fillRoundedRectangle (panel, 24.0f);

    juce::ColourGradient centreGlow (style.textPrimary.withAlpha (0.11f), bounds.getCentreX(), bounds.getCentreY() - 36.0f,
                                     juce::Colours::transparentWhite, bounds.getCentreX(), bounds.getBottom(), true);
    graphics.setGradientFill (centreGlow);
    graphics.fillRoundedRectangle (panel.reduced (10.0f), 20.0f);

    graphics.setColour (style.panelOutline.withAlpha (0.92f));
    graphics.drawRoundedRectangle (panel, 24.0f, 1.8f);
    graphics.setColour (style.textPrimary.withAlpha (0.14f));
    graphics.drawRoundedRectangle (panel.reduced (7.0f), 18.0f, 1.0f);
}

void TheGreatAmericanSpringAudioProcessorEditor::resized()
{
    auto area = getLocalBounds().reduced (18);

    const auto centreRow = [] (juce::Rectangle<int> rowArea, int contentWidth)
    {
        return rowArea.withWidth (juce::jmin (contentWidth, rowArea.getWidth()))
                      .withX (rowArea.getX() + juce::jmax (0, (rowArea.getWidth() - contentWidth) / 2));
    };

    // --- Header: logo left | title + art + options stacked right ---
    auto headerArea = area.removeFromTop (168);
    logoButton.setBounds (headerArea.removeFromLeft (300).reduced (4, 2));

    titleLabel.setBounds (headerArea.removeFromTop (56));

    headerArea.removeFromTop (4);
    {
        auto artRow = headerArea.removeFromTop (30);
        const int artW = 28 + 6 + 68 + 68 + 84;
        auto artCentred = centreRow (artRow, artW);
        themeLabel.setBounds (artCentred.removeFromLeft (28));
        artCentred.removeFromLeft (6);
        solarThemeButton.setBounds (artCentred.removeFromLeft (68));
        petalThemeButton.setBounds (artCentred.removeFromLeft (68));
        cosmicThemeButton.setBounds (artCentred.removeFromLeft (84));
    }

    headerArea.removeFromTop (6);
    showUnavailableTankControlsButton.setBounds (centreRow (headerArea.removeFromTop (28), 340));

    subtitleLabel.setBounds ({});
    area.removeFromTop (10);

    // --- Control row: Mode | Ext Routing | Feedback Phase ---
    {
        auto controlRow = centreRow (area.removeFromTop (32), 800);
        auto leftCtrl = controlRow.removeFromLeft (420);
        controlRow.removeFromLeft (20);
        auto rightCtrl = controlRow;

        modeLabel.setBounds (leftCtrl.removeFromLeft (48));
        modeComboBox.setBounds (leftCtrl.removeFromLeft (130));
        leftCtrl.removeFromLeft (16);
        ir2RoutingLabel.setBounds (leftCtrl.removeFromLeft (116));
        ir2RoutingComboBox.setBounds (leftCtrl.removeFromLeft (110));

        feedbackPhaseLabel.setBounds (rightCtrl.removeFromLeft (104));
        feedbackPhaseNormalButton.setBounds (rightCtrl.removeFromLeft (88));
        feedbackPhaseInvertButton.setBounds (rightCtrl.removeFromLeft (78));
    }

    area.removeFromTop (8);

    // --- Mono switches row ---
    {
        auto monoRow = centreRow (area.removeFromTop (30), 500);
        monoLeftRightSwapButton.setBounds (monoRow.removeFromLeft (160));
        monoRow.removeFromLeft (22);
        monoSourceToStereoButton.setBounds (monoRow.removeFromLeft (228));
    }

    area.removeFromTop (10);

    // --- Knobs ---
    {
        auto knobArea = area.removeFromTop (214);
        const int knobWidth = 104;
        const int knobGap   = 22;
        const int knobHeight = 92;

        auto layoutKnob = [&] (juce::Rectangle<int> b, juce::Label& lbl, juce::Slider& sl)
        {
            lbl.setBounds (b.removeFromTop (18));
            sl.setBounds  (b.removeFromTop (knobHeight));
        };

        auto row1 = centreRow (knobArea.removeFromTop (knobHeight + 24), knobWidth * 5 + knobGap * 4);
        auto row2 = centreRow (knobArea.removeFromTop (knobHeight + 24), knobWidth * 4 + knobGap * 3);

        layoutKnob (row1.removeFromLeft (knobWidth), driveLabel,           driveSlider);           row1.removeFromLeft (knobGap);
        layoutKnob (row1.removeFromLeft (knobWidth), preHpfCutoffLabel,    preHpfCutoffSlider);    row1.removeFromLeft (knobGap);
        layoutKnob (row1.removeFromLeft (knobWidth), preHpfResonanceLabel, preHpfResonanceSlider); row1.removeFromLeft (knobGap);
        layoutKnob (row1.removeFromLeft (knobWidth), postLpfCutoffLabel,   postLpfCutoffSlider);   row1.removeFromLeft (knobGap);
        layoutKnob (row1.removeFromLeft (knobWidth), postLpfResonanceLabel,postLpfResonanceSlider);

        layoutKnob (row2.removeFromLeft (knobWidth), crossfadeAmountLabel, crossfadeAmountSlider); row2.removeFromLeft (knobGap);
        layoutKnob (row2.removeFromLeft (knobWidth), extTankMixLabel,      extTankMixSlider);      row2.removeFromLeft (knobGap);
        layoutKnob (row2.removeFromLeft (knobWidth), feedbackAmountLabel,  feedbackAmountSlider);  row2.removeFromLeft (knobGap);
        layoutKnob (row2.removeFromLeft (knobWidth), wetDryLabel,          wetDrySlider);
    }

    area.removeFromTop (10);

    // --- Tank groups (expandable) ---
    {
        const auto showTanks = showUnavailableTankControlsButton.getToggleState();
        auto tankArea = centreRow (area.removeFromTop (showTanks ? 152 : 0), 880);
        auto topRow   = tankArea.removeFromTop (66);
        tankArea.removeFromTop (10);
        auto botRow   = tankArea;

        auto la  = topRow.removeFromLeft ((topRow.getWidth() - 14) / 2);  topRow.removeFromLeft (14);
        auto ra  = topRow;
        auto la2 = botRow.removeFromLeft ((botRow.getWidth() - 14) / 2);  botRow.removeFromLeft (14);
        auto ra2 = botRow;

        const auto layoutGroup = [] (juce::Rectangle<int> g,
                                     juce::GroupComponent& grp,
                                     juce::Label& lbl,
                                     juce::TextButton& btn)
        {
            grp.setBounds (g);
            auto inner = g.reduced (10, 12);
            lbl.setBounds (inner.removeFromTop (18));
            inner.removeFromTop (4);
            btn.setBounds (inner.removeFromTop (22));
        };

        layoutGroup (la,  leftTankGroup,   leftTankLabel,   leftTankLoadButton);
        layoutGroup (ra,  rightTankGroup,  rightTankLabel,  rightTankLoadButton);
        layoutGroup (la2, leftTank2Group,  leftTank2Label,  leftTank2LoadButton);
        layoutGroup (ra2, rightTank2Group, rightTank2Label, rightTank2LoadButton);
    }

    area.removeFromTop (8);

    // --- Playback ---
    playbackLabel.setBounds (area.removeFromTop (18));
    area.removeFromTop (4);

    {
        auto pb = centreRow (area.removeFromTop (28), 880);
        playbackSourceComboBox.setBounds (pb.removeFromLeft (640));
        pb.removeFromLeft (10);
        loadPlaybackButton.setBounds (pb.removeFromLeft (108));
        pb.removeFromLeft (10);
        playbackToggleButton.setBounds (pb.removeFromLeft (72));
    }
}
void TheGreatAmericanSpringAudioProcessorEditor::configureRotarySlider (juce::Slider& slider,
                                                                          juce::Label& label,
                                                                          const juce::String& labelText,
                                                                          const juce::String& suffix)
{
    label.setText (labelText, juce::dontSendNotification);
    label.setJustificationType (juce::Justification::centred);
    addAndMakeVisible (label);

    slider.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle (juce::Slider::TextBoxBelow, false, 84, 20);
    slider.setTextValueSuffix (suffix);
    addAndMakeVisible (slider);
}

void TheGreatAmericanSpringAudioProcessorEditor::applyTheme (Theme newTheme)
{
    currentTheme = newTheme;
    auto* themedLookAndFeel = dynamic_cast<ArtDirectedLookAndFeel*> (lookAndFeel.get());
    jassert (themedLookAndFeel != nullptr);

    if (themedLookAndFeel != nullptr)
        themedLookAndFeel->setTheme (currentTheme);

    const auto style = getThemeStyle (currentTheme);

    titleLabel.setFont (makeFont (28.0f, juce::Font::bold, style.titleTypeface));
    subtitleLabel.setFont (makeFont (12.0f, juce::Font::plain, style.bodyTypeface));
    modeLabel.setFont (makeFont (12.5f, juce::Font::bold, style.bodyTypeface));
    ir2RoutingLabel.setFont (makeFont (12.5f, juce::Font::bold, style.bodyTypeface));
    feedbackPhaseLabel.setFont (makeFont (12.5f, juce::Font::bold, style.bodyTypeface));
    themeLabel.setFont (makeFont (12.5f, juce::Font::bold, style.bodyTypeface));
    titleLabel.setColour (juce::Label::textColourId, style.textPrimary);
    subtitleLabel.setColour (juce::Label::textColourId, style.textSecondary);
    modeLabel.setColour (juce::Label::textColourId, style.textPrimary);
    ir2RoutingLabel.setColour (juce::Label::textColourId, style.textPrimary);
    feedbackPhaseLabel.setColour (juce::Label::textColourId, style.textPrimary);
    themeLabel.setColour (juce::Label::textColourId, style.textPrimary);

    const auto styleComboBox = [&style] (juce::ComboBox& comboBox)
    {
        comboBox.setColour (juce::ComboBox::textColourId, style.textPrimary);
        comboBox.setColour (juce::ComboBox::backgroundColourId, juce::Colours::transparentBlack);
        comboBox.setColour (juce::ComboBox::outlineColourId, juce::Colours::transparentBlack);
        comboBox.setColour (juce::ComboBox::arrowColourId, style.textPrimary);
    };

    styleComboBox (modeComboBox);
    styleComboBox (ir2RoutingComboBox);
    styleComboBox (playbackSourceComboBox);

    const auto styleControlLabel = [&style] (juce::Label& label)
    {
        label.setFont (makeFont (12.0f, juce::Font::bold, style.bodyTypeface));
        label.setColour (juce::Label::textColourId, style.textPrimary);
    };

    for (auto* label : { &driveLabel, &preHpfCutoffLabel, &preHpfResonanceLabel, &postLpfCutoffLabel,
                         &postLpfResonanceLabel, &crossfadeAmountLabel, &extTankMixLabel, &feedbackAmountLabel, &wetDryLabel,
                         &leftTankLabel, &rightTankLabel, &leftTank2Label, &rightTank2Label, &playbackLabel })
    {
        styleControlLabel (*label);
    }

    playbackLabel.setFont (makeFont (12.0f, juce::Font::bold, style.bodyTypeface));

    const auto styleSlider = [&style] (juce::Slider& slider)
    {
        slider.setColour (juce::Slider::textBoxTextColourId, style.textPrimary);
        slider.setColour (juce::Slider::textBoxBackgroundColourId, style.panelBottom.withAlpha (0.96f));
        slider.setColour (juce::Slider::textBoxOutlineColourId, style.buttonOutline.withAlpha (0.85f));
        slider.setColour (juce::Slider::rotarySliderFillColourId, style.knobStart);
        slider.setColour (juce::Slider::rotarySliderOutlineColourId, style.knobTrack);
        slider.setColour (juce::Slider::thumbColourId, style.radioFill);
    };

    for (auto* slider : { &driveSlider, &preHpfCutoffSlider, &preHpfResonanceSlider, &postLpfCutoffSlider,
                          &postLpfResonanceSlider, &crossfadeAmountSlider, &extTankMixSlider, &feedbackAmountSlider, &wetDrySlider })
    {
        styleSlider (*slider);
    }

    leftTankGroup.setText ("Left Main Tanks");
    rightTankGroup.setText ("Right Main Tanks");
    leftTank2Group.setText ("Left Ext Reverb Tanks");
    rightTank2Group.setText ("Right Ext Reverb Tanks");
    leftTankGroup.setColour (juce::GroupComponent::outlineColourId, style.accentA);
    leftTankGroup.setColour (juce::GroupComponent::textColourId, style.textPrimary);
    rightTankGroup.setColour (juce::GroupComponent::outlineColourId, style.accentB);
    rightTankGroup.setColour (juce::GroupComponent::textColourId, style.textPrimary);
    leftTank2Group.setColour (juce::GroupComponent::outlineColourId, style.accentC);
    leftTank2Group.setColour (juce::GroupComponent::textColourId, style.textPrimary);
    rightTank2Group.setColour (juce::GroupComponent::outlineColourId, style.radioFill);
    rightTank2Group.setColour (juce::GroupComponent::textColourId, style.textPrimary);

    refreshThemeButtons();
    refreshLogoButton();
    refreshOptionControls();
    refreshX2VisualState();
    repaint();
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshThemeButtons()
{
    solarThemeButton.setToggleState (currentTheme == Theme::solar, juce::dontSendNotification);
    petalThemeButton.setToggleState (currentTheme == Theme::petal, juce::dontSendNotification);
    cosmicThemeButton.setToggleState (currentTheme == Theme::cosmic, juce::dontSendNotification);
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshLogoButton()
{
    logoButton.setImages (false,
                          true,
                          true,
                          logoImage,
                          1.0f,
                          juce::Colours::transparentBlack,
                          logoImage,
                          0.92f,
                          getThemeStyle (currentTheme).radioFill.withAlpha (0.12f),
                          logoImage,
                          0.84f,
                           getThemeStyle (currentTheme).accentA.withAlpha (0.18f));
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshOptionControls()
{
    const auto feedbackInverted = audioProcessor.isFeedbackPhaseInverted();
    feedbackPhaseNormalButton.setToggleState (! feedbackInverted, juce::dontSendNotification);
    feedbackPhaseInvertButton.setToggleState (feedbackInverted, juce::dontSendNotification);

    const auto crossfadeAvailable = audioProcessor.isCrossfadeAvailableForCurrentLayout();
    crossfadeAmountSlider.setEnabled (crossfadeAvailable);
    crossfadeAmountLabel.setAlpha (crossfadeAvailable ? 1.0f : 0.45f);
    crossfadeAmountSlider.setAlpha (crossfadeAvailable ? 1.0f : 0.45f);

    if (! crossfadeAvailable)
    {
        if (std::abs (crossfadeAmountSlider.getValue()) > 0.0001)
            audioProcessor.setParameterPlainValue (TheGreatAmericanSpringAudioProcessor::crossfadeAmountParameterID, 0.0f);

        crossfadeAmountSlider.setValue (0.0, juce::dontSendNotification);
    }

    const auto showTankControls = showUnavailableTankControlsButton.getToggleState();

    juce::Component* tankControls[] = { &leftTankGroup, &rightTankGroup, &leftTank2Group, &rightTank2Group,
                                        &leftTankLabel, &rightTankLabel, &leftTank2Label, &rightTank2Label,
                                        &leftTankLoadButton, &rightTankLoadButton, &leftTank2LoadButton, &rightTank2LoadButton };

    for (auto* component : tankControls)
    {
        component->setVisible (showTankControls);
    }

    targetEditorHeight = showTankControls ? 800 : 640;
}

void TheGreatAmericanSpringAudioProcessorEditor::updateExpandedTankControlsAnimation()
{
    if (animatedEditorHeight == targetEditorHeight)
        return;

    const auto direction = targetEditorHeight > animatedEditorHeight ? 1 : -1;
    animatedEditorHeight += direction * 18;

    if ((direction > 0 && animatedEditorHeight > targetEditorHeight)
        || (direction < 0 && animatedEditorHeight < targetEditorHeight))
    {
        animatedEditorHeight = targetEditorHeight;
    }

    setSize (getWidth(), animatedEditorHeight);
}

void TheGreatAmericanSpringAudioProcessorEditor::timerCallback()
{
    introElapsedMs += 33;

    if (introThemeStep == 0 && introElapsedMs >= 1000)
    {
        introThemeStep = 1;
        applyTheme (Theme::petal);
    }

    if (introThemeStep == 1 && introElapsedMs >= 2000)
    {
        introThemeStep = 2;
        applyTheme (Theme::cosmic);
    }

    if (introThemeStep == 2 && introElapsedMs >= 3000)
    {
        introThemeStep = 3;
        applyTheme (Theme::solar);
    }

    updateExpandedTankControlsAnimation();
    refreshOptionControls();
}

void TheGreatAmericanSpringAudioProcessorEditor::chooseTankImpulseResponseFile (TankSlot slot)
{
    auto safeThis = juce::Component::SafePointer<TheGreatAmericanSpringAudioProcessorEditor> (this);
    activeChooser = std::make_unique<juce::FileChooser> ("Select spring tank IR",
                                                         audioProcessor.getSpringIrDirectory(),
                                                         "*.wav;*.aif;*.aiff;*.flac");

    activeChooser->launchAsync (juce::FileBrowserComponent::openMode | juce::FileBrowserComponent::canSelectFiles,
                                [safeThis, slot] (const juce::FileChooser& chooser)
                                {
                                    if (safeThis == nullptr)
                                        return;

                                    const auto selectedFile = chooser.getResult();
                                    safeThis->activeChooser.reset();

                                    if (selectedFile.existsAsFile())
                                    {
                                        safeThis->audioProcessor.loadTankImpulseResponseFile (slot, selectedFile);
                                        safeThis->refreshTankLabels();
                                    }
                                });
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshTankLabels()
{
    leftTankLabel.setText (audioProcessor.getTankImpulseResponseDisplayName (TankSlot::left1), juce::dontSendNotification);
    rightTankLabel.setText (audioProcessor.getTankImpulseResponseDisplayName (TankSlot::right1), juce::dontSendNotification);
    leftTank2Label.setText (audioProcessor.getTankImpulseResponseDisplayName (TankSlot::left2), juce::dontSendNotification);
    rightTank2Label.setText (audioProcessor.getTankImpulseResponseDisplayName (TankSlot::right2), juce::dontSendNotification);
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshX2VisualState()
{
    const auto style = getThemeStyle (currentTheme);
    const auto x2Enabled = audioProcessor.isX2Enabled();
    const auto routingName = audioProcessor.getIr2RoutingDisplayName();
    const auto secondaryText = x2Enabled ? style.textPrimary : style.textSecondary.withMultipliedAlpha (0.7f);
    const auto secondaryOutline = x2Enabled ? style.accentC : style.knobTrack;

    leftTank2Group.setText ("Left Ext Reverb Tanks - " + routingName);
    rightTank2Group.setText ("Right Ext Reverb Tanks - " + routingName);
    leftTank2Group.setColour (juce::GroupComponent::outlineColourId, secondaryOutline);
    leftTank2Group.setColour (juce::GroupComponent::textColourId, secondaryText);
    rightTank2Group.setColour (juce::GroupComponent::outlineColourId, secondaryOutline);
    rightTank2Group.setColour (juce::GroupComponent::textColourId, secondaryText);
    leftTank2Label.setColour (juce::Label::textColourId, secondaryText);
    rightTank2Label.setColour (juce::Label::textColourId, secondaryText);
    ir2RoutingLabel.setColour (juce::Label::textColourId, style.textPrimary);
    leftTank2LoadButton.setAlpha (x2Enabled ? 1.0f : 0.5f);
    rightTank2LoadButton.setAlpha (x2Enabled ? 1.0f : 0.5f);
    ir2RoutingComboBox.setAlpha (x2Enabled ? 1.0f : 0.86f);
}

void TheGreatAmericanSpringAudioProcessorEditor::choosePlaybackFile()
{
    auto safeThis = juce::Component::SafePointer<TheGreatAmericanSpringAudioProcessorEditor> (this);
    activeChooser = std::make_unique<juce::FileChooser> ("Select audio file to play",
                                                         juce::File {},
                                                         "*.wav;*.aif;*.aiff;*.flac;*.mp3");

    activeChooser->launchAsync (juce::FileBrowserComponent::openMode | juce::FileBrowserComponent::canSelectFiles,
                                [safeThis] (const juce::FileChooser& chooser)
                                {
                                    if (safeThis == nullptr)
                                        return;

                                    const auto selectedFile = chooser.getResult();
                                    safeThis->activeChooser.reset();

                                    if (selectedFile.existsAsFile())
                                    {
                                        safeThis->audioProcessor.loadPlaybackFile (selectedFile);
                                        safeThis->refreshPlaybackLabel();
                                    }
                                });
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshPlaybackLabel()
{
    playbackLabel.setText ("Playback Source", juce::dontSendNotification);
    const auto selectedIndex = audioProcessor.getSelectedPlaybackSourceIndex();

    if (selectedIndex >= 0)
        playbackSourceComboBox.setSelectedItemIndex (selectedIndex, juce::dontSendNotification);
    else
        playbackSourceComboBox.setText (audioProcessor.getPlaybackFileDisplayName(), juce::dontSendNotification);

    playbackToggleButton.setButtonText (audioProcessor.isPlaybackActive() ? "Stop" : "Play");
    playbackToggleButton.setEnabled (audioProcessor.hasPlaybackFile());
}

void TheGreatAmericanSpringAudioProcessorEditor::changeListenerCallback (juce::ChangeBroadcaster* source)
{
    if (source == &audioProcessor)
    {
        refreshTankLabels();
        refreshX2VisualState();
        refreshPlaybackLabel();
    }
}
