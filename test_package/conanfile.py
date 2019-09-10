import platform

from conans.client.run_environment import RunEnvironment
from conans.model.conan_file import ConanFile, tools
from conans import CMake
import os
import sys


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        if self.options["boost"].header_only:
            cmake.definitions["HEADER_ONLY"] = "TRUE"
        else:
            cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        if self.options["boost"].python:
            cmake.definitions["WITH_PYTHON"] = "TRUE"
        if not self.options["boost"].without_test:
            cmake.definitions["WITH_TEST"] = "TRUE"
        if not self.options["boost"].without_locale:
            cmake.definitions["WITH_LOCALE"] = "TRUE"
        if not self.options["boost"].without_regex:
            cmake.definitions["WITH_REGEX"] = "TRUE"
        if self.options["boost"].use_icu:
            cmake.definitions["ICU_USE_STATIC_LIBS"] = not self.options["icu"].shared
            cmake.definitions["USE_ICU"] = "TRUE"

        if "CONAN_CMAKE_CXX_STANDARD" in cmake.definitions:
            cmake.definitions["CMAKE_CXX_STANDARD"] = cmake.definitions["CONAN_CMAKE_CXX_STANDARD"]
            cmake.definitions["CMAKE_CXX_EXTENSIONS"] = cmake.definitions["CONAN_CMAKE_CXX_EXTENSIONS"]

        cmake.configure()
        cmake.build()


    def test(self):
        if tools.cross_building(self.settings):
            return
        bt = self.settings.build_type
        re = RunEnvironment(self)
        with tools.environment_append(re.vars):
            if platform.system() == "Darwin":
                lpath = os.environ["DYLD_LIBRARY_PATH"]
                self.run('DYLD_LIBRARY_PATH=%s ctest --output-on-error -C %s' % (lpath, bt))
            else:
                self.run('ctest --output-on-error -C %s' % bt)
            if self.options["boost"].python:
                os.chdir("bin")
                sys.path.append(".")
                import hello_ext
                hello_ext.greet()
