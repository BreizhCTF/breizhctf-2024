cmake_minimum_required(VERSION 3.22)
project(NanoGunner)

find_package(PkgConfig REQUIRED)
pkg_check_modules(gtkmm REQUIRED IMPORTED_TARGET gtkmm-3.0 glibmm-2.4 )

set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -s -g -O0")
set(CMAKE_CXX_STANDARD 17)

add_executable(NanoGunner main.cpp main.h vm.cpp vm.h)

target_link_libraries(NanoGunner PRIVATE PkgConfig::gtkmm)
