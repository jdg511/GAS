#include <BinaryData.h>

#include "PluginEditor.h"

namespace
{
using Theme = TheGreatAmericanSpringAudioProcessorEditor::Theme;

constexpr int presetMenuItemBaseId = 1001;
constexpr int savePresetMenuItemId = 9001;

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

/** Pick the most Art-Nouveau-flavoured display face actually installed on the
    host. Falls back gracefully to a refined serif so the title is always legible.
*/
juce::String pickArtNouveauTypeface()
{
    static const juce::String preferred[] = {
        "Harrington",          // Belle Epoque / Art Nouveau display face (Windows)
        "Goudy Stout",
        "Bauhaus 93",
        "Felix Titling",
        "Modern No. 20",
        "Bodoni MT",
        "Georgia"
    };

    const auto available = juce::Font::findAllTypefaceNames();
    for (const auto& name : preferred)
        if (available.contains (name))
            return name;

    return "Georgia";
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
                "Felix Titling",
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
                "Felix Titling",
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
                "Felix Titling",
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
                           juce::Slider& slider) override
    {
        const auto style = getThemeStyle (theme);
        const auto bounds = juce::Rectangle<float> (static_cast<float> (x), static_cast<float> (y),
                                                    static_cast<float> (width), static_cast<float> (height)).reduced (8.0f, 4.0f);
        const auto radius = juce::jmin (bounds.getWidth(), bounds.getHeight()) * 0.5f;
        const auto centre = bounds.getCentre();
        const auto angle = rotaryStartAngle + sliderPosProportional * (rotaryEndAngle - rotaryStartAngle);
        const auto knobBounds = juce::Rectangle<float> (radius * 2.0f, radius * 2.0f).withCentre (centre);
        const bool pulled = slider.getProperties()["pulled"];
        const bool pullKnob = slider.getProperties().contains ("pulled");

        if (pulled)
        {
            // Pulled out: a warm halo and a raised rim so it reads as "engaged"
            // from across the room, like a push-pull pot sitting proud.
            juce::ColourGradient halo (style.accentB.withAlpha (0.55f), centre.x, centre.y,
                                       style.accentB.withAlpha (0.0f), centre.x + radius * 1.6f, centre.y, true);
            g.setGradientFill (halo);
            g.fillEllipse (knobBounds.expanded (radius * 0.55f));

            g.setColour (style.accentB.withAlpha (0.95f));
            g.drawEllipse (knobBounds.expanded (4.0f), 2.2f);
        }
        else if (pullKnob)
        {
            // Pushed in: a faint dotted ring hints that this knob pulls.
            g.setColour (style.textSecondary.withAlpha (0.35f));
            juce::Path ringPath, dashed;
            ringPath.addEllipse (knobBounds.expanded (4.0f));
            const float dashes[] = { 2.0f, 4.0f };
            juce::PathStrokeType (1.0f).createDashedStroke (dashed, ringPath, dashes, 2);
            g.fillPath (dashed);
        }

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
            auto base = button.getToggleState() ? style.panelTop.brighter (0.22f) : style.panelTop.brighter (0.12f);
            if (shouldDrawButtonAsDown)        base = base.darker (0.16f);
            else if (shouldDrawButtonAsHighlighted) base = base.brighter (0.12f);
            juce::ColourGradient fill (base, bounds.getCentreX(), bounds.getY(),
                                       style.panelBottom.darker (0.08f), bounds.getCentreX(), bounds.getBottom(), false);
            g.setGradientFill (fill);
            g.fillRoundedRectangle (bounds, 8.0f);
            g.setColour (style.buttonOutline);
            g.drawRoundedRectangle (bounds, 8.0f, 1.4f);
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
            auto font = makeFont (12.5f, juce::Font::bold, style.bodyTypeface);
            g.setColour (style.textPrimary);
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

    content.addAndMakeVisible (logoButton);
    refreshLogoButton();

    content.addAndMakeVisible (titleComponent);

    subtitleLabel.setText ({}, juce::dontSendNotification);
    subtitleLabel.setJustificationType (juce::Justification::centred);

    ir2RoutingLabel.setText ("Ext Tanks", juce::dontSendNotification);
    content.addAndMakeVisible (ir2RoutingLabel);

    feedbackPhaseLabel.setText ("FB Phase", juce::dontSendNotification);
    content.addAndMakeVisible (feedbackPhaseLabel);

    dynamicsLabel.setText ("FB Dyn", juce::dontSendNotification);
    dynamicsLabel.setTooltip ("Three-way switch in the feedback RETURN leg, between the Feedback tap and the Fb In summer: Comp (MMBF5457 FET, 1176 territory), Off, Limit (Coolaudio V2181 VCA, 10:1). Both start at -24 dBFS. It holds down what recirculates, so turning Feedback up stops running away; the wet signal going to the output is untouched by it.");
    content.addAndMakeVisible (dynamicsLabel);

    stereoModeLabel.setText ("Setting", juce::dontSendNotification);
    content.addAndMakeVisible (stereoModeLabel);

    tubeSwitchLabel.setText ("Tube", juce::dontSendNotification);
    tubeSwitchLabel.setTooltip ("Rev C mini toggle beside the In knob: Off = solid state, On = the J201 tube stage (which also puts the tube on the output).");
    content.addAndMakeVisible (tubeSwitchLabel);

    dirtSwitchLabel.setText ("Dirt", juce::dontSendNotification);
    dirtSwitchLabel.setTooltip ("Rev C mini toggle beside the Gain knob: Off = clean, On = the Tube Screamer clipper (2x 1N4148).");
    content.addAndMakeVisible (dirtSwitchLabel);

    tapeSwitchLabel.setText ("Tape", juce::dontSendNotification);
    tapeSwitchLabel.setTooltip ("Rev C mini toggle beside the Out knob: Off = solid state, On = the 2N3904 differential pair tape stage. The tube runs first when Tube is on.");
    content.addAndMakeVisible (tapeSwitchLabel);

    themeLabel.setText ("Art", juce::dontSendNotification);
    content.addAndMakeVisible (themeLabel);

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
    content.addAndMakeVisible (feedbackPhaseNormalButton);
    content.addAndMakeVisible (feedbackPhaseInvertButton);

    // Comp / Off / Limit: a three-position switch, drawn as three radio buttons.
    const auto configureChoiceButton = [this] (juce::ToggleButton& button, const juce::String& text, int group,
                                               const juce::String& parameterID, float value, const juce::String& tip)
    {
        button.setButtonText (text);
        button.setRadioGroupId (group);
        button.setTooltip (tip);
        button.onClick = [this, parameterID, value]
        {
            audioProcessor.setParameterPlainValue (parameterID, value);
            refreshOptionControls();
        };
        content.addAndMakeVisible (button);
    };

    using P = TheGreatAmericanSpringAudioProcessor;
    configureChoiceButton (dynamicsCompButton,  "Comp",  3001, P::dynamicsParameterID, 0.0f, "MMBF5457 FET compressor (1176 territory) in the feedback RETURN leg, feedback sidechain, stereo linked. Threshold -24 dBFS. It tames what goes back round the loop, so the wet signal you hear keeps its own dynamics.");
    configureChoiceButton (dynamicsOffButton,   "Off",   3001, P::dynamicsParameterID, 1.0f, "Nothing in the feedback return leg. The loop is held only by the Feedback amount itself.");
    configureChoiceButton (dynamicsLimitButton, "Limit", 3001, P::dynamicsParameterID, 2.0f, "Coolaudio V2181 VCA limiter with a log-average detector, 10:1, stereo linked, in the feedback RETURN leg. Threshold -24 dBFS. The harder stop of the two when the loop starts running away.");

    configureChoiceButton (stereoButton,       "Stereo",        4001, P::stereoModeParameterID, 0.0f, "L and R each run their own tank path; feedback stays in its own channel.");
    configureChoiceButton (monoToStereoButton, "Mono > Stereo", 4001, P::stereoModeParameterID, 1.0f, "A mono source is copied to both channels first, then runs as Stereo.");
    configureChoiceButton (megaverbButton,     "MEGAVERB",      4001, P::stereoModeParameterID, 2.0f, "Feedback crosses over: what leaves the Left path is fed to the start of the Right path and vice versa, so echoes ping-pong L > R > L through both tank chains.");

    // Rev C: the Vol / Gain / Output pulls are now three separate mini toggles on the control deck,
    // so they get the same two-position switch treatment here as FB Phase.
    configureChoiceButton (tubeOffButton, "Off", 5001, P::inputTubeParameterID,  0.0f, "In stage stays solid state.");
    configureChoiceButton (tubeOnButton,  "On",  5001, P::inputTubeParameterID,  1.0f, "J201 tube stage in the In section, and the tube also runs on the output.");
    configureChoiceButton (dirtOffButton, "Off", 5002, P::dirtParameterID,       0.0f, "Gain stage stays clean.");
    configureChoiceButton (dirtOnButton,  "On",  5002, P::dirtParameterID,       1.0f, "Tube Screamer clipper (2x 1N4148) in the Gain section.");
    configureChoiceButton (tapeOffButton, "Off", 5003, P::outputTapeParameterID, 0.0f, "Out stage stays solid state.");
    configureChoiceButton (tapeOnButton,  "On",  5003, P::outputTapeParameterID, 1.0f, "2N3904 differential pair tape stage on the output.");

    // Each metering point shows Left and Right separately, so a lopsided tank
    // or a one-sided feedback build-up is visible rather than averaged away.
    const auto configureMeterPair = [this] (juce::Label& groupLabel, const juce::String& groupText,
                                            juce::Label& labelL, LevelMeter& meterL,
                                            juce::Label& labelR, LevelMeter& meterR,
                                            const juce::String& tip)
    {
        groupLabel.setText (groupText, juce::dontSendNotification);
        groupLabel.setJustificationType (juce::Justification::centredRight);
        content.addAndMakeVisible (groupLabel);

        labelL.setText ("L", juce::dontSendNotification);
        labelR.setText ("R", juce::dontSendNotification);

        for (auto* channelLabel : { &labelL, &labelR })
        {
            channelLabel->setJustificationType (juce::Justification::centredRight);
            content.addAndMakeVisible (*channelLabel);
        }

        meterL.setTooltip ("Left. " + tip);
        meterR.setTooltip ("Right. " + tip);
        content.addAndMakeVisible (meterL);
        content.addAndMakeVisible (meterR);
    };

    configureMeterPair (inputMeterLabel, "In",
                        inputMeterLabelL, inputMeterL, inputMeterLabelR, inputMeterR,
                        "Peak level straight after the In (Solid State / Tube) knob. Plugin only. 0 to -48 dBFS.");
    configureMeterPair (wetMeterLabel, "Wet",
                        wetMeterLabelL, wetMeterL, wetMeterLabelR, wetMeterR,
                        "Peak level straight after the Gain / Dirt / Comp-Limit circuit, just before the feedback path. Plugin only. 0 to -48 dBFS.");
    configureMeterPair (outputMeterLabel, "Out",
                        outputMeterLabelL, outputMeterL, outputMeterLabelR, outputMeterR,
                        "Peak level at the very end, after Post Output. Plugin only. 0 to -48 dBFS.");

    solarThemeButton.onClick = [this] { introThemeStep = 3; applyTheme (Theme::solar); };
    petalThemeButton.onClick = [this] { introThemeStep = 3; applyTheme (Theme::petal); };
    cosmicThemeButton.onClick = [this] { introThemeStep = 3; applyTheme (Theme::cosmic); };

    content.addAndMakeVisible (solarThemeButton);
    content.addAndMakeVisible (petalThemeButton);
    content.addAndMakeVisible (cosmicThemeButton);

    content.addAndMakeVisible (chainDescriptionDisplay);

    ir2RoutingComboBox.addItem ("Off", 1);
    ir2RoutingComboBox.addItem ("Series", 2);
    ir2RoutingComboBox.addItem ("Parallel", 3);
    ir2RoutingComboBox.setTooltip ("Route Left/Right Ext Reverb Tanks off, in series after Main Tanks, or in parallel with Main Tanks.");
    ir2RoutingComboBox.onChange = [this] { refreshX2VisualState(); };
    content.addAndMakeVisible (ir2RoutingComboBox);

    ir2RoutingAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::x2TanksParameterID, ir2RoutingComboBox);

    railOversamplingLabel.setText ("Oversampling", juce::dontSendNotification);
    railOversamplingLabel.setJustificationType (juce::Justification::centredRight);
    content.addAndMakeVisible (railOversamplingLabel);

    railOversamplingComboBox.addItem ("Off", 1);
    railOversamplingComboBox.addItem ("2x", 2);
    railOversamplingComboBox.addItem ("4x", 3);
    railOversamplingComboBox.addItem ("8x", 4);
    railOversamplingComboBox.setTooltip ("Plugin only. Clipping at the op-amp rails makes harmonics, and at the plain sample rate the "
                                         "ones above Nyquist fold back down as aliasing, which the real circuit never does. Running the "
                                         "rail saturation faster moves them out of the way first. 4x matches the tube, tape and Tube "
                                         "Screamer stages and is the default. 8x rejects a little more at more CPU; Off is cheapest and "
                                         "only matters when you drive the board nodes past about +5.5 dBFS.");
    content.addAndMakeVisible (railOversamplingComboBox);

    railOversamplingAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::railOversamplingParameterID, railOversamplingComboBox);

    configureRotarySlider (preInputLevelSlider, preInputLevelLabel, "Pre Input", " dB");
    configureRotarySlider (inputLevelSlider, inputLevelLabel, "In", " dB");
    configureRotarySlider (gainSlider, gainLabel, "Gain", " dB");
    configureRotarySlider (preHpfCutoffSlider, preHpfCutoffLabel, "HPF Cutoff", " Hz");
    configureRotarySlider (postLpfCutoffSlider, postLpfCutoffLabel, "LPF Cutoff", " Hz");
    // No suffix, and no fixed label or text: refreshX2VisualState sets both to match the
    // routing, because the knob does a different job in each of the three positions.
    configureRotarySlider (extTankMixSlider, extTankMixLabel, "Short / Long Tank Mix", "");
    // Read-only: the Parallel reading is two numbers, which cannot be typed back in
    // sensibly, and an edit would parse as the first one.
    extTankMixSlider.setTextBoxStyle (juce::Slider::TextBoxBelow, true, 112, 20);
    // Longest knob label in either row, so let it squeeze rather than clip.
    extTankMixLabel.setMinimumHorizontalScale (0.6f);
    // No suffix on these two either: the parameters now print "50%" themselves, and a
    // slider suffix would make it "50% %".
    configureRotarySlider (feedbackAmountSlider, feedbackAmountLabel, "Feedback", "");
    configureRotarySlider (wetDrySlider, wetDryLabel, "Wet/Dry", "");
    configureRotarySlider (outputLevelSlider, outputLevelLabel, "Out", " dB");
    configureRotarySlider (postOutputLevelSlider, postOutputLevelLabel, "Post Output", " dB");

    for (auto* slider : std::initializer_list<juce::Slider*> { &preInputLevelSlider, &inputLevelSlider, &gainSlider,
                                                               &outputLevelSlider, &postOutputLevelSlider })
        slider->setNumDecimalPlacesToDisplay (1);

    preInputLevelSlider.setTooltip ("Plugin-only trim ahead of everything, -48 to +18 dB. Not on the PCB.");
    postOutputLevelSlider.setTooltip ("Plugin-only trim after everything, -48 to +18 dB. Not on the PCB.");

    // Rev C: no more pull knobs. Tube, Dirt and Tape are the panel's own mini toggles, so these are
    // plain level knobs and the switch row below the Setting row does the switching.
    inputLevelSlider.setTooltip ("In, -18 to +18 dB, first knob on the wet path. Solid State or Tube is set by the TUBE switch.");
    gainSlider.setTooltip ("Gain, -18 to +18 dB, into the Dirt and Comp / Limit circuits. Clean or Dirt is set by the DIRT switch.");
    outputLevelSlider.setTooltip ("Out, -18 to +18 dB, after the Wet/Dry mix. Solid State or Tape is set by the TAPE switch. The tube runs first when TUBE is on.");

    gainAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::gainParameterID, gainSlider);
    preInputLevelAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::preInputLevelParameterID, preInputLevelSlider);
    postOutputLevelAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::postOutputLevelParameterID, postOutputLevelSlider);
    preHpfCutoffAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::preHpfCutoffParameterID, preHpfCutoffSlider);
    postLpfCutoffAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::postLpfCutoffParameterID, postLpfCutoffSlider);
    extTankMixAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::extTankMixParameterID, extTankMixSlider);
    feedbackAmountAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::feedbackAmountParameterID, feedbackAmountSlider);
    wetDryAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::wetDryParameterID, wetDrySlider);
    inputLevelAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::inputLevelParameterID, inputLevelSlider);
    outputLevelAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::outputLevelParameterID, outputLevelSlider);

    content.addAndMakeVisible (leftTankGroup);
    content.addAndMakeVisible (rightTankGroup);
    content.addAndMakeVisible (leftTank2Group);
    content.addAndMakeVisible (rightTank2Group);

    const auto styleTankLabel = [this] (juce::Label& label)
    {
        label.setJustificationType (juce::Justification::centredLeft);
        label.setMinimumHorizontalScale (0.7f);
        content.addAndMakeVisible (label);
    };

    styleTankLabel (leftTankLabel);
    styleTankLabel (rightTankLabel);
    styleTankLabel (leftTank2Label);
    styleTankLabel (rightTank2Label);

    leftTankLoadButton.setButtonText ("Load Left Main...");
    leftTankLoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::left1); };
    content.addAndMakeVisible (leftTankLoadButton);

    rightTankLoadButton.setButtonText ("Load Right Main...");
    rightTankLoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::right1); };
    content.addAndMakeVisible (rightTankLoadButton);

    leftTank2LoadButton.setButtonText ("Load Left Ext...");
    leftTank2LoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::left2); };
    content.addAndMakeVisible (leftTank2LoadButton);

    rightTank2LoadButton.setButtonText ("Load Right Ext...");
    rightTank2LoadButton.onClick = [this] { chooseTankImpulseResponseFile (TankSlot::right2); };
    content.addAndMakeVisible (rightTank2LoadButton);

    playbackLabel.setText ("Playback Source", juce::dontSendNotification);
    playbackLabel.setJustificationType (juce::Justification::centredLeft);
    content.addAndMakeVisible (playbackLabel);

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
    content.addAndMakeVisible (playbackSourceComboBox);

    loadPlaybackButton.setButtonText ("Add Audio...");
    loadPlaybackButton.onClick = [this] { choosePlaybackFile(); };
    content.addAndMakeVisible (loadPlaybackButton);

    playbackToggleButton.onClick = [this]
    {
        audioProcessor.setPlaybackActive (! audioProcessor.isPlaybackActive());
        refreshPlaybackLabel();
    };
    content.addAndMakeVisible (playbackToggleButton);

    for (auto* btn : std::initializer_list<juce::TextButton*> { &leftTankLoadButton, &rightTankLoadButton,
                                                                 &leftTank2LoadButton, &rightTank2LoadButton,
                                                                 &loadPlaybackButton, &playbackToggleButton })
    {
        btn->getProperties().set ("gasInverted", true);
    }

    presetLabel.setText ("Preset", juce::dontSendNotification);
    presetLabel.setJustificationType (juce::Justification::centredLeft);
    content.addAndMakeVisible (presetLabel);

    presetComboBox.onChange = [this]
    {
        const auto selectedId = presetComboBox.getSelectedId();

        if (selectedId == savePresetMenuItemId)
        {
            promptToSaveUserPreset();
            return;
        }

        const auto presetIndex = selectedId - presetMenuItemBaseId;

        if (presetIndex >= 0 && audioProcessor.loadPreset (presetIndex))
            currentPresetSelection = presetComboBox.getText();
    };
    content.addAndMakeVisible (presetComboBox);
    refreshPresetOptions();

    showUnavailableTankControlsButton.setButtonText ("BYOIRs (Bring your own impulse responses)");
    showUnavailableTankControlsButton.onClick = [this]
    {
        targetEditorHeight = showUnavailableTankControlsButton.getToggleState() ? baseExpandedHeight : baseCollapsedHeight;
        refreshOptionControls();
        startTimerHz (30);
    };
    content.addAndMakeVisible (showUnavailableTankControlsButton);
    showUnavailableTankControlsAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (
        audioProcessor.parameters, TheGreatAmericanSpringAudioProcessor::showUnavailableTankControlsParameterID, showUnavailableTankControlsButton);

    animatedEditorHeight = audioProcessor.shouldShowUnavailableTankControls() ? baseExpandedHeight : baseCollapsedHeight;
    targetEditorHeight = animatedEditorHeight;

    // The whole UI lives inside `content`, which gets the scale transform.
    // It must not eat mouse clicks meant for its children or the background.
    content.setInterceptsMouseClicks (false, true);
    addAndMakeVisible (content);

    // Drag-to-resize corner, aspect locked so the artwork never distorts.
    setResizable (true, true);
    setConstrainer (&sizeConstrainer);

    editorScale = readStoredEditorScale();
    updateSizeLimits();
    applyEditorScale (editorScale);

    refreshTankLabels();
    refreshPlaybackLabel();
    refreshOptionControls();
    refreshPullStates();
    refreshChainReadout();
    applyTheme (Theme::solar);
    refreshX2VisualState();
    startTimerHz (30);
}

void TheGreatAmericanSpringAudioProcessorEditor::configurePullKnob (PullKnobSlider& slider, const juce::String& parameterID)
{
    slider.getProperties().set ("pulled", false);
    slider.onPullToggle = [this, &slider, parameterID]
    {
        const auto engaged = audioProcessor.parameters.getRawParameterValue (parameterID)->load() >= 0.5f;
        audioProcessor.setParameterPlainValue (parameterID, engaged ? 0.0f : 1.0f);
        slider.setPulled (! engaged);
        refreshPullStates();
        refreshChainReadout();
    };
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshPullStates()
{
    const auto tube = audioProcessor.isInputTubeEngaged();
    const auto dirt = audioProcessor.isDirtEngaged();
    const auto tape = audioProcessor.isOutputTapeEngaged();

    inputLevelSlider.setPulled (tube);
    gainSlider.setPulled (dirt);
    outputLevelSlider.setPulled (tape);

    inputLevelLabel.setText (tube ? "In: TUBE" : "In: Solid State", juce::dontSendNotification);
    gainLabel.setText (dirt ? "Gain: DIRT" : "Gain: Clean", juce::dontSendNotification);

    // The Out knob drives BOTH output circuits, and the tube there follows the In pull
    // rather than a switch of its own. The label only looked at Tape, so with Tube on
    // and Tape off it read "Out: Solid State" while the J201 was in fact in circuit.
    outputLevelLabel.setText (tube && tape ? "Out: TUBE & TAPE"
                            : tube         ? "Out: TUBE"
                            : tape         ? "Out: TAPE"
                                           : "Out: Solid State",
                              juce::dontSendNotification);

    tubeOffButton.setToggleState (! tube, juce::dontSendNotification);
    tubeOnButton.setToggleState  (tube,   juce::dontSendNotification);
    dirtOffButton.setToggleState (! dirt, juce::dontSendNotification);
    dirtOnButton.setToggleState  (dirt,   juce::dontSendNotification);
    tapeOffButton.setToggleState (! tape, juce::dontSendNotification);
    tapeOnButton.setToggleState  (tape,   juce::dontSendNotification);
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshChainReadout()
{
    chainDescriptionDisplay.setRows (audioProcessor.getSignalChainLines());
}

TheGreatAmericanSpringAudioProcessorEditor::~TheGreatAmericanSpringAudioProcessorEditor()
{
    // Drop the constrainer before it is destroyed, so the resizable corner
    // cannot reach a dangling pointer during teardown.
    setConstrainer (nullptr);
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

    // Art Nouveau corner flourishes
    {
        const auto accentColour = style.accentA.withAlpha (0.28f);
        graphics.setColour (accentColour);
        const float cx = panel.getX();
        const float cy = panel.getY();
        const float cr = panel.getRight();
        const float cb = panel.getBottom();
        const float fl = 38.0f; // flourish length

        // Top-left
        juce::Path tl;
        tl.startNewSubPath (cx + 22, cy + 8);
        tl.cubicTo (cx + 22, cy + fl, cx + 8, cy + fl, cx + 8, cy + 22);
        graphics.strokePath (tl, juce::PathStrokeType (1.6f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // Top-right
        juce::Path tr;
        tr.startNewSubPath (cr - 22, cy + 8);
        tr.cubicTo (cr - 22, cy + fl, cr - 8, cy + fl, cr - 8, cy + 22);
        graphics.strokePath (tr, juce::PathStrokeType (1.6f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // Bottom-left
        juce::Path bl;
        bl.startNewSubPath (cx + 22, cb - 8);
        bl.cubicTo (cx + 22, cb - fl, cx + 8, cb - fl, cx + 8, cb - 22);
        graphics.strokePath (bl, juce::PathStrokeType (1.6f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // Bottom-right
        juce::Path br;
        br.startNewSubPath (cr - 22, cb - 8);
        br.cubicTo (cr - 22, cb - fl, cr - 8, cb - fl, cr - 8, cb - 22);
        graphics.strokePath (br, juce::PathStrokeType (1.6f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        // Top centre diamond accent
        const float mx = bounds.getCentreX();
        juce::Path diamond;
        diamond.startNewSubPath (mx, cy + 5);
        diamond.lineTo (mx + 6, cy + 11);
        diamond.lineTo (mx, cy + 17);
        diamond.lineTo (mx - 6, cy + 11);
        diamond.closeSubPath();
        graphics.setColour (accentColour.withMultipliedAlpha (0.7f));
        graphics.strokePath (diamond, juce::PathStrokeType (1.2f));
    }
}

void TheGreatAmericanSpringAudioProcessorEditor::resized()
{
    if (getWidth() <= 0 || getHeight() <= 0)
        return;

    // The window can be dragged to any size; the UI itself is always laid out
    // at the fixed logical size and then scaled to fill, so no control can ever
    // fall outside the window.
    editorScale = juce::jlimit (minEditorScale, maxEditorScale,
                                (double) getWidth() / (double) baseEditorWidth);
    storeEditorScale (editorScale);

    content.setTransform ({});
    content.setBounds (0, 0, baseEditorWidth, animatedEditorHeight);
    content.setTransform (juce::AffineTransform::scale ((float) editorScale));

    layoutContent();
}

void TheGreatAmericanSpringAudioProcessorEditor::layoutContent()
{
    constexpr int pad        = 8;
    constexpr int halfPad    = pad / 2;
    // All header rows and the Mode/Input rows share this column width so they
    // appear visually centred together rather than spanning the full panel.
    constexpr int contentWidth = 720;
    auto area = content.getLocalBounds().reduced (20);

    const auto centreRow = [] (juce::Rectangle<int> row, int w)
    {
        return row.withWidth (juce::jmin (w, row.getWidth()))
                  .withX (row.getX() + juce::jmax (0, (row.getWidth() - w) / 2));
    };

    // ── Header ────────────────────────────────────────────────────────────────
    auto header = area.removeFromTop (204);

    // Logo: 1.75× size (289×193), pushed 20 px left and 10 px above the top-left corner.
    logoButton.setBounds (juce::Rectangle<int> (-20, -10, 289, 193));

    // Title band – centred in the shared content column.
    // Band is 80 px so the 0.50 font-scale factor gives ~30 px text, letting
    // "The Great American Spring reverb" occupy roughly the same visual width
    // as the shorter name did at the original larger size.
    titleComponent.setBounds (centreRow (header.removeFromTop (80), contentWidth));
    subtitleLabel.setBounds ({});

    header.removeFromTop (halfPad);

    // Art row (theme selector) – cluster centred within the content column.
    {
        auto artRow = centreRow (header.removeFromTop (30), contentWidth);
        const int artW = 28 + 6 + 80 + 80 + 90;   // = 284
        auto r = centreRow (artRow, artW);
        themeLabel.setBounds (r.removeFromLeft (28));
        r.removeFromLeft (6);
        solarThemeButton.setBounds (r.removeFromLeft (80));
        petalThemeButton.setBounds  (r.removeFromLeft (80));
        cosmicThemeButton.setBounds (r.removeFromLeft (90));
    }

    header.removeFromTop (halfPad);

    // "BYOIRs" toggle – centred within content column.
    // Our LookAndFeel draws a 38 px switch to the LEFT of the text, so the text
    // centre sits 19 px right of the button-bounds centre.  Shift the whole button
    // 19 px left so the TEXT (the dominant visual) lands at the column centre.
    {
        auto optRow = centreRow (header.removeFromTop (26), contentWidth);
        // 420 rather than 340: the BYOIRs wording is longer than the old label.
        auto optBounds = centreRow (optRow, 420);
        // -19 accounts for the 38 px switch on the left (centres the text),
        // then +25+30 = +55 total shift right as requested.
        showUnavailableTankControlsButton.setBounds (optBounds.withX (optBounds.getX() + 36));
    }

    header.removeFromTop (halfPad);

    // Oversampling, centred in the space under the BYOIRs toggle. Always visible: it
    // applies whether or not the BYOIRs controls are showing.
    {
        auto osRow = centreRow (header.removeFromTop (26), contentWidth);
        auto os = centreRow (osRow, 200);
        railOversamplingLabel.setBounds (os.removeFromLeft (104));
        os.removeFromLeft (pad);
        railOversamplingComboBox.setBounds (os.removeFromLeft (88));
    }

    area.removeFromTop (pad);

    // ── Preset row ────────────────────────────────────────────────────────────
    {
        constexpr int rowW = 50 + 8 + 200 + 24 + 56 + 76 + 112 + 100;   // = 626
        auto row = centreRow (area.removeFromTop (26), rowW);
        presetLabel.setBounds (row.removeFromLeft (50));
        row.removeFromLeft (8);
        presetComboBox.setBounds (row.removeFromLeft (200));
        row.removeFromLeft (24);
        stereoModeLabel.setBounds (row.removeFromLeft (56));
        stereoButton.setBounds (row.removeFromLeft (76));
        monoToStereoButton.setBounds (row.removeFromLeft (112));
        megaverbButton.setBounds (row.removeFromLeft (100));
    }

    area.removeFromTop (pad);

    // ── Controls row: Ext Tanks | FB Phase | FB Dyn (Comp / Off / Limit) ────
    {
        constexpr int routingLabelW = 72;
        constexpr int routingComboW = 104;
        constexpr int groupGap      = 22;
        constexpr int phaseLabelW   = 70;
        constexpr int phaseButtonW  = 82;
        constexpr int dynLabelW     = 58;
        constexpr int dynButtonW    = 70;
        constexpr int controlsRowW  = routingLabelW + routingComboW + groupGap
                                    + phaseLabelW + phaseButtonW * 2 + groupGap
                                    + dynLabelW + dynButtonW * 3;   // = 704

        auto row = centreRow (area.removeFromTop (28), controlsRowW);

        ir2RoutingLabel.setBounds (row.removeFromLeft (routingLabelW));
        ir2RoutingComboBox.setBounds (row.removeFromLeft (routingComboW));
        row.removeFromLeft (groupGap);

        feedbackPhaseLabel.setBounds (row.removeFromLeft (phaseLabelW));
        feedbackPhaseNormalButton.setBounds (row.removeFromLeft (phaseButtonW));
        feedbackPhaseInvertButton.setBounds (row.removeFromLeft (phaseButtonW));
        row.removeFromLeft (groupGap);

        dynamicsLabel.setBounds (row.removeFromLeft (dynLabelW));
        dynamicsCompButton.setBounds (row.removeFromLeft (dynButtonW));
        dynamicsOffButton.setBounds (row.removeFromLeft (dynButtonW));
        dynamicsLimitButton.setBounds (row.removeFromLeft (dynButtonW));
    }

    area.removeFromTop (pad);

    // ── Rev C switch row: Tube | Dirt | Tape ─────────────────────────────────
    // These three were push-pulls on the Vol / Gain / Output knobs until Rev C moved them onto
    // their own mini toggles in the control deck's switch row. Two positions each, like the panel.
    {
        constexpr int swLabelW   = 44;
        constexpr int swButtonW  = 54;
        constexpr int swGroupGap = 22;
        constexpr int switchRowW = 3 * (swLabelW + swButtonW * 2) + swGroupGap * 2;   // = 500

        auto row = centreRow (area.removeFromTop (28), switchRowW);

        tubeSwitchLabel.setBounds (row.removeFromLeft (swLabelW));
        tubeOffButton.setBounds (row.removeFromLeft (swButtonW));
        tubeOnButton.setBounds (row.removeFromLeft (swButtonW));
        row.removeFromLeft (swGroupGap);

        dirtSwitchLabel.setBounds (row.removeFromLeft (swLabelW));
        dirtOffButton.setBounds (row.removeFromLeft (swButtonW));
        dirtOnButton.setBounds (row.removeFromLeft (swButtonW));
        row.removeFromLeft (swGroupGap);

        tapeSwitchLabel.setBounds (row.removeFromLeft (swLabelW));
        tapeOffButton.setBounds (row.removeFromLeft (swButtonW));
        tapeOnButton.setBounds (row.removeFromLeft (swButtonW));
    }

    area.removeFromTop (6);

    // ── The three level meters, Left over Right at each point ────────────────
    {
        constexpr int meterLabelW   = 30;   // "In" / "Wet" / "Out", spans both bars
        constexpr int chanLabelW    = 12;   // the "L" / "R" tag
        constexpr int meterW        = 120;
        constexpr int meterGroupW   = meterLabelW + chanLabelW + meterW;
        constexpr int rowW = meterGroupW * 3 + 20;

        auto block = centreRow (area.removeFromTop (34), rowW);

        const auto layoutMeterPair = [&] (juce::Rectangle<int> b, juce::Label& groupLabel,
                                          juce::Label& labelL, LevelMeter& meterL,
                                          juce::Label& labelR, LevelMeter& meterR)
        {
            // The group name sits centred against both bars.
            groupLabel.setBounds (b.removeFromLeft (meterLabelW));

            auto top = b.removeFromTop (b.getHeight() / 2);
            labelL.setBounds (top.removeFromLeft (chanLabelW));
            meterL.setBounds (top.reduced (2, 2));

            labelR.setBounds (b.removeFromLeft (chanLabelW));
            meterR.setBounds (b.reduced (2, 2));
        };

        layoutMeterPair (block.removeFromLeft (meterGroupW), inputMeterLabel,
                         inputMeterLabelL, inputMeterL, inputMeterLabelR, inputMeterR);
        block.removeFromLeft (10);
        layoutMeterPair (block.removeFromLeft (meterGroupW), wetMeterLabel,
                         wetMeterLabelL, wetMeterL, wetMeterLabelR, wetMeterR);
        block.removeFromLeft (10);
        layoutMeterPair (block.removeFromLeft (meterGroupW), outputMeterLabel,
                         outputMeterLabelL, outputMeterL, outputMeterLabelR, outputMeterR);
    }

    area.removeFromTop (pad);

    // ── The engaged signal chain, in words ───────────────────────────────────
    // Three rows' worth, reserved whether or not Parallel is showing its second tank
    // row, so switching routing never shifts everything below it.
    chainDescriptionDisplay.setBounds (centreRow (area.removeFromTop (38), 900));

    area.removeFromTop (6);

    // ── Knob rows ────────────────────────────────────────────────────────────
    {
        constexpr int kw = 100;
        constexpr int kg = 20;
        constexpr int kh = 88;

        auto knobs = area.removeFromTop (kh * 2 + 22 * 2 + 4);

        auto layoutKnob = [&] (juce::Rectangle<int> b, juce::Label& lbl, juce::Slider& sl)
        {
            lbl.setBounds (b.removeFromTop (18));
            sl.setBounds  (b.removeFromTop (kh));
        };

        // Rows read left to right in signal order (Rev C): Pre Input, In, Gain, LPF,
        // HPF; then Short/Long mix, Feedback, Wet/Dry, Out, Post Output. Pre Input and
        // Post Output are the plugin-only trims.
        constexpr int kwWide = 124;   // the pull knobs carry longer labels
        auto row1 = centreRow (knobs.removeFromTop (kh + 22), kwWide * 5 + kg * 4);
        knobs.removeFromTop (4);
        auto row2 = centreRow (knobs.removeFromTop (kh + 22), kwWide * 5 + kg * 4);
        juce::ignoreUnused (kw);

        layoutKnob (row1.removeFromLeft (kwWide), preInputLevelLabel,   preInputLevelSlider);   row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kwWide), inputLevelLabel,      inputLevelSlider);      row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kwWide), gainLabel,            gainSlider);            row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kwWide), postLpfCutoffLabel,   postLpfCutoffSlider);   row1.removeFromLeft (kg);
        layoutKnob (row1.removeFromLeft (kwWide), preHpfCutoffLabel,    preHpfCutoffSlider);

        layoutKnob (row2.removeFromLeft (kwWide), extTankMixLabel,      extTankMixSlider);      row2.removeFromLeft (kg);
        layoutKnob (row2.removeFromLeft (kwWide), feedbackAmountLabel,  feedbackAmountSlider);  row2.removeFromLeft (kg);
        layoutKnob (row2.removeFromLeft (kwWide), wetDryLabel,          wetDrySlider);          row2.removeFromLeft (kg);
        layoutKnob (row2.removeFromLeft (kwWide), outputLevelLabel,     outputLevelSlider);     row2.removeFromLeft (kg);
        layoutKnob (row2.removeFromLeft (kwWide), postOutputLevelLabel, postOutputLevelSlider);
    }

    area.removeFromTop (pad);

    // ── Tank groups (expandable) ───────────────────────────────────────────────
    {
        const bool show = showUnavailableTankControlsButton.getToggleState();
        auto ta = centreRow (area.removeFromTop (show ? 204 : 0), 880);
        auto top = ta.removeFromTop (98);
        ta.removeFromTop (pad);
        auto bot = ta.removeFromTop (98);

        auto la  = top.removeFromLeft ((top.getWidth() - 16) / 2);  top.removeFromLeft (16);
        auto ra  = top;
        auto la2 = bot.removeFromLeft ((bot.getWidth() - 16) / 2);  bot.removeFromLeft (16);
        auto ra2 = bot;

        const auto layoutGroup = [] (juce::Rectangle<int> g,
                                     juce::GroupComponent& grp,
                                     juce::Label& lbl,
                                     juce::TextButton& btn)
        {
            grp.setBounds (g);
            auto inner = g.reduced (14, 10);
            // Clear the group's caption row so the filename label isn't crowded.
            inner.removeFromTop (22);
            lbl.setBounds (inner.removeFromTop (20));
            inner.removeFromTop (8);
            btn.setBounds (inner.removeFromTop (26));
        };

        layoutGroup (la,  leftTankGroup,   leftTankLabel,   leftTankLoadButton);
        layoutGroup (ra,  rightTankGroup,  rightTankLabel,  rightTankLoadButton);
        layoutGroup (la2, leftTank2Group,  leftTank2Label,  leftTank2LoadButton);
        layoutGroup (ra2, rightTank2Group, rightTank2Label, rightTank2LoadButton);
    }

    area.removeFromTop (pad);

    // ── Playback ────────────────────────────────────────────────────────────
    // Label and controls share contentWidth so they centre-align with everything above.
    // Combo width is 514 so total fits exactly: 514+8+110+8+80 = 720.
    playbackLabel.setBounds (centreRow (area.removeFromTop (17), contentWidth));
    area.removeFromTop (halfPad);

    {
        auto pb = centreRow (area.removeFromTop (26), contentWidth);
        playbackSourceComboBox.setBounds (pb.removeFromLeft (514));
        pb.removeFromLeft (pad);
        loadPlaybackButton.setBounds     (pb.removeFromLeft (110));
        pb.removeFromLeft (pad);
        playbackToggleButton.setBounds   (pb.removeFromLeft (80));
    }
}
void TheGreatAmericanSpringAudioProcessorEditor::configureRotarySlider (juce::Slider& slider,
                                                                          juce::Label& label,
                                                                          const juce::String& labelText,
                                                                          const juce::String& suffix)
{
    label.setText (labelText, juce::dontSendNotification);
    label.setJustificationType (juce::Justification::centred);
    content.addAndMakeVisible (label);

    slider.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle (juce::Slider::TextBoxBelow, false, 84, 20);
    slider.setTextValueSuffix (suffix);
    content.addAndMakeVisible (slider);
}

void TheGreatAmericanSpringAudioProcessorEditor::refreshPresetOptions()
{
    const auto presetNames = audioProcessor.getPresetNames();
    presetComboBox.clear (juce::dontSendNotification);

    for (int index = 0; index < presetNames.size(); ++index)
        presetComboBox.addItem (presetNames[index], presetMenuItemBaseId + index);

    if (presetNames.size() > 2)
        presetComboBox.addSeparator();

    presetComboBox.addItem ("Save Current Preset...", savePresetMenuItemId);

    const auto selectedIndex = presetNames.indexOf (currentPresetSelection);

    if (selectedIndex >= 0)
        presetComboBox.setSelectedId (presetMenuItemBaseId + selectedIndex, juce::dontSendNotification);
    else if (presetNames.isEmpty())
        presetComboBox.setText (currentPresetSelection, juce::dontSendNotification);
    else
        presetComboBox.setSelectedId (presetMenuItemBaseId, juce::dontSendNotification);
}

void TheGreatAmericanSpringAudioProcessorEditor::promptToSaveUserPreset()
{
    auto safeThis = juce::Component::SafePointer<TheGreatAmericanSpringAudioProcessorEditor> (this);
    auto* savePresetWindow = new juce::AlertWindow ("Save Preset",
                                                    "Save the current settings as a user preset.",
                                                    juce::MessageBoxIconType::NoIcon,
                                                    this);
    savePresetWindow->addTextEditor ("presetName", currentPresetSelection, "Preset name");
    savePresetWindow->addButton ("Save", 1, juce::KeyPress (juce::KeyPress::returnKey));
    savePresetWindow->addButton ("Cancel", 0, juce::KeyPress (juce::KeyPress::escapeKey));
    savePresetWindow->enterModalState (true,
                                       juce::ModalCallbackFunction::create (
                                           [safeThis, savePresetWindow] (int result)
                                           {
                                               std::unique_ptr<juce::AlertWindow> cleanup (savePresetWindow);

                                               if (safeThis == nullptr)
                                                   return;

                                               if (result == 1)
                                               {
                                                   const auto presetName = savePresetWindow->getTextEditorContents ("presetName").trim();

                                                   if (safeThis->audioProcessor.saveUserPreset (presetName))
                                                   {
                                                       safeThis->currentPresetSelection = presetName.retainCharacters (
                                                           "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-()").trim();
                                                   }
                                               }

                                               safeThis->refreshPresetOptions();
                                           }),
                                       true);
}

void TheGreatAmericanSpringAudioProcessorEditor::applyTheme (Theme newTheme)
{
    currentTheme = newTheme;
    auto* themedLookAndFeel = dynamic_cast<ArtDirectedLookAndFeel*> (lookAndFeel.get());
    jassert (themedLookAndFeel != nullptr);

    if (themedLookAndFeel != nullptr)
        themedLookAndFeel->setTheme (currentTheme);

    const auto style = getThemeStyle (currentTheme);

    titleComponent.setStyle (style.textPrimary, style.accentA, pickArtNouveauTypeface());
    subtitleLabel.setFont (makeFont (12.0f, juce::Font::plain, style.bodyTypeface));
    for (auto* label : { &ir2RoutingLabel, &feedbackPhaseLabel, &dynamicsLabel, &stereoModeLabel, &themeLabel,
                         &tubeSwitchLabel, &dirtSwitchLabel, &tapeSwitchLabel })
    {
        label->setFont (makeFont (12.5f, juce::Font::bold, style.bodyTypeface));
        label->setColour (juce::Label::textColourId, style.textPrimary);
    }
    subtitleLabel.setColour (juce::Label::textColourId, style.textSecondary);

    const auto styleComboBox = [&style] (juce::ComboBox& comboBox)
    {
        comboBox.setColour (juce::ComboBox::textColourId, style.textPrimary);
        comboBox.setColour (juce::ComboBox::backgroundColourId, juce::Colours::transparentBlack);
        comboBox.setColour (juce::ComboBox::outlineColourId, juce::Colours::transparentBlack);
        comboBox.setColour (juce::ComboBox::arrowColourId, style.textPrimary);
    };

    styleComboBox (ir2RoutingComboBox);
    styleComboBox (playbackSourceComboBox);
    styleComboBox (presetComboBox);
    styleComboBox (railOversamplingComboBox);

    const auto styleControlLabel = [&style] (juce::Label& label)
    {
        label.setFont (makeFont (12.0f, juce::Font::bold, style.bodyTypeface));
        label.setColour (juce::Label::textColourId, style.textPrimary);
    };

    for (auto* label : { &gainLabel, &preHpfCutoffLabel, &postLpfCutoffLabel,
                         &extTankMixLabel, &feedbackAmountLabel, &wetDryLabel,
                         &preInputLevelLabel, &inputLevelLabel, &outputLevelLabel, &postOutputLevelLabel,
                         &inputMeterLabel, &wetMeterLabel, &outputMeterLabel, &railOversamplingLabel,
                         &inputMeterLabelL, &inputMeterLabelR,
                         &wetMeterLabelL, &wetMeterLabelR,
                         &outputMeterLabelL, &outputMeterLabelR,
                         &leftTankLabel, &rightTankLabel, &leftTank2Label, &rightTank2Label, &playbackLabel })
    {
        styleControlLabel (*label);
    }

    presetLabel.setFont (makeFont (12.5f, juce::Font::bold, style.bodyTypeface));
    presetLabel.setColour (juce::Label::textColourId, style.textPrimary);

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

    // Its face is fixed monospace so the columns keep lining up; only the colour
    // follows the theme.
    chainDescriptionDisplay.setTextColour (style.textSecondary);

    // Plugin-only knobs are labelled in the secondary colour so they read as
    // "not on the board" at a glance.
    preInputLevelLabel.setColour (juce::Label::textColourId, style.textSecondary);
    postOutputLevelLabel.setColour (juce::Label::textColourId, style.textSecondary);

    for (auto* slider : std::initializer_list<juce::Slider*> { &gainSlider, &preHpfCutoffSlider, &postLpfCutoffSlider,
                                                               &extTankMixSlider, &feedbackAmountSlider, &wetDrySlider,
                                                               &preInputLevelSlider, &inputLevelSlider, &outputLevelSlider, &postOutputLevelSlider })
    {
        styleSlider (*slider);
    }

    for (auto* meter : { &inputMeterL, &inputMeterR, &wetMeterL, &wetMeterR,
                         &outputMeterL, &outputMeterR })
    {
        meter->setTrackColours (style.panelBottom.withAlpha (0.85f),
                                style.knobStart,
                                style.buttonOutline.withAlpha (0.85f),
                                style.textPrimary);
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

    using Dynamics = TheGreatAmericanSpringAudioProcessor::Dynamics;
    const auto dynamics = audioProcessor.getDynamics();
    dynamicsCompButton.setToggleState (dynamics == Dynamics::comp, juce::dontSendNotification);
    dynamicsOffButton.setToggleState (dynamics == Dynamics::off, juce::dontSendNotification);
    dynamicsLimitButton.setToggleState (dynamics == Dynamics::limit, juce::dontSendNotification);

    using StereoMode = TheGreatAmericanSpringAudioProcessor::StereoMode;
    const auto stereoMode = audioProcessor.getStereoMode();
    stereoButton.setToggleState (stereoMode == StereoMode::stereo, juce::dontSendNotification);
    monoToStereoButton.setToggleState (stereoMode == StereoMode::monoToStereo, juce::dontSendNotification);
    megaverbButton.setToggleState (stereoMode == StereoMode::megaverb, juce::dontSendNotification);

    const auto showTankControls = showUnavailableTankControlsButton.getToggleState();

    juce::Component* tankControls[] = { &leftTankGroup, &rightTankGroup, &leftTank2Group, &rightTank2Group,
                                        &leftTankLabel, &rightTankLabel, &leftTank2Label, &rightTank2Label,
                                        &leftTankLoadButton, &rightTankLoadButton, &leftTank2LoadButton, &rightTank2LoadButton };

    for (auto* component : tankControls)
    {
        component->setVisible (showTankControls);
    }

    targetEditorHeight = showTankControls ? baseExpandedHeight : baseCollapsedHeight;
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

    // Height changed, so the locked aspect ratio and the size limits move with
    // it. The user's chosen scale is preserved throughout.
    updateSizeLimits();
    applyEditorScale (editorScale);
}

void TheGreatAmericanSpringAudioProcessorEditor::updateSizeLimits()
{
    sizeConstrainer.setFixedAspectRatio ((double) baseEditorWidth / (double) animatedEditorHeight);
    sizeConstrainer.setSizeLimits (juce::roundToInt (baseEditorWidth * minEditorScale),
                                   juce::roundToInt (animatedEditorHeight * minEditorScale),
                                   juce::roundToInt (baseEditorWidth * maxEditorScale),
                                   juce::roundToInt (animatedEditorHeight * maxEditorScale));
}

void TheGreatAmericanSpringAudioProcessorEditor::applyEditorScale (double newScale)
{
    editorScale = juce::jlimit (minEditorScale, maxEditorScale, newScale);
    setSize (juce::roundToInt (baseEditorWidth * editorScale),
             juce::roundToInt (animatedEditorHeight * editorScale));
}

double TheGreatAmericanSpringAudioProcessorEditor::defaultEditorScaleForDisplay()
{
    // Deliberately a fixed value rather than a screen-derived one.
    //
    // juce::Displays reports userArea in this display's own device pixels while
    // the editor is laid out in logical units that Windows then multiplies by
    // the monitor's DPI scale, and display.scale does not reliably reconcile
    // the two on a mixed-DPI, multi-monitor Windows setup. Deriving the default
    // from those numbers produced a window that fit one monitor and overflowed
    // another, which is the exact failure this is meant to avoid.
    //
    // 1.15 is chosen so the FULLY EXPANDED window (tank controls open, 900
    // logical px tall) still fits a 1080p-class monitor at 125% Windows
    // scaling with room for a title bar and taskbar. It is a floor, not a
    // ceiling: the window has a drag-resize corner up to maxEditorScale, and
    // whatever size the user settles on is remembered in the plugin state.
    return 1.15;
}

double TheGreatAmericanSpringAudioProcessorEditor::readStoredEditorScale() const
{
    const auto stored = (double) audioProcessor.parameters.state.getProperty ("editorScale", 0.0);

    if (stored >= minEditorScale && stored <= maxEditorScale)
        return stored;

    return defaultEditorScaleForDisplay();
}

void TheGreatAmericanSpringAudioProcessorEditor::storeEditorScale (double scale) const
{
    audioProcessor.parameters.state.setProperty ("editorScale", scale, nullptr);
}

void TheGreatAmericanSpringAudioProcessorEditor::timerCallback()
{
    // Meters are polled here rather than pushed from the audio thread, so the
    // ballistics cost nothing in processBlock.
    inputMeterL.setLevelDb (audioProcessor.getInputMeterDb (0));
    inputMeterR.setLevelDb (audioProcessor.getInputMeterDb (1));
    wetMeterL.setLevelDb (audioProcessor.getWetMeterDb (0));
    wetMeterR.setLevelDb (audioProcessor.getWetMeterDb (1));
    outputMeterL.setLevelDb (audioProcessor.getOutputMeterDb (0));
    outputMeterR.setLevelDb (audioProcessor.getOutputMeterDb (1));

    // Pull states and the chain readout follow the parameters, so host
    // automation and presets move the knobs in and out too.
    refreshPullStates();
    refreshChainReadout();

    introElapsedMs += 33;

    // Wait 3 s before the first flip, then hold each artwork for 2 s.
    if (introThemeStep == 0 && introElapsedMs >= 3000)
    {
        introThemeStep = 1;
        applyTheme (Theme::petal);
    }

    if (introThemeStep == 1 && introElapsedMs >= 5000)
    {
        introThemeStep = 2;
        applyTheme (Theme::cosmic);
    }

    if (introThemeStep == 2 && introElapsedMs >= 7000)
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

    // The blend knob does a different job in each routing, so its name, its reading and
    // whether it does anything at all follow the Ext Reverb Tanks selector.
    //
    //   Off       nothing to blend, so the knob reads N/A and is greyed out
    //   Series    "+ %Long Tank", 0% to 100% of long tank added in
    //   Parallel  "Short / Long Tank Mix", reading "x% Short / 100-x% Long"
    //
    // The slider's own textFromValueFunction is set here rather than the parameter's,
    // because the slider's wins for what is drawn on screen. The processor keeps the
    // matching law for the host's automation readout.
    using Routing = TheGreatAmericanSpringAudioProcessor::Ir2RoutingMode;
    const auto routing = audioProcessor.getIr2RoutingMode();

    switch (routing)
    {
        case Routing::series:
            extTankMixLabel.setText ("+ %Long Tank", juce::dontSendNotification);
            extTankMixSlider.textFromValueFunction = [] (double value)
            {
                return juce::String (juce::roundToInt (juce::jlimit (0.0, 1.0, value) * 100.0)) + "%";
            };
            extTankMixSlider.setTooltip ("How much of the long (Ext) tank gets added in. 0% is the short (Main) tank "
                                         "and the Gain / Dirt / Comp block on their own, 100% is all of it through the "
                                         "long tank, and it is a straight line across the whole sweep.");
            break;

        case Routing::parallel:
            extTankMixLabel.setText ("Short / Long Tank Mix", juce::dontSendNotification);
            extTankMixSlider.textFromValueFunction = [] (double value)
            {
                const auto longPercent = juce::roundToInt (juce::jlimit (0.0, 1.0, value) * 100.0);
                return juce::String (100 - longPercent) + "% Short / " + juce::String (longPercent) + "% Long";
            };
            extTankMixSlider.setTooltip ("Crossfade between the two tank pairs running side by side. Hard left is the "
                                         "short (Main) tanks alone, noon is half and half, hard right is the long (Ext) "
                                         "tanks alone. The two always add up to 100%.");
            break;

        case Routing::off:
        default:
            extTankMixLabel.setText ("N/A", juce::dontSendNotification);
            extTankMixSlider.textFromValueFunction = [] (double) { return juce::String ("N/A"); };
            extTankMixSlider.setTooltip ("Nothing to blend with the Ext Reverb Tanks set to Off. Pick Series or Parallel "
                                         "to bring this knob in.");
            break;
    }

    const auto blendActive = routing != Routing::off;
    extTankMixLabel.setColour (juce::Label::textColourId,
                               blendActive ? style.textPrimary : style.textSecondary.withMultipliedAlpha (0.55f));
    extTankMixSlider.setEnabled (blendActive);
    extTankMixSlider.setAlpha (blendActive ? 1.0f : 0.45f);
    extTankMixSlider.updateText();
    extTankMixSlider.repaint();
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
        refreshPresetOptions();
        refreshX2VisualState();
        refreshPlaybackLabel();
    }
}
