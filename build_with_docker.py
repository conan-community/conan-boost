import os
from build import get_builder

if __name__ == "__main__":
    channel = os.getenv("CONAN_CHANNEL", "testing")
    username = os.getenv("CONAN_USERNAME", "lasote")
    current_page = os.getenv("CONAN_CURRENT_PAGE", 1)
    total_pages = os.getenv("CONAN_TOTAL_PAGES", 1)
    gcc_versions = os.getenv("CONAN_GCC_VERSIONS", None)
    gcc_versions = gcc_versions.split(",") if gcc_versions else None
    
    builder = get_builder(username, channel)
    builder.docker_pack(current_page, total_pages, gcc_versions)
    
    if os.getenv("CONAN_UPLOAD", False) and os.getenv("CONAN_REFERENCE") and os.getenv("CONAN_PASSWORD"):
        reference = os.getenv("CONAN_REFERENCE")
        builder.upload_packages(reference, os.getenv("CONAN_PASSWORD"))