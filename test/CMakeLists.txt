PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(lambda lambda.cpp)
IF(NOT HEADER_ONLY)
	ADD_EXECUTABLE(regex regex.cpp) # Uses autolinkingç
	TARGET_LINK_LIBRARIES(regex ${CONAN_LIBS})
ENDIF()

