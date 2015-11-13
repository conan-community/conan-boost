[![Build Status](https://travis-ci.org/lasote/conan-boost.svg?branch=master)](https://travis-ci.org/lasote/conan-boost)

# conan-boost


[Conan.io](https://conan.io) package for boost library

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/boost/1.59.0/lasote/stable).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py
    
## Upload packages to server

    $ conan upload boost/1.59.0@lasote/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install boost/1.59.0@lasote/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    boost/1.59.0@lasote/stable

    [options]
    boost:shared=true # false
    # Take a look for all available options in conanfile.py
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

