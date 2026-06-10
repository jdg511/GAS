if (NOT DEFINED SOURCE_PLUGIN_BINARY)
    message(FATAL_ERROR "SOURCE_PLUGIN_BINARY is required.")
endif()

if (NOT DEFINED SOURCE_IR_DIR)
    message(FATAL_ERROR "SOURCE_IR_DIR is required.")
endif()

if (NOT EXISTS "${SOURCE_IR_DIR}")
    message(FATAL_ERROR "Spring IR source directory '${SOURCE_IR_DIR}' does not exist.")
endif()

get_filename_component(sourceBinary "${SOURCE_PLUGIN_BINARY}" ABSOLUTE)
get_filename_component(binaryDirectory "${sourceBinary}" DIRECTORY)
get_filename_component(binaryParentDirectory "${binaryDirectory}" DIRECTORY)
get_filename_component(binaryParentName "${binaryParentDirectory}" NAME)

set(destinationDirectories "${binaryDirectory}/Spring IRs")

if (binaryParentName STREQUAL "Contents")
    list(APPEND destinationDirectories "${binaryParentDirectory}/Resources/Spring IRs")
endif()

list(REMOVE_DUPLICATES destinationDirectories)

foreach(destinationDirectory IN LISTS destinationDirectories)
    if (EXISTS "${destinationDirectory}")
        file(REMOVE_RECURSE "${destinationDirectory}")
    endif()

    get_filename_component(destinationParent "${destinationDirectory}" DIRECTORY)
    file(MAKE_DIRECTORY "${destinationParent}")
    file(COPY "${SOURCE_IR_DIR}" DESTINATION "${destinationParent}")
endforeach()
