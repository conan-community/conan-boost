PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

CONAN_BASIC_SETUP()

IF(NOT HEADER_ONLY)
	find_package(Boost COMPONENTS regex)
	
	IF(Boost_FOUND)
	    include_directories(${Boost_INCLUDE_DIRS})
	    ADD_EXECUTABLE(lambda lambda.cpp)
	    ADD_EXECUTABLE(regex_exe regex.cpp)
	    TARGET_LINK_LIBRARIES(regex_exe ${Boost_LIBRARIES})
	ELSE()
	    MESSAGE(FATAL_ERROR "ERROR! BOOST NOT FOUND!")
	ENDIF()
ELSE()
	ADD_EXECUTABLE(lambda lambda.cpp)
ENDIF()
