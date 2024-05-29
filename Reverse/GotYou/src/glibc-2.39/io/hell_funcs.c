#include <hell_funcs.h>
#include <string.h>

uint32_t vals[4] = {0, 0, 0, 0};
bool checks[5] = {false, false, false, false, false};

void unk_func1(const char* first, const char* second, uint8_t val) {
    vals[0] *= (val+1)*7;
    vals[1] /= (val+1);
    vals[2] += val+3;
    vals[3] += val+4;
}

void unk_func2(int param, uint8_t val) {
    vals[0] += val+8;
    vals[1] += val+5;
    vals[2] *= (val+1)*3;
    vals[3] /= (val+1);
}

void unk_func3(const char* path, uint8_t val) {
    vals[0] /= (val+1);
    vals[1] += val+1;
    vals[2] += val+7;
    vals[3] *= (val+1)*5;
}

void unk_func4(int oldfd, uint8_t val) {
    vals[0] += val+2;
    vals[1] *= (val+1)*9;
    vals[2] /= (val+1);
    vals[3] += val+6;
}

void part_check(uint32_t idx, struct _IO_FILE* __stream) {
    if((idx+1)%4 != 0) return;
    switch(idx/4) {
        case 0:
            if(vals[0] == 387488 && vals[1] == 1844208 && vals[2] == 13 && vals[3] == 4661) checks[0] = true;
            break;
        case 1:
            if(vals[0] == 10448 && vals[1] == 7463745 && vals[2] == 1458 && vals[3] == 28) checks[1] = true;
            break;
        case 2:
            if(vals[0] == 6190 && vals[1] == 4218 && vals[2] == 701 && vals[3] == 4000) checks[2] = true;
            break;
        case 3:
            if(vals[0] == 3942 && vals[1] == 47313 && vals[2] == 63 && vals[3] == 2027) checks[3] = true;
            break;
        case 4:
            if(vals[0] == 857 && vals[1] == 3888 && vals[2] == 46 && vals[3] == 20741) checks[4] = true;
            break;
    }
    uint32_t new_vals[4] = {0, 0, 0, 0};
    memcpy(vals, new_vals, sizeof(new_vals));
}

bool check_valid(void) {
    return checks[0] == true && checks[1] == true && checks[2] == true && checks[3] == true && checks[4] == true;
}