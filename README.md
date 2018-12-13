[![Build status](https://ci.appveyor.com/api/projects/status/hlb8joewtth07nmb/branch/release/1.69.0?svg=true)](https://ci.appveyor.com/project/lasote/conan-boost/branch/release/1.69.0)

[![Build Status](https://travis-ci.org/lasote/conan-boost.svg?branch=release%2F1.69.0)](https://travis-ci.org/lasote/conan-boost)

# conan-boost

Conan package for Boost library

Thanks to @DavidZemon for the huge help with cross-building support!

The packages generated with this **conanfile** can be found on [bintray](https://bintray.com/conan-community).

## Reuse the packages

### Basic setup

    $ conan install boost/1.69.0@conan/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    boost/1.69.0@conan/stable

    [options]
    boost:shared=True # False
    # Take a look for all available options in conanfile.py

    [generators]
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install .

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake*
with all the paths and variables that you need to link with your dependencies.

Follow the Conan getting started: http://docs.conan.io


### Cross building

The package works cross compiled to ARM, tested from windows, using the SYSGCC toolchain and the following profile:

    target_host=arm-linux-gnueabihf
    standalone_toolchain=C:/sysgcc/raspberry
    cc_compiler=gcc
    cxx_compiler=g++

    [settings]
    os=Linux
    arch=armv7
    compiler=gcc
    compiler.version=6
    compiler.libcxx=libstdc++
    build_type=Release

    [env]
    CONAN_CMAKE_FIND_ROOT_PATH=$standalone_toolchain/$target_host/sysroot
    SYSROOT=$standalone_toolchain/$target_host/sysroot
    PATH=[$standalone_toolchain/bin]
    CHOST=$target_host
    AR=$target_host-ar
    AS=$target_host-as
    RANLIB=$target_host-ranlib
    LD=$target_host-ld
    STRIP=$target_host-strip
    CC=$target_host-$cc_compiler
    CXX=$target_host-$cxx_compiler
    CXXFLAGS=-I"$standalone_toolchain/$target_host/lib/include"


Apply the profile when running "conan install" or "conan create" with ``--profile`` option.
