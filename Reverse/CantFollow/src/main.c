#include <stdio.h>
#include <sys/ptrace.h>
#include <stdint-gcc.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>
#include <sys/wait.h>

uint8_t key_box[] = {19, 19, 225, 133, 35, 155, 32, 243, 36, 147, 246, 254, 190, 27, 205, 40, 32, 124, 181, 10, 87, 79, 155, 196, 126, 135, 218, 182, 142, 81, 156, 166, 46, 113, 222, 1, 103, 99, 202, 158, 7, 218, 107};
uint32_t mul_box[] = {5346, 6570, 12168, 13266, 9996, 15470, 11193, 10348, 11685, 25132, 9504, 9888, 21800, 6460, 12144, 1225, 6800, 3325, 23086, 3224, 5566, 1520, 27724, 11712, 3135, 24856, 11515, 21000, 9639, 1330, 25245, 7200, 7040, 580, 19608, 2352, 4214, 5700, 17544, 8575, 2640, 20587, 2750};
uint32_t and_box[] = {2, 18, 64, 1, 0, 2, 32, 48, 4, 3, 48, 48, 36, 27, 0, 32, 32, 92, 53, 0, 81, 79, 16, 0, 94, 0, 16, 36, 2, 81, 0, 32, 46, 112, 82, 0, 33, 67, 66, 16, 0, 82, 105};

uint64_t common_var;
uint8_t child_i = 0;

void child_func() {
    ptrace(PTRACE_TRACEME, NULL, NULL, NULL);
    while(true) {
        common_var *= (key_box[child_i] ^ common_var);
        __asm__("int3");
        child_i++;
    }
}

int main() {
    printf(" ------------ CantFollow v4.9.6 -------------\n"
           "|                                            |\n"
           "|            Don't lose control !            |\n"
           "|                by HellCorp                 |\n"
           "|                                            |\n"
           " --------------------------------------------\n\n");
    printf("Password: ");
    uint8_t input[44];
    size_t input_len;
    if(!fgets((char*)input, sizeof(input), stdin) || (input_len = strlen(input)) != 43) {
        printf("Failure...\n");
        return 0;
    }
    pid_t child_pid;
    if(!(child_pid = fork())) child_func();
    ptrace(PTRACE_ATTACH, child_pid, NULL, NULL);
    ptrace(PTRACE_CONT, child_pid, NULL, NULL);
    waitpid(child_pid, NULL, 0);
    for(uint8_t i = 0; i < input_len; i++) {
        ptrace(PTRACE_POKEDATA, child_pid, &common_var, input[i]);
        ptrace(PTRACE_CONT, child_pid, NULL, NULL);
        waitpid(child_pid, NULL, 0);
        common_var = ptrace(PTRACE_PEEKDATA, child_pid, &common_var, NULL) & 0xFFFFFFFF;
        if(common_var != mul_box[i] || (input[i] & key_box[i]) != and_box[i]) {
            printf("Failure...\n");
            return 1;
        }
    }
    printf("Success ! %s is your flag.\n", input);
    return 0;
}
