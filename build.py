from conan.packager import ConanMultiPackager
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
                filtered_builds.append([settings, options, env_vars, build_requires])
            builder.builds = filtered_builds

    builder.run()

