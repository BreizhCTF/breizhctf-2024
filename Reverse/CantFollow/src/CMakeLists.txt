cmake_minimum_required(VERSION 3.22)
project(CantFollow C)

set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -s -g -O0")
set(CMAKE_C_STANDARD 17)

add_executable(CantFollow main.c)
