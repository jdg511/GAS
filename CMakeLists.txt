cmake_minimum_required(VERSION 3.22)

project(TheGreatAmericanSpring VERSION 3.0.0)

include(FetchContent)

set(JUCE_SOURCE_DIR "C:/Users/Jason/.juce/JUCE" CACHE PATH "Path to a local JUCE checkout. If missing, JUCE is fetched automatically.")
set(GAS_JUCE_GIT_TAG "8.0.12" CACHE STRING "JUCE git tag to fetch when JUCE_SOURCE_DIR is unavailable.")

if (EXISTS "${JUCE_SOURCE_DIR}/CMakeLists.txt")
    add_subdirectory("${JUCE_SOURCE_DIR}" JUCE-build)
    set(_gas_juce_src_dir "${JUCE_SOURCE_DIR}")
else()
    message(STATUS "JUCE_SOURCE_DIR was not found; fetching JUCE ${GAS_JUCE_GIT_TAG}.")
    FetchContent_Declare(
        juce
        GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
        GIT_TAG ${GAS_JUCE_GIT_TAG}
        GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(juce)
    set(_gas_juce_src_dir "${juce_SOURCE_DIR}")
endif()

# juce_graphics.cpp exceeds MSVC's default 64k section limit; /bigobj lifts it.
# /Od skips optimisation on that TU, keeping the compile fast.
if (MSVC)
    set_source_files_properties(
        "${_gas_juce_src_dir}/modules/juce_graphics/juce_graphics.cpp"
        "${_gas_juce_src_dir}/modules/juce_graphics/juce_graphics_Harfbuzz.cpp"
        PROPERTIES
            COMPILE_OPTIONS "/Od;/bigobj")
endif()

set(SCC_ASSET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/Assets")
set(SCC_BASE_PLUGIN_FORMATS Standalone VST3 LV2 CACHE STRING "JUCE plugin formats to request. Platform-incompatible formats are ignored by JUCE.")
set(SCC_VST2_SDK_PATH "" CACHE PATH "Path to the legacy Steinberg VST2 SDK folder. When set, the JUCE VST format is added.")
set(SCC_AAX_SDK_PATH "" CACHE PATH "Path to the Avid AAX SDK (the folder containing its own CMakeLists.txt, e.g. .../aax-sdk-2-10-0-beta/aax-package). When set, the JUCE AAX format is added.")
set(SCC_DEPLOY_WINDOWS_VST3_AFTER_BUILD ON CACHE BOOL "Copy the Windows VST3 bundle to SCC_VST3_DEPLOY_ROOT after building.")
set(SCC_VST3_DEPLOY_ROOT "C:/Program Files/Common Files/VST3" CACHE PATH "Windows VST3 install root used when SCC_DEPLOY_WINDOWS_VST3_AFTER_BUILD is ON.")
set(SPRING_IR_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/Spring IRs")

set(SCC_PLUGIN_FORMATS ${SCC_BASE_PLUGIN_FORMATS})

if (SCC_VST2_SDK_PATH)
    juce_set_vst2_sdk_path("${SCC_VST2_SDK_PATH}")
    list(APPEND SCC_PLUGIN_FORMATS VST)
else()
    list(REMOVE_ITEM SCC_PLUGIN_FORMATS VST)
    message(STATUS "VST2 disabled. Configure with -DSCC_VST2_SDK_PATH=/path/to/VST2_SDK to add the legacy VST target.")
endif()

if (SCC_AAX_SDK_PATH)
    juce_set_aax_sdk_path("${SCC_AAX_SDK_PATH}")
    list(APPEND SCC_PLUGIN_FORMATS AAX)
else()
    list(REMOVE_ITEM SCC_PLUGIN_FORMATS AAX)
    message(STATUS "AAX disabled. Configure with -DSCC_AAX_SDK_PATH=/path/to/aax-package to add the AAX target. Note: the resulting binary still needs PACE/iLok wraptool signing before Pro Tools will load it.")
endif()

list(REMOVE_DUPLICATES SCC_PLUGIN_FORMATS)

juce_add_plugin(TheGreatAmericanSpring
    COMPANY_NAME "Illicit Apothecary"
    VERSION "${PROJECT_VERSION}"
    BUNDLE_ID "com.illicitapothecary.gas"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD FALSE
    PLUGIN_MANUFACTURER_CODE IlAp
    PLUGIN_CODE Gas1
    FORMATS ${SCC_PLUGIN_FORMATS}
    LV2URI "urn:illicitapothecary:plugins:great-american-spring"
    VST3_CATEGORIES Fx Reverb Stereo
    AAX_CATEGORY Reverb Effect
    PRODUCT_NAME "The Great American Spring reverb Rev C")

juce_generate_juce_header(TheGreatAmericanSpring)

juce_add_binary_data(TheGreatAmericanSpringAssets
    SOURCES
        "${SCC_ASSET_DIR}/Images/background_session_03.png"
        "${SCC_ASSET_DIR}/Images/background_session_08.png"
        "${SCC_ASSET_DIR}/Images/background_session_09.png"
        "${SCC_ASSET_DIR}/Logos/illicit_apothecary_logo.svg"
        "${SCC_ASSET_DIR}/Playback/Make Reverb Great Again-mono.mp3"
        "${SCC_ASSET_DIR}/Playback/Its a Shame-stereo.mp3"
        "${SCC_ASSET_DIR}/Playback/Zombie Remix-stereo.mp3"
        # NAM rig demo clips (added 2026-09-12)
        "${SCC_ASSET_DIR}/Playback/arpeggio-deluxe-clean.mp3"
        "${SCC_ASSET_DIR}/Playback/arpeggio-dirty-punk.mp3"
        "${SCC_ASSET_DIR}/Playback/arpeggio-iconic-cleanish.mp3"
        "${SCC_ASSET_DIR}/Playback/arpeggio-quick-clean.mp3"
        "${SCC_ASSET_DIR}/Playback/arpeggio-warm-crunch.mp3"
        "${SCC_ASSET_DIR}/Playback/finger-bass-bite.mp3"
        "${SCC_ASSET_DIR}/Playback/finger-bass-clean-bright.mp3"
        "${SCC_ASSET_DIR}/Playback/finger-bass-growl.mp3"
        "${SCC_ASSET_DIR}/Playback/finger-bass-nice-warm.mp3"
        "${SCC_ASSET_DIR}/Playback/metal-5150.mp3"
        "${SCC_ASSET_DIR}/Playback/metal-blackstar.mp3"
        "${SCC_ASSET_DIR}/Playback/metal-dualrec.mp3"
        "${SCC_ASSET_DIR}/Playback/pick-bass-bite.mp3"
        "${SCC_ASSET_DIR}/Playback/pick-bass-clean-bright.mp3"
        "${SCC_ASSET_DIR}/Playback/pick-bass-growl.mp3"
        "${SCC_ASSET_DIR}/Playback/pick-bass-metalcore.mp3"
        "${SCC_ASSET_DIR}/Playback/pick-bass-rock-classic.mp3"
        "${SCC_ASSET_DIR}/Playback/power-chords-classic-hi-gain.mp3"
        "${SCC_ASSET_DIR}/Playback/power-chords-iconic-cleanish.mp3"
        "${SCC_ASSET_DIR}/Playback/power-chords-plexi.mp3"
        "${SCC_ASSET_DIR}/Playback/power-chords-punk-rock-rhythm.mp3"
        "${SCC_ASSET_DIR}/Playback/rhythm-chords-ac30-crunch.mp3"
        "${SCC_ASSET_DIR}/Playback/rhythm-chords-fender-clean.mp3"
        "${SCC_ASSET_DIR}/Playback/rhythm-chords-suhr-clean.mp3"
        "${SCC_ASSET_DIR}/Playback/solo-diezel.mp3"
        "${SCC_ASSET_DIR}/Playback/solo-fortin.mp3"
        "${SCC_ASSET_DIR}/Playback/solo-mesa.mp3")

target_sources(TheGreatAmericanSpring
    PRIVATE
        Source/PluginEditor.cpp
        Source/PluginEditor.h
        Source/PluginProcessor.cpp
        Source/PluginProcessor.h
        Source/DSP/ClipperCircuitModels.h
        Source/DSP/DynamicsModels.h
        Source/DSP/FeedbackBlock.h
        Source/DSP/ModularFxChain.h
        Source/DSP/RevCStages.h
        Source/DSP/SaturationModels.h
        Source/DSP/TankIRBlock.h
        Source/DSP/WetDryMixerBlock.h)

target_compile_definitions(TheGreatAmericanSpring
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0)

target_link_libraries(TheGreatAmericanSpring
    PRIVATE
        TheGreatAmericanSpringAssets
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags)

function(scc_copy_spring_irs_after_build target_name)
    if (TARGET ${target_name})
        add_custom_command(TARGET ${target_name} POST_BUILD
            COMMAND "${CMAKE_COMMAND}"
                -DSOURCE_PLUGIN_BINARY=$<TARGET_FILE:${target_name}>
                -DSOURCE_IR_DIR=${SPRING_IR_SOURCE_DIR}
                -P "${CMAKE_CURRENT_SOURCE_DIR}/cmake/CopySpringIRsToPlugin.cmake"
            VERBATIM)
    endif()
endfunction()

foreach(format_name IN ITEMS Standalone VST VST3 LV2 AAX)
    scc_copy_spring_irs_after_build(TheGreatAmericanSpring_${format_name})
endforeach()

if (WIN32 AND SCC_DEPLOY_WINDOWS_VST3_AFTER_BUILD AND TARGET TheGreatAmericanSpring_VST3)
    add_custom_command(TARGET TheGreatAmericanSpring_VST3 POST_BUILD
        COMMAND "${CMAKE_COMMAND}"
            -DSOURCE_VST3_BINARY=$<TARGET_FILE:TheGreatAmericanSpring_VST3>
            -DSOURCE_IR_DIR=${SPRING_IR_SOURCE_DIR}
            -DDESTINATION_VST3_ROOT=${SCC_VST3_DEPLOY_ROOT}
            -P "${CMAKE_CURRENT_SOURCE_DIR}/cmake/CopyVST3Bundle.cmake"
        VERBATIM)
endif()
