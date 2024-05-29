#include <windows.h>
#include <stdio.h>

int main() {
    printf(" ------------- AllIsIn v21.12.05 -------------\n"
        "|                                             |\n"
        "|         No reason to look elsewhere         |\n"
        "|                 by HellCorp                 |\n"
        "|                                             |\n"
        " ---------------------------------------------\n\n");
    printf("Password: ");
    char input[39];
    if (!fgets(input, 39, stdin) || strlen(input) != 38) {
        printf("Failure...\n");
        return 1;
    }
    HMODULE hModule = GetModuleHandle(NULL);
    CHAR flag[39];
    if (LoadStringA(hModule, 101, flag, 39) != 38) {
        printf("Error...\n");
        return 1;
    }
    for (UINT8 i = 0; i < 38; i++) {
        if (input[i] != (char)(flag[i] + 5)) {
            printf("Failure...\n");
            return 1;
        }
    }
    printf("Success ! %s is your flag.\n", input);
    return 0;
}