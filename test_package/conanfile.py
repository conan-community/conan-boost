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

    def configure(self):
        if self.options["Boost"].header_only:
            self.settings.clear()

    def build(self):
        cmake = CMake(self)
        if self.options["Boost"].header_only:
            cmake.definitions["HEADER_ONLY"] = "TRUE"
        if self.options["Boost"].python:
            cmake.definitions["WITH_PYTHON"] = "TRUE"
        cmake.configure()
        cmake.build()

    def test(self):
        bt = self.settings.build_type
        re = RunEnvironment(self)
        with tools.environment_append(re.vars):
            lpath = os.environ["DYLD_LIBRARY_PATH"]
            self.run('DYLD_LIBRARY_PATH=%s ctest --output-on-error -C %s' % (lpath, bt))
            if self.options["Boost"].python:
                os.chdir("bin")
                sys.path.append(".")
                import hello_ext
                hello_ext.greet()
