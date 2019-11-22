from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class NetcdfcConan(ConanFile):
    name = "netcdf-c"
    version = "4.6.2"
    license = "MIT"
    author = "Lars Bilke, lars.bilke@ufz.de"
    url = "https://github.com/bilke/conan-netcdf-c"
    description = "Unidata network Common Data Form"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
                "fPIC": [True, False],
                "netcdf_4": [True, False], 
                "dap": [True, False],
                "parallel4":[True,False]}
    default_options = "shared=False", "fPIC=True", "netcdf_4=True", "dap=False", "parallel4=False"
    generators = "cmake"

    def source(self):
        self.run("git clone --depth=1 --branch v{0} https://github.com/Unidata/netcdf-c.git".format(self.version))
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
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
            "FIND_PACKAGE(HDF5 NAMES ${SEARCH_PACKAGE_NAME} COMPONENTS C HL NO_MODULES REQUIRED ${NC_HDF5_LINK_TYPE})",
            '''set(HDF5_DIR ${CONAN_HDF5_ROOT}/cmake/hdf5)
      FIND_PACKAGE(HDF5 REQUIRED COMPONENTS C HL NO_MODULE)''')
        tools.replace_in_file("netcdf-c/liblib/CMakeLists.txt",
            "TARGET_LINK_LIBRARIES(netcdf ${TLL_LIBS})",
            "TARGET_LINK_LIBRARIES(netcdf ${TLL_LIBS} ${CONAN_LIBS})")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported right now")

    def requirements(self):
        if self.options.netcdf_4:
            self.requires("hdf5/1.10.5@CHM/dev")
        if self.options.dap:
            self.requires("libcurl/7.64.1@bincrafters/stable")

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["BUILD_UTILITIES"] = False
        cmake.definitions["ENABLE_NETCDF_4"] = self.options.netcdf_4
        cmake.definitions["ENABLE_DAP"] = self.options.dap
        cmake.definitions["ENABLE_PARALLEL4"] = self.options.parallel4
        cmake.configure(source_folder="netcdf-c")
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["netcdf"]

