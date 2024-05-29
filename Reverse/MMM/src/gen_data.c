#include <stdlib.h>
#include <stdio.h>
#include <string.h>



int main()
{
  char flag[] = "BZHCTF{S33!";
  srand(0x1337);

  for(int i = 0; i<strlen(flag); i++) {
    printf("%p, ", rand() % 256);
  }

}
