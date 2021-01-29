from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

class NetcdfcConan(ConanFile):
    name = "netcdf-c"
    license = "MIT"
    url = "https://github.com/Chrismarsh/conan-netcdf-c"
    description = "Unidata network Common Data Form"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
                "fPIC": [True, False],
                "netcdf_4": [True, False],
                "dap": [True, False],
                "parallel4":[True,False]}
    default_options = "shared=True", "fPIC=True", "netcdf_4=True", "dap=False", "parallel4=False"
    generators = "cmake"

    source_subfolder = 'netcdf-c'

    def source(self):

        tools.get(**self.conan_data["sources"][self.version])

        os.rename("netcdf-c-{0}".format(self.version), self.source_subfolder)
   
        #under macos, we need the install_name to remain with an  @rpath dir prefix. On linux, we don't need that
        if tools.os_info.is_macos:
            tools.replace_in_file("netcdf-c/CMakeLists.txt", "project(netCDF C)",
                                  '''project(netCDF C)
                                    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                    conan_basic_setup(KEEP_RPATHS)''')
        else:
            tools.replace_in_file("netcdf-c/CMakeLists.txt", "project(netCDF C)",
                                  '''project(netCDF C)
                                    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                    conan_basic_setup()''')

        # Fix overwriting of CMAKE_MODULE_PATH set by Conan
        tools.replace_in_file("netcdf-c/CMakeLists.txt",
            "SET(CMAKE_MODULE_PATH",
            "SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}")
        
        # Fix usage of custom FindHDF5.cmake in hdf5 package
        # Also: Fix NO_MODULES to NO_MODULE, removed link type
        tools.replace_in_file("netcdf-c/CMakeLists.txt",
            "FIND_PACKAGE(HDF5 COMPONENTS C HL REQUIRED)",
            '''set(HDF5_DIR ${CONAN_HDF5_ROOT}/cmake/hdf5)
      FIND_PACKAGE(HDF5 COMPONENTS C HL REQUIRED)''')

        tools.replace_in_file("netcdf-c/liblib/CMakeLists.txt",
            "TARGET_LINK_LIBRARIES(netcdf ${TLL_LIBS})",
            "TARGET_LINK_LIBRARIES(netcdf ${TLL_LIBS} ${CONAN_LIBS})")

      
    def requirements(self):
        if self.options.netcdf_4:
            self.requires("hdf5/[>=1.12]@CHM/stable")
        if self.options.dap:
            self.requires("libcurl/[>=7.64]@bincrafters/stable")

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["BUILD_UTILITIES"] = False
        cmake.definitions["ENABLE_NETCDF_4"] = self.options.netcdf_4
        cmake.definitions["ENABLE_DAP"] = self.options.dap
        cmake.definitions["ENABLE_PARALLEL4"] = self.options.parallel4

        if tools.os_info.is_macos:
            cmake.definitions["CMAKE_INSTALL_NAME_DIR"] = '@rpath' #self.package_folder+'/lib'

        cmake.configure(source_folder="netcdf-c")
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

        # if tools.os_info.is_linux:
        #     with tools.chdir(self.package_folder):
        #         cmd = "patchelf --remove-rpath lib/libnetcdf.so"
        #         os.system(cmd)

    def package_info(self):
        self.cpp_info.libs = ["netcdf"]
