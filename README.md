[![Download](https://api.bintray.com/packages/conan-community/conan/Boost%3Aconan/images/download.svg) ](https://bintray.com/conan-community/conan/Boost%3Aconan/_latestVersion)
[![Build Status Travis](https://travis-ci.org/conan-community/conan-Boost.svg)](https://travis-ci.org/conan-community/conan-Boost)
[![Build Status AppVeyor](https://ci.appveyor.com/api/projects/status/github/conan-community/conan-Boost?svg=true)](https://ci.appveyor.com/project/ConanCIintegration/conan-Boost)

## Conan package recipe for *Boost*



The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/conan-community/conan/Boost%3Aconan).


## Issues

If you wish to report an issue or make a request for a package, please do so here:

[Issues Tracker](https://github.com/conan-community/community/issues)


## For Users

### Basic setup

    $ conan install Boost/1.62.0@conan/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    Boost/1.62.0@conan/stable

    [generators]
    txt

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create . conan/stable


### Available Options
| Option        | Default | Possible Values  |
| ------------- |:----------------- |:------------:|
| shared      | False |  [True, False] |
| header_only      | False |  [True, False] |
| fPIC      | False |  [True, False] |
| python      | False |  [True, False] |
| without_atomic      | False |  [True, False] |
| without_chrono      | False |  [True, False] |
| without_container      | False |  [True, False] |
| without_context      | False |  [True, False] |
| without_coroutine      | False |  [True, False] |
| without_coroutine2      | False |  [True, False] |
| without_date_time      | False |  [True, False] |
| without_exception      | False |  [True, False] |
| without_filesystem      | False |  [True, False] |
| without_graph      | False |  [True, False] |
| without_graph_parallel      | False |  [True, False] |
| without_iostreams      | False |  [True, False] |
| without_locale      | False |  [True, False] |
| without_log      | False |  [True, False] |
| without_math      | False |  [True, False] |
| without_mpi      | False |  [True, False] |
| without_program_options      | False |  [True, False] |
| without_random      | False |  [True, False] |
| without_regex      | False |  [True, False] |
| without_serialization      | False |  [True, False] |
| without_signals      | False |  [True, False] |
| without_system      | False |  [True, False] |
| without_test      | False |  [True, False] |
| without_thread      | False |  [True, False] |
| without_timer      | False |  [True, False] |
| without_type_erasure      | False |  [True, False] |
| without_wave      | False |  [True, False] |


## Add Remote

Conan Community has its own Bintray repository, however, we are working to distribute all package in the Conan Center:

    $ conan remote add conan-center "https://conan.bintray.com"


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package Boost.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](LICENSE)
