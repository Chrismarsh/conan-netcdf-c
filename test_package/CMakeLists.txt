cmake_minimum_required(VERSION 2.8.12)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

find_package(HDF5 REQUIRED)

add_executable(example simple_xy_wr.c)
target_link_libraries(example ${CONAN_LIBS} ${HDF5_C_LIBRARIES})
