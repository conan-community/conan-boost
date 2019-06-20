from conan.packager import ConanMultiPackager
import copy
import os
import platform



if __name__ == "__main__":
    builder = ConanMultiPackager()

    if os.getenv("HEADER_ONLY"):

        builder.add({}, {"boost:header_only": True})
    else:
        builder.add_common_builds(shared_option_name="boost:shared", pure_c=False)

        if platform.system() == "Windows":
            filtered_builds = []
            for settings, options, env_vars, build_requires in builder.builds:

                # MinGW shared with linker errors. I don't have a clue
                if settings["compiler"] == "gcc" and options["boost:shared"] is True:
                    continue

                if ( ( settings["compiler"] == "Visual Studio" ) and ( int(settings["compiler.version"]) >= 14 ) ) and ( int(settings["compiler.version"]) <= 15 ):
                    options_use_icu = options.copy()
                    options_use_icu["boost:use_icu"] = True
                    filtered_builds.append([settings, options_use_icu, env_vars, build_requires])

                filtered_builds.append([settings, options, env_vars, build_requires])
            builder.builds = filtered_builds


        if platform.system() == "Linux":
            filtered_builds = []
            for settings, options, env_vars, build_requires in builder.builds:

                if ( settings["compiler"] == "clang" ) and ( float( settings["compiler.version"] ) >= 6 ):
                    settings_libstdcxx11 = settings.copy()
                    settings_libstdcxx11["compiler.libcxx"] = "libstdc++11"
                    filtered_builds.append([settings_libstdcxx11, options, env_vars, build_requires])

                    options_use_icu = options.copy()
                    options_use_icu["boost:use_icu"] = True
                    filtered_builds.append([settings_libstdcxx11, options_use_icu, env_vars, build_requires])

                if ( settings["compiler"] == "gcc" ) and ( settings["compiler.libcxx"] == "libstdc++11" ) and ( float( settings["compiler.version"] ) >= 6 ) :
                    options_use_icu = options.copy()
                    options_use_icu["boost:use_icu"] = True
                    filtered_builds.append([settings, options_use_icu, env_vars, build_requires])

                filtered_builds.append([settings, options, env_vars, build_requires])
            builder.builds = filtered_builds


        if platform.system() == "Darwin":
            filtered_builds = []
            for settings, options, env_vars, build_requires in builder.builds:

                settings_cppstd = settings.copy()
                settings_cppstd["compiler.cppstd"] = 11
                options_use_icu = options.copy()
                options_use_icu["boost:use_icu"] = True
                filtered_builds.append([settings_cppstd, options_use_icu, env_vars, build_requires])

                filtered_builds.append([settings, options, env_vars, build_requires])

            builder.builds = filtered_builds

    builder.run()
