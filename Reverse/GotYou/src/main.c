#include <stdio.h>
#include <stdint-gcc.h>
#include <string.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <malloc.h>
#include <sys/stat.h>
#include <unistd.h>
#include <wchar.h>
#include <stdbool.h>

uint64_t base_addr = 0;
uint64_t ld_base_addr = 0;
uint64_t got_addr = 0;
uint64_t plt_addr = 0;
uint64_t rela_plt_addr = 0;
uint64_t dynstr_addr = 0;
uint64_t dynsym_addr = 0;

void __attribute__ ((constructor)) find_sec_addresses() {
    uint64_t rip;
    __asm__ __volatile__ (
        "call 1f\n"
        "1: pop %0"
        : "=r" (rip)
    );
    base_addr = ((rip-0x1000) >> 12) << 12;
    uint64_t program_headers_addr = base_addr+0x40;
    uint64_t dyn_header_addr = 0;
    while(!dyn_header_addr) {
        uint32_t type = *((uint32_t*) program_headers_addr);
        if(type == 2) dyn_header_addr = program_headers_addr;
        program_headers_addr += 0x38;
    }
    uint64_t dyn_addr = base_addr + *((uint64_t*)(dyn_header_addr + 0x10));
    plt_addr = base_addr + 0x1020;
    while(!got_addr || !rela_plt_addr || !dynstr_addr || !dynsym_addr) {
        uint64_t d_tag = *(uint64_t*) dyn_addr;
        uint64_t d_val = *((uint64_t*)(dyn_addr + 0x8));
        switch(d_tag) {
            case 3:
                got_addr = d_val;
                break;
            case 5:
                dynstr_addr = d_val;
                break;
            case 6:
                dynsym_addr = d_val;
                break;
            case 0x17:
                rela_plt_addr = d_val;
                break;
        }
        dyn_addr += 0x10;
    }
}

uint64_t find_func_got_addr(char* func_name) {
    char* dyn_str_string = (char*)dynstr_addr;
    while(strcmp(dyn_str_string, func_name)) {
        dyn_str_string += strlen(dyn_str_string) + 1;
    }
    uint32_t string_off = (uint64_t)dyn_str_string - dynstr_addr;
    uint64_t dyn_sym_entry = dynsym_addr;
    while(*(uint32_t*)dyn_sym_entry != string_off) dyn_sym_entry += 0x18;
    uint32_t dyn_sym_idx = (dyn_sym_entry - dynsym_addr) / 0x18;
    uint64_t rela_plt_entry = rela_plt_addr;
    while((*((uint64_t*)(rela_plt_entry+8)) >> 32) != dyn_sym_idx) rela_plt_entry += 0x18;
    uint64_t func_got_addr = base_addr+*(uint64_t*)rela_plt_entry;
    return func_got_addr;
}

void reset_got_func_val(char* func_name) {
    uint64_t func_got_addr = find_func_got_addr(func_name);
    uint64_t got_page = (got_addr >> 12) << 12;
    mprotect((void*)got_page, 0x8, 6);
    *(uint64_t*)(got_addr+0x8) = ld_base_addr + 0x35310;
    *(uint64_t*)(got_addr+0x10) = ld_base_addr + 0x126f0;
    *(uint64_t*)func_got_addr = ((func_got_addr-got_addr-0x8-0x10)/8)*0x10+plt_addr+0x10;
    mprotect((void*)got_page, 0x8, 2);
}

void find_ld_base_addr() {
    uint64_t puts_got_addr = find_func_got_addr("mprotect");
    uint64_t mprotect_libc_addr = *(uint64_t*) puts_got_addr;
    uint64_t libc_addr = mprotect_libc_addr - 0xf9cc0;
    uint64_t ld_got_addr = libc_addr + 0x1d0010;
    uint64_t ld_addr = *(uint64_t*) ld_got_addr;
    ld_base_addr = ld_addr - 0x126f0;
}

int main() {
    find_ld_base_addr();
    printf(" -------------- GotYou v14.5.10 --------------\n"
           "|                                             |\n"
           "|        Now you see me, now you don't        |\n"
           "|                 by HellCorp                 |\n"
           "|                                             |\n"
           " ---------------------------------------------\n\n");
    printf("Password: ");
    char input[21];
    if(fgets(input, sizeof(input), stdin) <= 0 || strlen(input) != 20) {
        printf("Failure...\n");
        return 0;
    }
    uint8_t input_len = strlen(input);
    input[input_len] = 0;
    uint64_t res = 0;
    bool reset_func = true;
    for(uint8_t i = 0; i < input_len; i++) {
        uint8_t func_idx = input[i] >> 4;
        uint8_t val = input[i] & 0xF;
        if(reset_func) {
            switch (func_idx) {
                case 3: {
                    reset_got_func_val("strncmp");
                    break;
                }
                case 5: {
                    reset_got_func_val("mallopt");
                    break;
                }
                case 6: {
                    reset_got_func_val("chmod");
                    break;
                }
                case 7: {
                    reset_got_func_val("dup2");
                    break;
                }
                default:
                    printf("Failure...\n");
                    return 0;
            }
        }
        int r1 = rand(), r2 = rand();
        res |= strncmp(&r1, &r2, val);
        res |= mallopt(r1, val);
        res |= chmod(&res, val);
        res |= dup2(r1, val);
        res |= ungetc(i, &r1);
        reset_func = i != input_len-1 && func_idx != (input[i+1] >> 4);
        if(reset_func) {
            switch (func_idx) {
                case 3: {
                    reset_got_func_val("strncmp");
                    break;
                }
                case 5: {
                    reset_got_func_val("mallopt");
                    break;
                }
                case 6: {
                    reset_got_func_val("chmod");
                    break;
                }
                case 7: {
                    reset_got_func_val("dup2");
                    break;
                }
                default:
                    printf("Failure...\n");
                    return 0;
            }
        }
    }
    res = getwchar();
    if(res) printf("Congratulations ! Your flag is BZHCTF{%s}\n", input);
    else printf("Failure...\n");
    return 0;
}