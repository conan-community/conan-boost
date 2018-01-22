import shutil

from conans import ConanFile
from conans import tools
import os
import sys

# From from *1 (see below, b2 --show-libraries), also ordered following linkage order
# see https://github.com/Kitware/CMake/blob/master/Modules/FindBoost.cmake to know the order

lib_list = ['math', 'wave', 'container', 'exception', 'graph', 'iostreams', 'locale', 'log',
            'program_options', 'random', 'regex', 'mpi', 'serialization', 'signals',
            'coroutine', 'fiber', 'context', 'timer', 'thread', 'chrono', 'date_time',
            'atomic', 'filesystem', 'system', 'graph_parallel', 'python',
            'stacktrace', 'test', 'type_erasure']


class BoostConan(ConanFile):
    name = "Boost"
    version = "1.66.0"
    settings = "os", "arch", "compiler", "build_type"
    folder_name = "boost_%s" % version.replace(".", "_")
    # The current python option requires the package to be built locally, to find default Python
    # implementation
    options = {
        "shared": [True, False],
        "header_only": [True, False],
        "fPIC": [True, False]
    }
    options.update({"without_%s" % libname: [True, False] for libname in lib_list})

    default_options = ["shared=False", "header_only=False", "fPIC=False"]
    default_options.extend(["without_%s=False" % libname for libname in lib_list if libname != "python"])
    default_options.append("without_python=True")
    default_options = tuple(default_options)

    url = "https://github.com/lasote/conan-boost"
    license = "Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    short_paths = True
    no_copy_source = False

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")

    def configure(self):
        if not self.options.without_iostreams and not self.options.header_only:
            self.requires("bzip2/1.0.6@conan/stable")
            self.options["bzip2"].shared = False
            
            self.requires("zlib/1.2.11@conan/stable")
            self.options["zlib"].shared = False

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        zip_name = "%s.zip" % self.folder_name if sys.platform == "win32" else "%s.tar.gz" % self.folder_name
        url = "http://sourceforge.net/projects/boost/files/boost/%s/%s/download" % (self.version, zip_name)
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)

        tools.unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.options.header_only:
            self.output.warn("Header only package, skipping build")
            return

        b2_exe = self.bootstrap()
        flags = self.get_build_flags()
        # Help locating bzip2 and zlib
        self.create_user_config_jam(self.build_folder)

        # JOIN ALL FLAGS
        b2_flags = " ".join(flags)
        full_command = "%s %s -j%s --abbreviate-paths -d2" % (b2_exe, b2_flags, tools.cpu_count())
        # -d2 is to print more debug info and avoid travis timing out without output
        sources = os.path.join(self.source_folder, self.folder_name)
        full_command += ' --debug-configuration --build-dir="%s"' % self.build_folder
        self.output.warn(full_command)

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            with tools.chdir(sources):
                # to locate user config jam (BOOST_BUILD_PATH)
                with tools.environment_append({"BOOST_BUILD_PATH": self.build_folder}):
                    # To show the libraries *1
                    # self.run("%s --show-libraries" % b2_exe)
                    self.run(full_command)

    def get_build_cross(self):
        architecture = self.settings.get_safe('arch')
        flags = []
        self.output.info("Cross building, detecting compiler...")
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
        flags.append("target-os=%s" % str(self.settings.os).lower())
        return flags

    def get_build_flags(self):

        architecture = self.settings.get_safe('arch')
        flags = []

        if self.settings.compiler == "gcc":
            flags.append("--layout=system")

        if tools.cross_building(self.settings) and architecture not in ['x86', 'x86_64']:
            flags = self.get_build_cross()
        else:
            if self.settings.compiler == "Visual Studio":
                cversion = self.settings.compiler.version
                _msvc_version = "14.1" if  cversion == "15" else "%s.0" % cversion
                flags.append("toolset=msvc-%s" % _msvc_version)
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

        for libname in lib_list:
            if getattr(self.options, "without_%s" % libname):
                flags.append("--without-%s" % libname)

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

        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            flags.append("threading=multi")

        return flags

    def create_user_config_jam(self, folder):
        """To help locating the zlib and bzip2 deps"""
        self.output.warn("Patching user-config.jam")
        contents = "\nusing zlib : 1.2.11 : <include>%s <search>%s ;" % (
            self.deps_cpp_info["zlib"].include_paths[0].replace('\\', '/'),
            self.deps_cpp_info["zlib"].lib_paths[0].replace('\\', '/'))
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            contents += "\nusing bzip2 : 1.0.6 : <include>%s <search>%s ;" % (
                self.deps_cpp_info["bzip2"].include_paths[0].replace('\\', '/'),
                self.deps_cpp_info["bzip2"].lib_paths[0].replace('\\', '/'))

        if not tools.cross_building(self.settings) and self.settings.compiler in ("gcc", "clang"):
            compiler = os.environ.get('CC', None) or "gcc"
            contents += '\nusing %s : %s : "%s" ; ' % (self.settings.compiler,
                                                       self.settings.compiler.version,
                                                       tools.which(compiler).replace("\\", "/"))

        if tools.cross_building(self.settings) and self.settings.arch not in ["x86_64", "x86"]:
            # We only need special instructions for non-x86 CPUs.
            # # Boost seems to handle x86 just fine without modding any jam files
            cross_compiler = tools.which(os.environ['CXX']).replace("\\", "/")
            contents += '\nusing {0} : {1} : "{2}"'.format(
                    self.settings.get_safe('compiler'),
                    self.settings.arch,
                    cross_compiler)
            contents += " :\n"
            if "AR" in os.environ:
                contents += '<archiver>"%s" ' % tools.which(os.environ["AR"]).replace("\\", "/")
            if "RANLIB" in os.environ:
                contents += '<ranlib>"%s" ' % tools.which(os.environ["RANLIB"]).replace("\\", "/")
            if "CXXFLAGS" in os.environ:
                contents += '<cxxflags>"%s" ' % os.environ["CXXFLAGS"]
            if "CFLAGS" in os.environ:
                contents += '<cflags>"%s" ' % os.environ["CFLAGS"]


            contents += " ;"
        self.output.warn(contents)
        filename = "%s/user-config.jam" % folder
        tools.save(filename,  contents)

    ##################### BOOSTRAP METHODS ###########################
    def _get_boostrap_toolset(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            comp_ver = self.settings.compiler.version
            return "vc%s" % ("141" if comp_ver == "15" else comp_ver)

        with_toolset = {"apple-clang": "darwin"}.get(str(self.settings.compiler),
                                                     str(self.settings.compiler))
        return with_toolset

    def bootstrap(self):
        folder = os.path.join(self.source_folder, self.folder_name, "tools", "build")
        try:
            bootstrap = "bootstrap.bat" if tools.os_info.is_windows else "./bootstrap.sh"
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                self.output.info("Using %s %s" % (self.settings.compiler, self.settings.compiler.version))
                with tools.chdir(folder):
                    self.run("%s %s" % (bootstrap, self._get_boostrap_toolset()))
        except Exception:
            self.output.warn(tools.load(os.path.join(folder, "bootstrap.log")))
            raise
        return os.path.join(folder, "b2.exe") if tools.os_info.is_windows else os.path.join(folder, "b2")

    ####################################################################

    def package(self):
        # This stage/lib is in source_folder... Face palm, looks like it builds in build but then
        # copy to source with the good lib name
        out_lib_dir = os.path.join(self.folder_name, "stage", "lib")
        self.copy(pattern="*", dst="include/boost", src="%s/boost" % self.folder_name)
        if not self.options.shared:
            self.copy(pattern="*.a", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=out_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.so.*", dst="lib", src=out_lib_dir, keep_path=False, symlinks=True)
        self.copy(pattern="*.dylib*", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=out_lib_dir, keep_path=False)

        # When first call with source do not package anything
        if not os.path.exists(os.path.join(self.package_folder, "lib")):
            return

        self.renames_to_make_cmake_find_package_happy()

    def renames_to_make_cmake_find_package_happy(self):
        # CMake findPackage help
        renames = []
        for libname in os.listdir(os.path.join(self.package_folder, "lib")):
            new_name = libname
            libpath = os.path.join(self.package_folder, "lib", libname)
            if self.settings.compiler == "Visual Studio":
                if new_name.startswith("lib"):
                    if os.path.isfile(libpath):
                        new_name = libname[3:]
                if "-s-" in libname:
                    new_name = new_name.replace("-s-", "-")
                elif "-sgd-" in libname:
                    new_name = new_name.replace("-sgd-", "-gd-")

            for arch in ["x", "a", "i", "s", "m", "p"]:  # Architectures
                for addr in ["32", "64"]:  # Model address
                    new_name = new_name.replace("-%s%s-" % (arch, addr), "-")

            renames.append([libpath, os.path.join(self.package_folder, "lib", new_name)])

        for original, new in renames:
            if original != new and not os.path.exists(new):
                self.output.info("Rename: %s => %s" % (original, new))
                os.rename(original, new)

    def package_info(self):
        gen_libs = tools.collect_libs(self)

        self.cpp_info.libs = [None for _ in range(len(lib_list))]

        # The order is important, reorder following the lib_list order
        missing_order_info = []
        for real_lib_name in gen_libs:
            for pos, alib in enumerate(lib_list):
                if os.path.splitext(real_lib_name)[0].split("-")[0].endswith(alib):
                    self.cpp_info.libs[pos] = real_lib_name
                    break
            else:
                self.output.info("Missing in order: %s" % real_lib_name)
                missing_order_info.append(real_lib_name)  # Assume they do not depend on other

        self.cpp_info.libs = [x for x in self.cpp_info.libs if x is not None] + missing_order_info

        if self.options.without_test:  # remove boost_unit_test_framework
            self.cpp_info.libs = [lib for lib in self.cpp_info.libs if "unit_test" not in lib]

        self.output.info("LIBRARIES: %s" % self.cpp_info.libs)
        self.output.info("Package folder: %s" % self.package_folder)

        if not self.options.header_only and self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")
        else:
            self.cpp_info.defines.append("BOOST_USE_STATIC_LIBS")

        if not self.options.header_only:
            if not self.options.without_python:
                if not self.options.shared:
                    self.cpp_info.defines.append("BOOST_PYTHON_STATIC_LIB")

            if self.settings.compiler == "Visual Studio":
                # DISABLES AUTO LINKING! NO SMART AND MAGIC DECISIONS THANKS!
                self.cpp_info.defines.extend(["BOOST_ALL_NO_LIB"])
