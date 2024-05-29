/*
 * Memory Tagging Extension (MTE) example for Linux
 *
 * Compile with gcc and use -march=armv8.5-a+memtag
 *    gcc mte-example.c -o mte-example -march=armv8.5-a+memtag
 *
 * Compilation should be done on a recent Arm Linux machine for the .h files to include MTE support.
 *
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/auxv.h>
#include <sys/mman.h>
#include <sys/prctl.h>

__attribute__((always_inline))
inline void* mte_tag(void* ptr, size_t len) {
  asm volatile ("irg %0, %0\n" : "+r"(ptr));
  void* end_ptr = ptr;
  for (size_t i = 0; i < len; i += 16) {
    asm volatile ("stg %0, [%0], #16\n" : "+r"(end_ptr));
  }
  return ptr;
}

void* _mte_tag(void* ptr, size_t len) {
  asm volatile ("irg %0, %0\n" : "+r"(ptr));
  void* end_ptr = ptr;
  for (size_t i = 0; i < len; i += 16) {
    asm volatile ("stg %0, [%0], #16\n" : "+r"(end_ptr));
  }
  return ptr;
}

// __attribute__((always_inline))
// inline void* mte_tag_and_zero(void* ptr, size_t len) {
//   asm volatile ("irg %0, %0\n" : "+r"(ptr));
//   void* end_ptr = ptr;
//   for (size_t i = 0; i < len; i += 16) {
//     asm volatile ("stzg %0, [%0], #16\n" : "+r"(end_ptr));
//   }
//   return ptr;
// }

__attribute__((always_inline))
inline void* mte_strip_tag(void* ptr) {
  return (uint64_t*)((uintptr_t)ptr & 0xfffffffffffffful);
}

uint16_t mte_get_tag(void* ptr) {
  return (uint16_t)( ((uintptr_t)ptr & 0xff00000000000000ul) >>56 );
}

unsigned char* secure_malloc(uint32_t size){
  unsigned char *ret = malloc(size);
  //printf("pointer is %p\n",ret);
  ret = _mte_tag(ret-16, size+16)+16;
  //printf("pointer is now %p\n", ret);
  return ret;
}

// void* secure_free(void *ptr, uint32_t size){
//   //printf("pointer to free : %p\n", ptr);
//   unsigned char *strip_ptr = mte_strip_tag(ptr);
//   unsigned char *new_ptr = _mte_tag(strip_ptr-16, size+16)+16;
//   //printf("pointer new tag : %p\n", new_ptr);
//   free(new_ptr);
// }

void* secure_free(void *ptr, uint32_t size){
  //printf("pointer to free : %p\n", ptr);
  unsigned char *strip_ptr = mte_strip_tag(ptr);
  uint16_t old_tag = mte_get_tag(ptr);
  unsigned char *new_ptr;
  //printf("old tag : 0x%x\n", old_tag);
  do {
    new_ptr = _mte_tag(strip_ptr-16, size+16)+16;
    //printf("new tag : 0x%x\n", mte_get_tag(new_ptr));
  } while(mte_get_tag(new_ptr) == old_tag);
  //printf("pointer new tag : %p\n", new_ptr);
  free(new_ptr);
}

typedef struct{
  size_t size;
  unsigned char* data;
} allocations;

uint32_t nb_alloc = 0;
#define MAX_SIZE 100
allocations allocations_array[MAX_SIZE];

void process(){
  uint16_t choice, index ;
  uint32_t length;
  int data;
    
  void *init = malloc(0x20);
  //printf("base_heap is %p\n", (long long)init & 0xfffffffffffff000);
  
  if(mprotect((long long)init & 0xfffffffffffff000, 0x0000000000021000, PROT_MTE | PROT_READ | PROT_WRITE)){
    perror("mprotect() failed");
    return  EXIT_FAILURE;
  };

  while (1) {
    puts("1. Alloc\n2. Free\n3. Edit\n4. Print\n5. Exit");
    scanf("%u",&choice);
    getchar();

    switch (choice) {
      case 1:
        if (nb_alloc < 1000){
          puts("index :");
          scanf("%u",&index);
          getchar();
          if (index < MAX_SIZE){
            puts("alloc size :");
            scanf("0x%x",&length);
            getchar();
            if (length <= 0x100 && length > 0){
              allocations_array[index].size = length;
              allocations_array[index].data = secure_malloc(length);
              puts("Data :");
              fgets(allocations_array[index].data,length-1,stdin);
              puts("Alloc done");
              nb_alloc += 1;
            } else {
              goto EXIT_LABEL;
            }
          } else {
            goto EXIT_LABEL;
          }
        }
        break;
      case 2:
        puts("index :");
        scanf("%u",&index);
        getchar();

        if (index < MAX_SIZE){
          if (allocations_array[index].size != 0 && allocations_array[index].data != 0){
            secure_free(allocations_array[index].data, allocations_array[index].size);
            puts("Free done");
          } else {
            goto EXIT_LABEL;
          }
        } else {
          goto EXIT_LABEL;
        }
        break;
      case 3:
        puts("index :");
        scanf("%u",&index);
        getchar();

        if (index < MAX_SIZE){
          if (allocations_array[index].size != 0 && allocations_array[index].data != 0){
            puts("New data :");
            fgets(allocations_array[index].data, allocations_array[index].size-1, stdin);
          } else {
            goto EXIT_LABEL;
          }
        } else {
          goto EXIT_LABEL;
        }
        break;
      case 4:
        puts("index :");
        scanf("%u",&index);
        getchar();

        if (index < MAX_SIZE){
          if (allocations_array[index].size != 0 && allocations_array[index].data != 0){
            printf("Data is : %s\n",allocations_array[index].data);
          } else {
            goto EXIT_LABEL;
          }
        } else {
          goto EXIT_LABEL;
        }
        break;
      case 5:
        goto EXIT_LABEL;
    }
  }

EXIT_LABEL:
  puts("Bye");

}

int main(void)
{
//    unsigned char *ptr;   // pointer to memory for MTE demonstration
   /*
     * Use the architecture dependent information about the processor
     * from getauxval() to check if MTE is available.
     */
    if (!((getauxval(AT_HWCAP2)) & HWCAP2_MTE))
    {
        printf("FAIL\n");
        return EXIT_FAILURE;
    }

    /*
     * Enable MTE with synchronous checking
     */
    if (prctl(PR_SET_TAGGED_ADDR_CTRL,
              PR_TAGGED_ADDR_ENABLE | PR_MTE_TCF_SYNC | (0xfffe << 3),
              0, 0, 0))
    {
            perror("prctl() failed");
            return EXIT_FAILURE;
    }
    
    setbuf(stdout, 0);
    process();
    return 0;
}