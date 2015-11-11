from conans.model.conan_file import ConanFile
from conans import CMake
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    requires = "Boost/1.57.0@lasote/stable"
    generators = "cmake"

    def config(self):
        # If header only, the compiler, etc, does not affect the package!
        # RECURRENT PROBLEM!! premature evaluation
        if self.options["Boost"].header_only:
            self.settings.clear()

    def build(self):
        cmake = CMake(self.settings)
        header_only = "ON" if self.options["Boost"].header_only else "OFF"
        self.run('cmake . %s -DHEADER_ONLY=%s' % (cmake.command_line, header_only))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
        
    def test(self):
        self.run("cd bin && .%slambda < ../data.txt" % (os.sep))
        if not self.options["Boost"].header_only:
            self.run("cd bin && .%sregex_exe < ../data.txt" % (os.sep))
