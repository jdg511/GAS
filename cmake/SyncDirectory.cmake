if (NOT DEFINED SOURCE_DIR)
    message(FATAL_ERROR "SOURCE_DIR is required.")
endif()

if (NOT DEFINED DESTINATION_DIR)
    message(FATAL_ERROR "DESTINATION_DIR is required.")
endif()

if (NOT EXISTS "${SOURCE_DIR}")
    message(FATAL_ERROR "Source directory '${SOURCE_DIR}' does not exist.")
endif()

if (EXISTS "${DESTINATION_DIR}")
    file(REMOVE_RECURSE "${DESTINATION_DIR}")
endif()

get_filename_component(destinationParent "${DESTINATION_DIR}" DIRECTORY)
file(MAKE_DIRECTORY "${destinationParent}")
file(COPY "${SOURCE_DIR}" DESTINATION "${destinationParent}")
