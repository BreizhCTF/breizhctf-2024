#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char cmd[20] = "date";
    char name[50];

    printf("Entrez votre nom : ");
    gets(name);

    printf("Bonjour, %s\n", name);
    printf("Votre nom a été stocké dans notre système à la date suivante :\n");
    system(cmd);

    return 0;
}
