#include <stdio.h>
#include <stdlib.h> 

int main()
{
  srand(0x1337);
  for(int i = 0; i<10; i++) 
    printf("%p, ", rand() % 256);
  return 0;
}
