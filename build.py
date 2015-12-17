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

        for compiler_version in ("14", "12"):
            compiler = '-s compiler="Visual Studio" -s compiler.version=%s ' % compiler_version
            
            # Shared
            test(compiler + '-s arch=x86 -s build_type=Debug -s compiler.runtime=MDd -o Boost:shared=True')
            test(compiler + '-s arch=x86 -s build_type=Release -s compiler.runtime=MD -o Boost:shared=True')
            test(compiler + '-s arch=x86_64 -s build_type=Debug -s compiler.runtime=MDd -o Boost:shared=True')
            test(compiler + '-s arch=x86_64 -s build_type=Release -s compiler.runtime=MD -o Boost:shared=True')

            
            # Static
            test(compiler + '-s arch=x86_64 -s build_type=Release -s compiler.runtime=MT -o Boost:shared=False')
            test(compiler + '-s arch=x86_64 -s build_type=Debug -s compiler.runtime=MTd -o Boost:shared=False')
            test(compiler + '-s arch=x86_64 -s build_type=Debug -s compiler.runtime=MDd -o Boost:shared=False')
            test(compiler + '-s arch=x86_64 -s build_type=Release -s compiler.runtime=MD -o Boost:shared=False')
            
            
            test(compiler + '-s arch=x86 -s build_type=Debug -s compiler.runtime=MDd -o Boost:shared=False')
            test(compiler + '-s arch=x86 -s build_type=Debug -s compiler.runtime=MTd -o Boost:shared=False')
            test(compiler + '-s arch=x86 -s build_type=Release -s compiler.runtime=MD -o Boost:shared=False')
            test(compiler + '-s arch=x86 -s build_type=Release -s compiler.runtime=MT -o Boost:shared=False')

            
    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)

        # Shared x86_64
        test('-s arch=x86_64 -s build_type=Debug -o Boost:shared=True')
        test('-s arch=x86_64 -s build_type=Release -o Boost:shared=True')
        
        if not platform.system() == "Darwin" and not os.getenv("TRAVIS", False):   
            # Shared x86
            test('-s arch=x86 -s build_type=Debug -o Boost:shared=True')
            test('-s arch=x86 -s build_type=Release -o Boost:shared=True')
            
            # Static x86
            test('-s arch=x86 -s build_type=Debug -o Boost:shared=False')
            test('-s arch=x86 -s build_type=Release -o Boost:shared=False')
       
	    # Static x86_64
        test('-s arch=x86_64 -s build_type=Debug -o Boost:shared=False')
        test('-s arch=x86_64 -s build_type=Release -o Boost:shared=False')



            
        # HEADER ONLY
        test('-o Boost:header_only=True')
