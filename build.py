import os
import platform
import sys

if __name__ == "__main__":
    
    os.system('conan export lasote/stable')
    
    def test(settings):
        argv =  " ".join(sys.argv[1:])
        command = "conan test %s %s" % (settings, argv)
        retcode = os.system(command)
        if retcode != 0:
            exit("Error while executing:\n\t %s" % command)


    if platform.system() == "Windows":
        if len(sys.argv) != 2 or sys.argv[1] not in ["x86", "x86_64"]:
            print("Please, specify x86 or x86_64 as a parameter")
            exit()

        arch = sys.argv[1]
        print("Verify that you are running a %s visual console" % arch)
        raw_input("Press Enter to continue...")

        compiler = '-s compiler="Visual Studio" -s compiler.version=12 '
        # Static
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MDd -o OpenSSL:shared=False')
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MTd -o OpenSSL:shared=False')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MD -o OpenSSL:shared=False')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MT -o OpenSSL:shared=False')

        # Shared
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MDd -o OpenSSL:shared=True')
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MTd -o OpenSSL:shared=True')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MD -o OpenSSL:shared=True')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MT -o OpenSSL:shared=True')

    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        if not os.getenv("TRAVIS", False):   
            # Static x86
            test('-s arch=x86 -s build_type=Debug -o Boost:shared=False')
            test('-s arch=x86 -s build_type=Release -o Boost:shared=False')
    
            # Shared x86
            test('-s arch=x86 -s build_type=Debug -o Boost:shared=True')
            test('-s arch=x86 -s build_type=Release -o Boost:shared=True')

        # Static x86_64
        test('-s arch=x86_64 -s build_type=Debug -o Boost:shared=False')
        test('-s arch=x86_64 -s build_type=Release -o Boost:shared=False')

        # Shared x86_64
        test('-s arch=x86_64 -s build_type=Debug -o Boost:shared=True')
        test('-s arch=x86_64 -s build_type=Release -o Boost:shared=True')
        
    # HEADER ONLY
    test('-o Boost:header_only=True')    
