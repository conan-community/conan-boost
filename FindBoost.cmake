MESSAGE(STATUS "********* Conan FindBoost wrapper **********")
SET(Boost_DEBUG 0)

MESSAGE("COMPONENTS TO SEARCH: ${Boost_FIND_COMPONENTS}")

SET(BOOST_ROOT ${CONAN_BOOST_ROOT})
SET(BOOST_INCLUDEDIR ${CONAN_INCLUDE_DIRS_BOOST})
SET(Boost_LIBRARY_DIR ${CONAN_LIB_DIRS_BOOST})
SET(BOOST_LIBRARYDIR ${CONAN_LIB_DIRS_BOOST})
SET(Boost_NO_SYSTEM_PATHS ON)
SET(Boost_NO_BOOST_CMAKE ON)

# READ conaninfo and detect HEADER ONLY
FILE(READ ${CONAN_BOOST_ROOT}/conaninfo.txt CONANINFO_FILE) 
IF(WIN32)
    # Appends "g"
    IF(CONANINFO_FILE MATCHES "compiler.runtime=MTd" OR CONANINFO_FILE MATCHES "compiler.runtime=MDd")
        SET(Boost_USE_DEBUG_RUNTIME ON)
    ELSE()
        SET(Boost_USE_DEBUG_RUNTIME OFF)
    ENDIF()
    
    # Appends "s"
    IF(CONANINFO_FILE MATCHES "compiler.runtime=MT" OR CONANINFO_FILE MATCHES "compiler.runtime=MTd")
        SET(Boost_USE_STATIC_RUNTIME ON)
    ELSE()
        SET(Boost_USE_STATIC_RUNTIME OFF)
    ENDIF()
    
    MESSAGE("DEBUG RUNTIME: ${Boost_USE_DEBUG_RUNTIME}")
    MESSAGE("STATIC RUNTIME: ${Boost_USE_STATIC_RUNTIME}")
    
    # The space is important, so it doesn't match the flag for zlib:shared=False
    IF(CONANINFO_FILE MATCHES " shared=False")
        SET(Boost_USE_STATIC_LIBS ON) # Removed in the original file
    ELSE()
        SET(Boost_USE_STATIC_LIBS OFF)
    ENDIF()

ENDIF()

IF(CONANINFO_FILE MATCHES " header_only=True")
    MESSAGE(STATUS "DETECTED Boost HEADER ONLY PACKAGE")
    SET(BOOST_HEADER_ONLY TRUE)
    SET(Boost_FOUND TRUE)
    SET(BOOST_FOUND TRUE)
ENDIF()


IF(NOT BOOST_HEADER_ONLY)
    include("${CONAN_BOOST_ROOT}/OriginalFindBoost.cmake")
ENDIF() # END IF HEADER_ONLY
