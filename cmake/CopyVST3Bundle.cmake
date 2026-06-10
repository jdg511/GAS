if (NOT DEFINED SOURCE_VST3_BINARY)
    message(FATAL_ERROR "SOURCE_VST3_BINARY is required.")
endif()

if (NOT DEFINED DESTINATION_VST3_ROOT)
    message(FATAL_ERROR "DESTINATION_VST3_ROOT is required.")
endif()

if (NOT DEFINED SOURCE_IR_DIR)
    message(FATAL_ERROR "SOURCE_IR_DIR is required.")
endif()

get_filename_component(sourceBinary "${SOURCE_VST3_BINARY}" ABSOLUTE)
get_filename_component(sourceArchDirectory "${sourceBinary}" DIRECTORY)
get_filename_component(sourceContentsDirectory "${sourceArchDirectory}" DIRECTORY)
get_filename_component(sourceBundleDirectory "${sourceContentsDirectory}" DIRECTORY)
get_filename_component(bundleName "${sourceBundleDirectory}" NAME)

if (NOT bundleName MATCHES "\\.vst3$")
    message(FATAL_ERROR "Resolved source bundle '${sourceBundleDirectory}' does not look like a VST3 bundle.")
endif()

set(destinationBundleDirectory "${DESTINATION_VST3_ROOT}/${bundleName}")
set(sourceResourceIrDirectory "${sourceContentsDirectory}/Resources/Spring IRs")
set(sourceLegacyIrDirectory "${sourceArchDirectory}/Spring IRs")
set(sourcePlaybackResourceDirectory "${sourceContentsDirectory}/Resources/Playback Audio")

file(MAKE_DIRECTORY "${DESTINATION_VST3_ROOT}")

if (NOT EXISTS "${SOURCE_IR_DIR}")
    message(FATAL_ERROR "Spring IR source directory '${SOURCE_IR_DIR}' does not exist.")
endif()

if (EXISTS "${sourceResourceIrDirectory}")
    file(REMOVE_RECURSE "${sourceResourceIrDirectory}")
endif()

if (EXISTS "${sourceLegacyIrDirectory}")
    file(REMOVE_RECURSE "${sourceLegacyIrDirectory}")
endif()

if (EXISTS "${sourcePlaybackResourceDirectory}")
    file(REMOVE_RECURSE "${sourcePlaybackResourceDirectory}")
endif()

file(COPY "${SOURCE_IR_DIR}" DESTINATION "${sourceContentsDirectory}/Resources")

if (EXISTS "${destinationBundleDirectory}")
    file(REMOVE_RECURSE "${destinationBundleDirectory}")
endif()

file(COPY "${sourceBundleDirectory}" DESTINATION "${DESTINATION_VST3_ROOT}")
