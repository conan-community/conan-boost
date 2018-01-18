import platform
import os

from conans import tools

env = {"CONAN_USERNAME": "lasote",
       "CONAN_CHANNEL": "testing"}

if platform.system() == "Windows":
    env["CONAN_VISUAL_VERSIONS"] = "15, 14, 12"

if platform.system() == "Linux":
    env["CONAN_GCC_VERSIONS"] = "4.9, 5, 6, 7"
    env["CONAN_USE_DOCKER"] = "1"

elif platform.system() == "Darwin":
    from conans.client.conf.detect import _get_default_compiler
    _ , version = _get_default_compiler()
    env["CONAN_APPLE_CLANG_VERSIONS"] = version

with tools.environment_append(env):
    print(env)
    os.system("python build.py")

