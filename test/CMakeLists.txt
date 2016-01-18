PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)

CONAN_BASIC_SETUP()
find_package(Boost COMPONENTS regex)

IF(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS})
    ADD_EXECUTABLE(lambda lambda.cpp)
    ADD_EXECUTABLE(regex_exe regex.cpp)
    TARGET_LINK_LIBRARIES(regex_exe ${Boost_LIBRARIES})
ELSE()
    MESSAGE(FATAL_ERROR "ERROR! BOOST NOT FOUND!")
ENDIF()
