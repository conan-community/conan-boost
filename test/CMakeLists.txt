PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(lambda lambda.cpp)
IF(NOT HEADER_ONLY)
	ADD_EXECUTABLE(regex_exe regex.cpp) # Uses autolinking
	TARGET_LINK_LIBRARIES(regex_exe ${CONAN_LIBS})
ENDIF()

