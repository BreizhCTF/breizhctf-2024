#include <unistd.h>
#include <stdio.h>
#include "file_decoder.h"

void decode_file(uint8_t input[8]) {
    if(access("flag.enc", F_OK) != -1) {
        FILE *enc_file = fopen("flag.enc", "r");
        FILE *dec_file = fopen("flag", "w");
        if (enc_file) {
            if(dec_file) {
                uint8_t bit_off = (input[0] >> 2) & 1;
                uint8_t input_i = 0;
                uint8_t buffer[1024];
                while (fread(buffer, sizeof(buffer), 1, enc_file)) {
                    for (uint32_t i = 0; i < sizeof(buffer) / 2; i++) {
                        uint32_t off = i * 2 + (uint32_t)bit_off;
                        uint8_t dec_byte = buffer[off] ^ input[input_i] ^ input[(input_i+1)%8];
                        fwrite(&dec_byte, 1, 1, dec_file);
                        input_i++;
                        if (input_i == 8) input_i = 0;
                    }
                }
                fclose(enc_file);
                fclose(dec_file);
                printf("Done !\n");
            } else printf("An error occurred when creating flag file...\n");
        } else printf("An error occurred when opening flag.enc...\n");
    } else printf("Couldn't find file flag.enc...\n");
}
