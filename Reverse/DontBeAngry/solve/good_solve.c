#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>


uint8_t SBOX[256] = {70, 90, 117, 178, 128, 155, 173, 39, 36, 16, 3, 25, 52, 32, 97, 250, 50, 154, 153, 198, 147, 195, 87, 161, 244, 201, 156, 34, 177, 22, 133, 76, 237, 143, 30, 206, 126, 47, 5, 182, 254, 179, 139, 91, 121, 236, 238, 205, 49, 246, 109, 152, 18, 241, 181, 176, 216, 56, 62, 89, 184, 220, 255, 99, 194, 129, 101, 226, 131, 0, 83, 191, 209, 55, 183, 187, 207, 145, 208, 165, 229, 130, 95, 196, 169, 23, 132, 168, 27, 240, 26, 61, 110, 164, 210, 29, 171, 1, 57, 221, 142, 14, 200, 118, 20, 217, 92, 252, 44, 67, 96, 84, 75, 215, 180, 175, 122, 81, 211, 107, 41, 115, 59, 48, 19, 218, 120, 112, 235, 149, 93, 162, 73, 219, 86, 69, 134, 35, 174, 78, 37, 223, 66, 160, 24, 197, 98, 43, 33, 203, 38, 199, 192, 111, 186, 40, 245, 108, 151, 71, 190, 100, 150, 88, 113, 72, 60, 85, 159, 82, 170, 230, 54, 212, 9, 185, 124, 253, 28, 2, 68, 225, 63, 7, 214, 10, 204, 58, 106, 188, 148, 146, 74, 4, 163, 189, 8, 224, 243, 15, 104, 119, 105, 102, 45, 53, 248, 166, 80, 103, 167, 123, 247, 127, 125, 251, 116, 249, 12, 13, 213, 138, 77, 11, 65, 114, 46, 21, 233, 234, 172, 228, 232, 31, 79, 193, 158, 136, 94, 135, 242, 157, 17, 202, 137, 140, 64, 144, 239, 6, 141, 222, 51, 227, 231, 42};
uint8_t SBOX_1[256];
uint8_t SBOX_2[256];
const uint32_t seed = 0x21011793;

void swap(uint8_t *a, uint8_t *b) {
    uint8_t tmp = *a;
    *a = *b;
    *b = tmp;
}

void shuffle_sbox() {
    for (uint8_t i = 256 - 1; i > 0; --i) {
        uint8_t j = rand() % (i + 1);
        swap(&SBOX[i], &SBOX[j]);
    }
}

void invert_input(uint8_t input[8]) {
    int start = 0;
    int end = 8 - 1;
    while (start < end) {
        swap(&input[start], &input[end]);
        start++;
        end--;
    }
}

void apply_sbox(uint8_t input[8]) {
    for(uint8_t i = 0; i < 8; i++) {
        input[i] = SBOX[input[i]];
    }
}

void mul_add(uint8_t input[8]) {
    uint8_t output[8];
    for(uint8_t i = 0; i < 8; i++) {
        output[i] = input[i] ^ input[((i + 1) % 8)];
    }
    memcpy(input, output, 8);
}

void add_round_output(uint8_t input[8], uint8_t output[8]) {
    for(uint8_t i = 0; i < 8; i++) {
        output[i] ^= input[i];
    }
}

void round(uint8_t input[8], uint8_t output[8]) {
    apply_sbox(input);
    mul_add(input);
    add_round_output(input, output);
}

void process_hash(uint8_t input[8]) {
    uint8_t output[8];
    memcpy(output, input, 8);
    for(uint8_t i = 0; i < 2; i++) {
        round(input, output);
    }
    memcpy(input, output, 8);
}


void extract_bits(uint64_t and_val, uint64_t res1, uint64_t or_val, uint64_t res2, uint64_t* bits, uint64_t* val) {
    *bits = 0;
    *val = 0;
    for(uint8_t i = 0; i < 64; i++) {
        *bits <<= 1;
        *val <<= 1;
        uint8_t and_bit = (and_val >> (63-i)) & 1;
        uint8_t res1_bit = (res1 >> (63-i)) & 1;
        if(and_bit) {
            if(res1_bit) *val |= 1;
            *bits |= 1;
        } else {
            uint8_t or_bit = (or_val >> (63-i)) & 1;
            uint8_t res2_bit = (res2 >> (63-i)) & 1;
            if(!or_bit) {
                if(res2_bit) *val |= 1;
                *bits |= 1;
            }
        }
    }
}

bool try_val(uint64_t val) {
    uint64_t val_cpy = val;
    process_hash(&val_cpy);
    if(val_cpy == 0x214dabee2f9cb469 || val_cpy == 0x89d1229b1ff58cc3) {
        memcpy(SBOX, SBOX_2, 256);
        val_cpy = val;
        invert_input(&val_cpy);
        process_hash(&val_cpy);
        memcpy(SBOX, SBOX_1, 256);
        if(val_cpy == 0xe261c6a49f5eed8a || val_cpy == 0x37b7f8273028c5c6) {
            
            return true;
        }
    }
    return false;
}

bool bruteforce(uint64_t bits, uint64_t val, uint8_t index) {
    if(index >= 64) return false;
    if(!((bits >> index) & 1)) {
        if(try_val(val | (1LL << index))) {
            val = val | (1LL << index);
            printf("Correct input: ");
            fwrite(&val, 1, 8, stdout);
            printf("\n");
            return true;
        }
        if(bruteforce(bits, val | (1LL << index), index+1)) return true;
    }
    return bruteforce(bits, val, index+1);
}

int main() {
    srand(seed);
    shuffle_sbox();
    memcpy(SBOX_1, SBOX, 256);
    shuffle_sbox();
    memcpy(SBOX_2, SBOX, 256);
    memcpy(SBOX, SBOX_1, 256);
    uint64_t bits, val;
    extract_bits(0x15de954d20b158aa, 0x1054014020201002, 0xee73dc6abbb6de9a, 0xee73fe7fffb6fedf, &bits, &val);
    bruteforce(bits, val, 0);
    extract_bits(0x15de954d20b158aa, 0x1054014020201002, 0xee73dc6abbb6de9a, 0xfe77fd7afffefedb, &bits, &val);
    bruteforce(bits, val, 0);
    extract_bits(0x15de954d20b158aa, 0x10004d20301002, 0xee73dc6abbb6de9a, 0xee73fe7fffb6fedf, &bits, &val);
    bruteforce(bits, val, 0);
    extract_bits(0x15de954d20b158aa, 0x10004d20301002, 0xee73dc6abbb6de9a, 0xfe77fd7afffefedb, &bits, &val);
    bruteforce(bits, val, 0);
    return 0;
}
