from conans.model.conan_file import ConanFile
from conans import CMake
import os
import sys


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def config(self):
        if self.options["Boost"].header_only:
            self.settings.clear()

    def build(self):
        cmake = CMake(self.settings)
        header_only = "-DHEADER_ONLY=TRUE " if self.options["Boost"].header_only else ""
        with_python = "-DWITH_PYTHON=True" if self.options["Boost"].python else ""
        self.run('cmake "%s" %s %s %s' % (self.conanfile_directory, cmake.command_line, header_only, with_python))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        
    def test(self):        
        data_file = os.path.join(self.conanfile_directory, "data.txt")
        self.run("cd bin && .%slambda < %s" % (os.sep, data_file))
        if not self.options["Boost"].header_only:
            self.run("cd bin && .%sregex_exe < %s" % (os.sep, data_file))
            if self.options["Boost"].python:
                os.chdir("bin")
                sys.path.append(".")
                import hello_ext
                hello_ext.greet()
