from conan.packager import ConanMultiPackager
import copy
import platform


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="Boost:shared", pure_c=False)    
    builder.builds.append([{}, {"Boost:header_only": True}])
    if platform.system() == "Linux":
        filtered_builds = []
        for settings, options in builder.builds:
            filtered_builds.append([settings, options])
            new_options = copy.copy(options)
            new_options["Boost:fPIC"] = True
            filtered_builds.append([settings, new_options])
        builder.builds = filtered_builds
    builder.run()

