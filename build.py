import os
from conan.packager import ConanMultiPackager
import sys
import platform
from copy import copy

if __name__ == "__main__":
    channel = os.getenv("CONAN_CHANNEL", "testing")
    username = os.getenv("CONAN_USERNAME", "lasote")
    current_page = os.getenv("CONAN_CURRENT_PAGE", "1")
    total_pages = os.getenv("CONAN_TOTAL_PAGES", "1")
    gcc_versions = os.getenv("CONAN_GCC_VERSIONS", None)
    gcc_versions = gcc_versions.split(",") if gcc_versions else None
    use_docker = os.getenv("CONAN_USE_DOCKER", False)
    upload = os.getenv("CONAN_UPLOAD", False)
    reference = os.getenv("CONAN_REFERENCE")
    password = os.getenv("CONAN_PASSWORD")
    travis = os.getenv("TRAVIS", False)
    travis_branch = os.getenv("TRAVIS_BRANCH", None)
    appveyor = os.getenv("APPVEYOR", False)
    appveyor_branch = os.getenv("APPVEYOR_REPO_BRANCH", None)

    channel = "stable" if travis and travis_branch=="master" else channel
    channel = "stable" if appveyor and appveyor_branch=="master" and not os.getenv("APPVEYOR_PULL_REQUEST_NUMBER") else channel
    os.environ["CONAN_CHANNEL"] = channel # Override the environment value for test/conanfile.py file

    args = " ".join(sys.argv[1:])
    builder = ConanMultiPackager(args, username, channel)
    builder.add_common_builds(shared_option_name="Boost:shared", visual_versions=[10, 12, 14])
    print(builder.builds)

    if use_docker:  
        builder.docker_pack(current_page, total_pages, gcc_versions)
    else:
        builder.pack(current_page, total_pages)

    if upload and reference and password:
        builder.upload_packages(reference, password)
