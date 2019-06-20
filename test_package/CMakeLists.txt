cmake_minimum_required(VERSION 2.8)

project(conan_boost_test_package)
enable_testing()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
if(CONAN_SETTINGS_OS STREQUAL "Android")
    set(CONAN_LIBCXX "") # NDK fails when specified: https://github.com/android-ndk/ndk/issues/541
endif()

CONAN_BASIC_SETUP()

IF(NOT HEADER_ONLY)

    set(Boost_DEBUG 1)

    if( WITH_PYTHON )
        list( APPEND BOOST_LIBS_TO_SEARCH python )
    endif()
    if( WITH_REGEX )
        list( APPEND BOOST_LIBS_TO_SEARCH regex )
    endif()
    if( WITH_LOCALE )
        list( APPEND BOOST_LIBS_TO_SEARCH locale )
        if( USE_ICU )
            list( APPEND BOOST_LIBS_TO_SEARCH thread )
        endif()
    endif()

    find_package( Boost COMPONENTS ${BOOST_LIBS_TO_SEARCH} REQUIRED )
    include_directories(${Boost_INCLUDE_DIRS})

endif()

function( target_link_to_icu target )

    if( ICU_USE_STATIC_LIBS )

        if(NOT ICU_FOUND)
            set(ICU_DEBUG 1)
            set(ICU_ROOT "${CONAN_ICU_ROOT}")
            find_package(ICU COMPONENTS i18n uc data REQUIRED)
        endif()

        target_include_directories( ${target} PUBLIC ${ICU_INCLUDE_DIRS} )
        target_link_libraries( ${target} PUBLIC ${ICU_LIBRARIES} )

        if(MSVC)
           target_link_libraries( ${target} PUBLIC advapi32 )
        elseif(UNIX AND NOT APPLE )
            target_link_libraries( ${target} PUBLIC dl )
        endif()

    endif()

endfunction()


add_executable(lambda lambda.cpp)
add_test(NAME TestLambda
         COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:lambda>" ${TEST_ARGS})


IF(NOT HEADER_ONLY)

    if( WITH_REGEX )
        add_executable(regex_exe regex.cpp)
        target_link_libraries(regex_exe ${Boost_LIBRARIES})
        add_test(NAME TestRegex
                COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_exe>")
    endif()

    if( WITH_TEST )
        add_executable(test test.cpp)
        target_link_libraries(test ${CONAN_LIBS})
    endif()

    if( WITH_PYTHON )
        add_library(hello_ext SHARED python.cpp)
        if(WIN32)
            set_target_properties(hello_ext PROPERTIES SUFFIX ".pyd")
            target_include_directories(hello_ext PRIVATE C:/Python27/include)
            target_link_libraries(hello_ext C:/Python27/libs/python27.lib ${CONAN_LIBS})
        endif()
    endif()

    if( USE_ICU )
        if( WITH_REGEX )
            add_executable(regex_use_icu regex_use_icu.cpp)
            target_link_libraries(regex_use_icu ${Boost_LIBRARIES} )
            target_link_to_icu( regex_use_icu )
            add_test(NAME TestRegexUseICU
                     COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:regex_use_icu>")
        endif()

        if( WITH_LOCALE )
            add_executable(locale_use_icu locale_use_icu.cpp)
            target_link_libraries(locale_use_icu ${Boost_LIBRARIES} )
            target_link_to_icu( locale_use_icu )
            add_test(NAME TestLocaleUseICU
                     COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:locale_use_icu>")
            if(UNIX)  
                find_package( Iconv REQUIRED )
                if( Iconv_FOUND AND NOT Iconv_IS_BUILT_IN )
                    target_link_libraries( locale_use_icu ${Iconv_LIBRARIES} )
                endif()
            endif()
        endif()
    endif()

    # Test a different exe linking with the CONAN_LIBS to actually test the package_info
    if( WITH_REGEX )
        add_executable(newregex regex.cpp)
        target_link_libraries(newregex ${CONAN_LIBS})
        add_test(NAME TestRegexNew
                 COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:newregex>" ${TEST_ARGS})
    endif()
ENDIF()
