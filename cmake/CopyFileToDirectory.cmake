if (NOT DEFINED SOURCE_FILE)
    message(FATAL_ERROR "SOURCE_FILE is required.")
endif()

if (NOT DEFINED DESTINATION_DIR)
    message(FATAL_ERROR "DESTINATION_DIR is required.")
endif()

if (NOT EXISTS "${SOURCE_FILE}")
    message(FATAL_ERROR "Source file '${SOURCE_FILE}' does not exist.")
endif()

file(MAKE_DIRECTORY "${DESTINATION_DIR}")
file(COPY "${SOURCE_FILE}" DESTINATION "${DESTINATION_DIR}")
