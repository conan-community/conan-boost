import os
import platform
import sys

############### CONFIGURE THESE VALUES ##################
default_username = "lasote"
default_channel = "testing"
#########################################################

conan_username = os.getenv("CONAN_USERNAME", default_username)
conan_channel = os.getenv("CONAN_CHANNEL", default_channel if not os.getenv("TRAVIS", False) else "travis")
conan_password = os.getenv("CONAN_PASSWORD", None)
conan_upload = os.getenv("CONAN_UPLOAD", False)
conan_reference = os.getenv("CONAN_REFERENCE", False) 

if __name__ == "__main__":

    if len(sys.argv)==2:
         versions = [sys.argv[1]]
    else:
         versions = ["4.6", "4.8", "4.9", "5.2", "5.3"]
        
    for gcc_version in versions:
        # Do not change this "lasote" name is the dockerhub image, its a generic image
        # for build c/c++ with docker and gcc
        image_name = "lasote/conangcc%s" % gcc_version.replace(".", "")
        if not os.path.exists(os.path.expanduser("~/.conan/data")): # Maybe for travis
            os.system("sudo mkdir ~/.conan/data && sudo chmod -R 777 ~/.conan/data")
        os.system("sudo docker pull %s" % image_name)
        curdir = os.path.abspath(os.path.curdir)
        env_vars = '-e CONAN_USERNAME=%s -e CONAN_CHANNEL=%s' % (conan_username, conan_channel) 
        command = 'sudo docker run --rm -v %s:/home/conan/project -v '\
                  '~/.conan/data:/home/conan/.conan/data -it %s %s /bin/sh -c '\
                  '"cd project && sudo pip install conan==0.0.1rc3 --upgrade && python build.py"' % (curdir, env_vars, image_name)
        ret = os.system(command)
        if ret != 0:
            exit("Error building")
      
    if conan_upload and conan_password:  
        os.system("conan user %s -p %s" % (conan_username, conan_password))
        ret = os.system("conan upload %s/%s/%s --all --force" % (conan_reference, conan_username, conan_channel))
        if ret != 0:
            exit("Error uploading")
