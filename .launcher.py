import platform
import os

import sys

from conans import tools
from conans.client.output import ConanOutput

env = {"CONAN_USERNAME": "lasote",
       "CONAN_CHANNEL": "testing",
       "CONAN_REFERENCE": "boost/1.69.0"}

if platform.system() == "Windows":
    env["CONAN_VISUAL_VERSIONS"] = "15, 14, 12"
elif platform.system() == "Linux":
    env["CONAN_GCC_VERSIONS"] = "4.9, 5, 6, 7"
    env["CONAN_USE_DOCKER"] = "1"
elif platform.system() == "Darwin":
    from conans.client.conf.detect import _get_default_compiler
    _, version = _get_default_compiler(ConanOutput(stream=sys.stdout))
    env["CONAN_APPLE_CLANG_VERSIONS"] = version

with tools.environment_append(env):
    with tools.chdir(os.path.dirname(os.path.realpath(__file__))):
        ret = os.system("python build.py")
        if ret != 0:
            raise Exception("Error!")

