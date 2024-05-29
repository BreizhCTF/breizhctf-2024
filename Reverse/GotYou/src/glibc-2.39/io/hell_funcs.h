#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

extern void unk_func1(const char* first, const char* second, uint8_t val);
extern void unk_func2(int param, uint8_t val);
extern void unk_func3(const char* path, uint8_t val);
extern void unk_func4(int oldfd, uint8_t val);
extern void part_check(uint32_t idx, struct _IO_FILE* __stream);
extern bool check_valid(void);