from conan.packager import ConanMultiPackager
import copy
import platform
import os


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="Boost:shared", pure_c=False)
    if os.getenv("CONAN_VISUAL_VERSIONS") == "15":
        # There is an unknown problem in visual 2015 trying to use 2017 to do something with b2
        new_build = copy.deepcopy(builder.builds)[-1]
        new_build.options["Boost:header_only"] = True
        builder.add(*new_build)

    if platform.system() == "Linux":
        filtered_builds = []
        for settings, options, env_vars, build_requires in builder.builds:
            filtered_builds.append([settings, options])
            new_options = copy.copy(options)
            new_options["Boost:fPIC"] = True
            filtered_builds.append([settings, new_options, env_vars, build_requires])
        builder.builds = filtered_builds
    builder.run()

