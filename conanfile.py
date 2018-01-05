from conans import ConanFile
from conans import tools
import os
import sys
from conans import __version__ as conan_version
from conans.model.version import Version


class BoostConan(ConanFile):
    name = "Boost"
    version = "1.66.0"
    if conan_version < Version("0.99"):
        settings = "os", "arch", "compiler", "build_type"
    else:
        settings = "os", "arch", "compiler", "build_type", "os_build", "arch_build"
    FOLDER_NAME = "boost_%s" % version.replace(".", "_")
    # The current python option requires the package to be built locally, to find default Python
    # implementation
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False],
        "python": [True, False],  # Note: this variable does not have the 'without_' prefix to keep
        # the old shas
        "without_atomic": [True, False],
        "without_chrono": [True, False],
        "without_container": [True, False],
        "without_context": [True, False],
        "without_coroutine": [True, False],
        "without_coroutine2": [True, False],
        "without_date_time": [True, False],
        "without_exception": [True, False],
        "without_fiber": [True, False],
        "without_filesystem": [True, False],
        "without_graph": [True, False],
        "without_graph_parallel": [True, False],
        "without_iostreams": [True, False],
        "without_locale": [True, False],
        "without_log": [True, False],
        "without_math": [True, False],
        "without_metaparse": [True, False],
        "without_mpi": [True, False],
        "without_poly_collection": [True, False],  # New in 1.65.0
        "without_program_options": [True, False],
        "without_random": [True, False],
        "without_regex": [True, False],
        "without_serialization": [True, False],
        "without_signals": [True, False],
        "without_stacktrace": [True, False],  # New in 1.65.0
        "without_system": [True, False],
        "without_test": [True, False],
        "without_thread": [True, False],
        "without_timer": [True, False],
        "without_type_erasure": [True, False],
        "without_wave": [True, False]
    }

    default_options = "shared=False", \
        "header_only=False", \
        "fPIC=False", \
        "python=False", \
        "without_atomic=False", \
        "without_chrono=False", \
        "without_container=False", \
        "without_context=False", \
        "without_coroutine=False", \
        "without_coroutine2=False", \
        "without_date_time=False", \
        "without_exception=False", \
        "without_fiber=False", \
        "without_filesystem=False", \
        "without_graph=False", \
        "without_graph_parallel=False", \
        "without_iostreams=False", \
        "without_locale=False", \
        "without_log=False", \
        "without_math=False", \
        "without_metaparse=False", \
        "without_mpi=False", \
        "without_poly_collection=False", \
        "without_program_options=False", \
        "without_random=False", \
        "without_regex=False", \
        "without_serialization=False", \
        "without_signals=False", \
        "without_stacktrace=False", \
        "without_system=False", \
        "without_test=False", \
        "without_thread=False", \
        "without_timer=False", \
        "without_type_erasure=False", \
        "without_wave=False"

    url = "https://github.com/lasote/conan-boost"
    license = "Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    short_paths = True

    def config_options(self):
        """ First configuration step. Only settings are defined. Options can be removed
        according to these settings
        """
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")

    def configure(self):
        """ Second configuration step. Both settings and options have values, in this case
        we can force static library if MT was specified as runtime
        """
        if self.settings.compiler == "Visual Studio" and \
           self.options.shared and "MT" in str(self.settings.compiler.runtime):
            self.options.shared = False

        if self.options.header_only:
            # Should be doable in conan_info() but the UX is not ready
            self.options.remove("shared")
            self.options.remove("fPIC")
            self.options.remove("python")

        if not self.options.without_iostreams and not self.options.header_only:
            self.requires("bzip2/1.0.6@conan/stable")
            self.options["bzip2/1.0.6"].shared = self.options.shared
            
            self.requires("zlib/1.2.11@conan/stable")
            self.options["zlib"].shared = self.options.shared

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        zip_name = "%s.zip" % self.FOLDER_NAME if sys.platform == "win32" else "%s.tar.gz" % self.FOLDER_NAME
        url = "http://sourceforge.net/projects/boost/files/boost/%s/%s/download" % (self.version, zip_name)
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return

        flags = self.boostrap()

        flags.extend(self.get_build_flags())
        
        # Append flags for zlib
        if not self.options.without_iostreams and not self.options.header_only:
            flags.append("-sBZIP2_BINARY=bz2")
            flags.append("-sBZIP2_INCLUDE=%s" % (self.deps_cpp_info["bzip2"].include_paths[0]))
            flags.append("-sBZIP2_LIBPATH=%s" % (self.deps_cpp_info["bzip2"].lib_paths[0]))
            
            flags.append("-sZLIB_BINARY=zlib%s" % ("d" if self.settings.build_type == "Debug" else ""))
            flags.append("-sZLIB_INCLUDE=%s" % (self.deps_cpp_info["zlib"].include_paths[0]))
            flags.append("-sZLIB_LIBPATH=%s" % (self.deps_cpp_info["zlib"].lib_paths[0]))

        # JOIN ALL FLAGS
        b2_flags = " ".join(flags)

        command = "b2" if self.settings.os == "Windows" else "./b2"

        without_python = "--without-python" if not self.options.python else ""
        full_command = "cd %s && %s %s -j%s --abbreviate-paths %s -d2" % (
            self.FOLDER_NAME,
            command,
            b2_flags,
            tools.cpu_count(),
            without_python)  # -d2 is to print more debug info and avoid travis timing out without output
        
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            full_command = "%s && %s" % (tools.vcvars_command(self.settings), full_command)
      
        self.output.warn(full_command)
        self.run(full_command)

    def get_build_cross(self):
        architecture = self.settings.get_safe('arch')
        flags = []
        self.output.info("Cross building, detecting compiler...")
        # We only need special instructions for non-x86 CPUs.
        # # Boost seems to handle x86 just fine without modding any jam files
        cross_compiler = tools.which(os.environ['CXX'])
        jam_filepath = os.path.join(self.source_folder, self.FOLDER_NAME, 'project-config.jam')
        with open(jam_filepath, 'a') as jam_file:
            jam_file.write('\nusing {0} : {1} : {2} ;'.format(
                self.settings.get_safe('compiler'),
                architecture,
                cross_compiler
            ))
        flags.append('toolset={0}-{1}'.format(self.settings.get_safe('compiler'), architecture))
        flags.append('architecture=' + 'arm' if architecture.startswith('arm') else architecture)
        # Let's just assume it's 32-bit... 64-bit is pretty rare outside of x86_64
        flags.append('address-model=32')
        if self.settings.get_safe('os').lower() == 'linux':
            flags.append('binary-format=elf')
        else:
            raise Exception("I'm so sorry! I don't know the appropriate binary "
                            "format for your architecture. :'(")
        if architecture.startswith('arm'):
            if 'hf' in architecture:
                flags.append('-mfloat-abi=hard')
            flags.append('abi=aapcs')
        else:
            raise Exception("I'm so sorry! I don't know the appropriate ABI for "
                            "your architecture. :'(")
        self.output.info("Cross building flags: %s" % flags)
        return flags

    def get_build_flags(self):
        architecture = self.settings.get_safe('arch')
        flags = []

        if tools.cross_building(self.settings) and architecture not in ['x86', 'x86_64']:
            flags = self.get_build_cross()
        else:
            if self.settings.compiler == "Visual Studio":
                flags.append("toolset=msvc-%s" % self._msvc_version())
            elif not self.settings.os == "Windows" and self.settings.compiler == "gcc" and \
                    str(self.settings.compiler.version)[0] >= "5":
                # For GCC >= v5 we only need the major otherwise Boost doesn't find the compiler
                # The NOT windows check is necessary to exclude MinGW:
                flags.append("toolset=%s-%s" % (self.settings.compiler,
                                                str(self.settings.compiler.version)[0]))
            elif str(self.settings.compiler) in ["clang", "gcc"]:
                # For GCC < v5 and Clang we need to provide the entire version string
                flags.append("toolset=%s-%s" % (self.settings.compiler,
                                                str(self.settings.compiler.version)))
            if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime:
                flags.append("runtime-link=%s" % ("static" if "MT" in str(self.settings.compiler.runtime) else "shared"))

        flags.append("link=%s" % ("static" if not self.options.shared else "shared"))
        flags.append("variant=%s" % str(self.settings.build_type).lower())
        if architecture == 'x86':
            flags.append('address-model=32')
        elif architecture == 'x86_64':
            flags.append('address-model=64')

        option_names = {
            "--without-atomic": self.options.without_atomic,
            "--without-chrono": self.options.without_chrono,
            "--without-container": self.options.without_container,
            "--without-context": self.options.without_context,
            "--without-coroutine": self.options.without_coroutine,
            "--without-coroutine2": self.options.without_coroutine2,
            "--without-date_time": self.options.without_date_time,
            "--without-exception": self.options.without_exception,
            "--without-fiber": self.options.without_fiber,
            "--without-filesystem": self.options.without_filesystem,
            "--without-graph": self.options.without_graph,
            "--without-graph_parallel": self.options.without_graph_parallel,
            "--without-iostreams": self.options.without_iostreams,
            "--without-locale": self.options.without_locale,
            "--without-log": self.options.without_log,
            "--without-math": self.options.without_math,
            "--without-metaparse": self.options.without_metaparse,
            "--without-mpi": self.options.without_mpi,
            "--without-program_options": self.options.without_program_options,
            "--without-random": self.options.without_random,
            "--without-regex": self.options.without_regex,
            "--without-serialization": self.options.without_serialization,
            "--without-signals": self.options.without_signals,
            "--without-system": self.options.without_system,
            "--without-test": self.options.without_test,
            "--without-thread": self.options.without_thread,
            "--without-timer": self.options.without_timer,
            "--without-type_erasure": self.options.without_type_erasure,
            "--without-wave": self.options.without_wave
        }

        for option_name, activated in option_names.items():
            if activated:
                flags.append(option_name)

        cxx_flags = []
        # fPIC DEFINITION
        if self.settings.compiler != "Visual Studio":
            if self.options.fPIC:
                cxx_flags.append("-fPIC")

        # LIBCXX DEFINITION FOR BOOST B2
        try:
            if str(self.settings.compiler.libcxx) == "libstdc++":
                flags.append("define=_GLIBCXX_USE_CXX11_ABI=0")
            elif str(self.settings.compiler.libcxx) == "libstdc++11":
                flags.append("define=_GLIBCXX_USE_CXX11_ABI=1")
            if "clang" in str(self.settings.compiler):
                if str(self.settings.compiler.libcxx) == "libc++":
                    cxx_flags.append("-stdlib=libc++")
                    cxx_flags.append("-std=c++11")
                    flags.append('linkflags="-stdlib=libc++"')
                else:
                    cxx_flags.append("-stdlib=libstdc++")
                    cxx_flags.append("-std=c++11")
        except:
            pass

        cxx_flags = 'cxxflags="%s"' % " ".join(cxx_flags) if cxx_flags else ""
        flags.append(cxx_flags)
        return flags

    def boostrap(self):
        with_toolset = {"apple-clang": "darwin"}.get(str(self.settings.compiler),
                                                     str(self.settings.compiler))
        command = "bootstrap" if self.settings.os_build == "Windows" \
                              else "./bootstrap.sh --with-toolset=%s" % with_toolset

        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            command = "%s && %s" % (tools.vcvars_command(self.settings), command)

        flags = []
        if self.settings.os_build == "Windows" and self.settings.compiler == "gcc":
            command += " mingw"
            flags.append("--layout=system")
            
        try:
            self.run("cd %s && %s" % (self.FOLDER_NAME, command))
        except:
            self.run("cd %s && type bootstrap.log" % self.FOLDER_NAME
                     if self.settings.os_build == "Windows"
                     else "cd %s && cat bootstrap.log" % self.FOLDER_NAME)
            raise
        return flags

    def package(self):
        self.copy(pattern="*", dst="include/boost", src="%s/boost" % self.FOLDER_NAME)
        self.copy(pattern="*.a", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.so", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.so.*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.dylib*", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.lib", dst="lib", src="%s/stage/lib" % self.FOLDER_NAME)
        self.copy(pattern="*.dll", dst="bin", src="%s/stage/lib" % self.FOLDER_NAME)

        if not self.options.header_only and self.settings.compiler == "Visual Studio" and \
           self.options.shared == "False":
            # CMake findPackage help
            renames = []
            for libname in os.listdir(os.path.join(self.package_folder, "lib")):
                libpath = os.path.join(self.package_folder, "lib", libname)
                new_name = libname
                if new_name.startswith("lib"):
                    if os.path.isfile(libpath):
                        new_name = libname[3:]
                if "-s-" in libname:
                    new_name = new_name.replace("-s-", "-")
                elif "-sgd-" in libname:
                    new_name = new_name.replace("-sgd-", "-gd-")

                renames.append([libpath, os.path.join(self.package_folder, "lib", new_name)])

            for original, new in renames:
                if original != new:
                    self.output.info("Rename: %s => %s" % (original, new))
                    os.rename(original, new)

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

        if self.options.without_test: # remove boost_unit_test_framework
            self.cpp_info.libs = [lib for lib in self.cpp_info.libs if "unit_test" not in lib]

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)

        if not self.options.header_only and self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
        else:
            self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

        if not self.options.header_only:
            if self.options.python:
                if not self.options.shared:
                    self.cpp_info.defines.append("BOOST_PYTHON_STATIC_LIB")

            if self.settings.compiler == "Visual Studio":
                # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
                self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"])

    def _msvc_version(self):
        if self.settings.compiler.version == "15":
            return "14.1"
        else:
            return "%s.0" % self.settings.compiler.version
