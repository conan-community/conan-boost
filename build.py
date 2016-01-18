import os
from conan.packager import ConanMultiPackager
import sys
import platform
from copy import copy

def add_visual_builds(builder, visual_version, arch):
    base_set = {"compiler": "Visual Studio", 
                "compiler.version": visual_version, 
                "arch": arch}
    sets = []
    sets.append([{"build_type": "Release", "compiler.runtime": "MT"}, {"Boost:shared=False"}])        
    sets.append([{"build_type": "Debug", "compiler.runtime": "MTd"}, {"Boost:shared=False"}])
    sets.append([{"build_type": "Debug", "compiler.runtime": "MDd"}, {"Boost:shared=False"}])
    sets.append([{"build_type": "Release", "compiler.runtime": "MD"}, {"Boost:shared=False"}])
    sets.append([{"build_type": "Debug", "compiler.runtime": "MDd"}, {"Boost:shared=True"}])
    sets.append([{"build_type": "Release", "compiler.runtime": "MD"}, {"Boost:shared=True"}])        
      
    for setting, options in sets:
       tmp = copy(base_set)
       tmp.update(setting)
       builder.add(setting, options)
       
def add_other_builds(builder):
    # Not specified compiler or compiler version, will use the auto detected     
    for arch in ["x86", "x86_64"]:
        for shared in [True, False]:
            for build_type in ["Debug", "Release"]:
                if arch == "x86" and (platform.system() == "Darwin" or os.getenv("TRAVIS", False)):    
                    continue
                builder.add({"arch":arch, "build_type": build_type}, {"Boost:shared": shared})
           
def get_builder(username, channel):
    args = " ".join(sys.argv[1:])
    builder = ConanMultiPackager(args, username, channel)
    if platform.system() == "Windows":
        for visual_version in [10, 12, 14]:
            for arch in ["x86", "x86_64"]:
                add_visual_builds(builder, visual_version, arch)
    else:
        add_other_builds(builder)
    
    return builder
        
if __name__ == "__main__":
    channel = os.getenv("CONAN_CHANNEL", "testing")
    username = os.getenv("CONAN_USERNAME", "lasote")
    current_page = os.getenv("CONAN_CURRENT_PAGE", "1")
    total_pages = os.getenv("CONAN_TOTAL_PAGES", "1")
    
    builder = get_builder(username, channel)
    builder.pack(current_page, total_pages)
    
    if os.getenv("CONAN_UPLOAD", False) and os.getenv("CONAN_REFERENCE") and os.getenv("CONAN_PASSWORD"):
        reference = os.getenv("CONAN_REFERENCE")
        builder.upload_packages(reference, os.getenv("CONAN_PASSWORD"))
