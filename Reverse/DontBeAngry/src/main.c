#include <stdio.h>
#include <sys/time.h>
#include <sys/signal.h>
#include <string.h>
#include <stdint-gcc.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>
#include "custom_hash.h"
#include "file_decoder.h"

const uint32_t seed = 0x21011793;
bool ready = false;

void __attribute__((noinline)) swap(uint8_t *a, uint8_t *b) {
    uint8_t tmp = *a;
    *a = *b;
    *b = tmp;
}

void __attribute__((noinline)) shuffle_sbox() {
    for (uint8_t i = 256 - 1; i > 0; --i) {
        uint8_t j = rand() % (i + 1);
        swap(&SBOX[i], &SBOX[j]);
    }
}

void __attribute__((noinline)) invert_input(uint8_t input[8]) {
    int start = 0;
    int end = 8 - 1;
    while (start < end) {
        swap(&input[start], &input[end]);
        start++;
        end--;
    }
}


void __attribute__((noinline)) add_timer() {
    struct itimerval timer;
    timer.it_value.tv_sec = 0;
    timer.it_value.tv_usec = 900;
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 0;
    setitimer(ITIMER_REAL, &timer, NULL);
}

void __attribute__((noinline)) timer_handler(int signo) {
    if(ready) shuffle_sbox();
    add_timer();
}

void __attribute__((constructor)) premain() {
    srand(seed);
    signal(SIGALRM, timer_handler);
    add_timer();
}

int main(int argc, char** argv) {
    printf(" ------------ DontBeAngry v6.2.34 ------------\n"
           "|                                             |\n"
           "|        Sometimes, you must keep calm        |\n"
           "|                 by HellCorp                 |\n"
           "|                                             |\n"
           " ---------------------------------------------\n\n");
    printf("Password : ");
    uint8_t input[9], input_cpy[9];
    fgets(input, 9, stdin);
    if(argc >= 2 && !strcmp(argv[1], "--decrypt")) {
        printf("Decoding file...\n");
        decode_file(input);
        return 0;
    } else {
        if((*((uint64_t*)input) & 0x15de954d20b158aa) == 0x1054014020201002 || (*((uint64_t*)input) & 0x15de954d20b158aa) == 0x10004d20301002) {
            if((*((uint64_t*)input) | 0xee73dc6abbb6de9a) == 0xee73fe7fffb6fedf || (*((uint64_t*)input) | 0xee73dc6abbb6de9a) == 0xfe77fd7afffefedb) {
                ready = true;
                sleep(1);
                strcpy(input_cpy, input);
                invert_input(input_cpy);
                process_hash(input);
                if ((*(uint64_t *) input) == 0x214dabee2f9cb469 || (*((uint64_t *) input) == 0x89d1229b1ff58cc3)) {
                    sleep(1);
                    process_hash(input_cpy);
                    if ((*(uint64_t *) input_cpy) == 0xe261c6a49f5eed8a || (*((uint64_t *) input_cpy) == 0x37b7f8273028c5c6)) {
                        printf("Success !\n");
                        return 0;
                    }
                }
            }
        }
        printf("Failure...\n");
    }
    return 1;
}
