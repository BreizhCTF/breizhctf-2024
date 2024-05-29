cmake_minimum_required(VERSION 3.22)
project(DontBeAngry C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -s -g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -s -g -O0")

add_executable(DontBeAngry main.c custom_hash.h custom_hash.c file_decoder.h file_decoder.c)
