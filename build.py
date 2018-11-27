from conan.packager import ConanMultiPackager
import copy
import platform


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="boost:shared", pure_c=False)

    if platform.system() == "Windows":
        filtered_builds = []
        for settings, options, env_vars, build_requires in builder.builds:
            # MinGW shared with linker errors. I don't have a clue
            if settings["compiler"] == "gcc" and options["boost:shared"] == True:
                continue
            filtered_builds.append([settings, options, env_vars, build_requires])
        builder.builds = filtered_builds

    if platform.system() == "Linux":
        filtered_builds = []
        for settings, options, env_vars, build_requires in builder.builds:
            filtered_builds.append([settings, options])
            new_options = copy.copy(options)
            new_options["boost:fPIC"] = True
            filtered_builds.append([settings, new_options, env_vars, build_requires])
        builder.builds = filtered_builds

    builder.run()

