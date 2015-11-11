from conans import ConanFile
from conans import tools
import platform, os, sys


class BoostConan(ConanFile):
    name = "Boost"
    version = "1.57.0" 
    
    settings = "os", "arch", "compiler", "build_type"   
    FOLDER_NAME = "boost_%s" % version.replace(".", "_") 
    options = {"shared": [True, False], "header_only": [True, False]}
    default_options = "shared=True", "header_only=False"
    counter_config = 0
   
    def config(self):
        # If header only, the compiler, etc, does not affect the package!
        self.counter_config += 1
        # config is called twice, one before receive the upper dependencies and another before
        if self.options.header_only and self.counter_config==2:
            self.output.info("HEADER ONLY")
            self.settings.clear()
            self.options.remove("shared")
        if not self.options.header_only and self.settings.os == "Windows" and self.options.shared and "MT" in str(self.settings.compiler.runtime):
            self.options.shared = False

    def source(self):
        zip_name = "%s.zip" % self.FOLDER_NAME if sys.platform == "win32" else "%s.tar.gz" % self.FOLDER_NAME
        url = "http://sourceforge.net/projects/boost/files/boost/%s/%s/download" % (self.version, zip_name)
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)
        tools.unzip(zip_name, ".")
        os.unlink(zip_name)

    def build(self):
        if self.options.header_only:
            return
        
        if self.settings.os == "Linux": # Fixme, just debian based works for building
            self.run("sudo apt-get install libbz2-dev || true")
            self.run("sudo apt-get install gcc-%s-multilib || true" % self.settings.compiler.version)
            self.run("sudo apt-get install g++-%s-multilib || true" % self.settings.compiler.version)
            self.run("sudo dpkg --add-architecture i386 || true")
            self.run("sudo apt-get update || true")
            self.run("sudo apt-get install libbz2-dev:i386 || true")

        command = "bootstrap" if self.settings.os == "Windows" else "./bootstrap.sh"
        try:
            self.run("cd %s && %s" % (self.FOLDER_NAME, command))
        except:
            self.run("cd %s && type bootstrap.log" if self.settings.os == "Windows" else "cd %s && cat bootstrap.sh")
            raise

        flags = []
        if self.settings.compiler == "Visual Studio":
            flags.append("toolset=msvc-12.0")

        flags.append("link=%s" % ("static" if not self.options.shared else "shared"))
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime:
            flags.append("runtime-link=%s" % ("static" if "MT" in str(self.settings.compiler.runtime) else "shared"))
        flags.append("variant=%s" % str(self.settings.build_type).lower())
        flags.append("address-model=%s" % ("32" if self.settings.arch == "x86" else "64"))
        b2_flags = " ".join(flags)

        command = "b2" if self.settings.os == "Windows" else "./b2"
        full_command = "cd %s && %s %s -j4 --abbreviate-paths --without-python" % (self.FOLDER_NAME, command, b2_flags)
        self.output.warn(full_command)
        self.run(full_command)

    def package(self):
        self.copy(pattern="*", dst="include/boost", src="%s/boost" % self.FOLDER_NAME)
        self.copy(pattern="*.a", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.so", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.so.*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.dylib*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.lib", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.dll", dst="bin", src="%s/stage/lib" % self.FOLDER_NAME)
        
    def package_info(self):
        if not self.options.header_only:
            if self.options.shared:
                self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
            else:
                self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

        libs = ("atomic chrono container context coroutine date_time exception filesystem "
                "graph iostreams locale log_setup log math_c99 math_c99f math_c99l math_tr1 "
                "math_tr1f math_tr1l prg_exec_monitor program_options random regex serialization "
                "signals system test_exec_monitor thread timer unit_test_framework wave "
                "wserialization").split()
        if not self.options.header_only and self.settings.os != "Windows":
            self.cpp_info.libs.extend(["boost_%s" % lib for lib in libs])
        elif self.settings.os == "Windows":
            win_libs = []
            # http://www.boost.org/doc/libs/1_55_0/more/getting_started/windows.html
            visual_version = int(str(self.settings.compiler.version)) * 10
            runtime = "mt"# str(self.settings.compiler.runtime).lower()
            
            abi_tags = []
            if self.settings.compiler.runtime in ("MTd", "MT"):
                abi_tags.append("s")
            
            if self.settings.build_type == "Debug":
                abi_tags.append("gd")
            
            abi_tags = ("-%s" % "".join(abi_tags)) if abi_tags else ""
            
            version = "_".join(self.version.split(".")[0:2])
            suffix = "vc%d-%s%s-%s" %  (visual_version, runtime, abi_tags, version)
            prefix = "lib" if not self.options.shared else ""
            
            
            win_libs.extend(["%sboost_%s-%s" % (prefix, lib, suffix) for lib in libs if lib not in ["exception", "test_exec_monitor"]])
            win_libs.extend(["libboost_exception-%s" % suffix, "libboost_test_exec_monitor-%s" % suffix])
            
            #self.output.warn("EXPORTED BOOST LIBRARIES: %s" % win_libs)
            self.cpp_info.libs.extend(win_libs)
            self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"]) # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
