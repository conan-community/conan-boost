from conans.model.conan_file import ConanFile
from conans import CMake
import os
import sys
import platform


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

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        
    def test(self):        
        data_file = os.path.join(self.source_folder, "data.txt")
        self.run("cd bin && .%slambda < %s" % (os.sep, data_file))
        if os.path.exists("bin/regex_exe%s" % ".exe" if platform.system == "Windows" else ""):
            self.output.warn("Running regex_exe...")
            self.run("cd bin && .%sregex_exe < %s" % (os.sep, data_file))
            if self.options["Boost"].python:
                os.chdir("bin")
                sys.path.append(".")
                import hello_ext
                hello_ext.greet()
        if os.path.exists("bin/newregex%s" % ".exe" if platform.system == "Windows" else ""):
            self.output.warn("Running newregex...")
            self.run("cd bin && .%sregex_exe < %s" % (os.sep, data_file))
