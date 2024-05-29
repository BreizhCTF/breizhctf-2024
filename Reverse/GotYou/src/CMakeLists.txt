cmake_minimum_required(VERSION 3.22)
project(GotYou C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-znow")
#set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-zlazy")
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -s")

add_executable(GotYou main.c)

add_custom_command(
        TARGET GotYou POST_BUILD
        COMMAND patchelf --set-rpath ./ ./GotYou && patchelf --set-interpreter ./ld-linux-x86-64.so.2 ./GotYou
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Patching ELF"
)
