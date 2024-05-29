#include <stdio.h>

int main() {
    FILE *file;
    char ch;

    file = fopen("/root/flag.txt", "r");

    if (file == NULL) {
        printf("Impossible d'ouvrir le fichier du flag, vous pouvez contacter un admin.\n");
        return 1;
    }
    while ((ch = fgetc(file)) != EOF) {
        printf("%c", ch);
    }
    fclose(file);
    return 0;
}
