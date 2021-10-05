/*
 * EXPLICIT FREE LIST ALLOCATOR *
-------------------------------------
* Every block of memory has an 8-byte header which contains the size of the block.
* If a block is free the least significant bit of the size is set to 1. That is why
* a free block size is refrenced as (*block_ptr - 1). The first 16 bytes of free blocks 
* contain pointers to the next and brevious free blocks. 
*/

#include <stdio.h>
#include <string.h>
#include "./allocator.h"
#include "./debug_break.h"

#define HEADER_SIZE 8

static unsigned long *segment_start;  // Start of heap segment
static size_t segment_size;  // Size of heap segment
static size_t nused;  // Number of bytes used
static int nblocks;  // Number of blocks that the segment is divided into
static int nfree_blocks;  // Number of free blocks
static unsigned long *first_free_block;  // The first free blocl of the segment

// First 16 bytes of payload of free blocks.
typedef struct payload {
    unsigned long *next_free;  // Pointer to the next free block.
    unsigned long *previous_free;  // Pointer to the previous free block.
} payload;

// Rounds up the given number to the given multiple which must be a power of 2.
size_t roundup(size_t sz, size_t mult) {
    return (sz + mult - 1) & ~(mult - 1);
}

// Creates a new free block at the specified block_start location.
void make_new_free_header(unsigned long *block_start, size_t block_size,
                          unsigned long *next_free_block, unsigned long *previous_free_block) {
    block_size += 1;  // Set least significant bit to 1.
    memcpy(block_start, &block_size, HEADER_SIZE);
    payload free_blocks = {next_free_block, previous_free_block};
    memcpy(block_start + 1, &free_blocks, sizeof(payload));
    nblocks += 1;
    nfree_blocks += 1;
    nused += HEADER_SIZE + sizeof(payload);
}

// Changes a free header to a used one with the specified new size.
void make_used_header(unsigned long *block_start, size_t block_size) {
    *block_start = block_size;
    nused -= sizeof(payload);
    nused += block_size;
    nfree_blocks--;
}

/* Adds padding to the end of a block if the space is not enough
 * to create a new free block.
*/
void add_padding(unsigned long *block_start, size_t padding) {
    *block_start += padding;
    nused += padding;
}

/* This function merges two free blocks. The one pointed to by 
 * first_block and the one to the right of first_block. It also does
 * some rewiring but it is not enough. add_to_list completes the rewiring.
*/
void merge_blocks(unsigned long *first_block) {
    unsigned long *block_to_the_right = first_block + ((*first_block + HEADER_SIZE) / 8);
    if (block_to_the_right == first_free_block) {
        first_free_block = first_block;
    }
    *first_block += (*block_to_the_right + HEADER_SIZE);
    nblocks--;
    nfree_blocks--;
}

/* This function iterates through all blocks until
 * it finds the first free block.
*/
unsigned long * find_first_free() {
    if (nblocks == 1) {
        return segment_start;
    }
    unsigned long *position = segment_start;
    while (*position % ALIGNMENT == 0) {  // while block is used
        position += (*position + HEADER_SIZE) / 8;
    }
    return position;
}

/* This function finds the previous free block of the block
 * pointed to by ptr. It assumes that the block pointed to
 * by ptr is not free and it iterated through free blocks
 * until it finds the block that is previous to ptr. That
 * is why the block passed into add_to_list must pretend that
 * it is not free.
*/
unsigned long *find_previous_free(unsigned long *ptr) {
    *ptr += 1;
    unsigned long *first = find_first_free();
    *ptr -= 1;
    if (first >= ptr) {
        return NULL;
    }
    for (int i = 0; i < (nfree_blocks - 2); i++) {
        if ((unsigned long *)(*(first + 1)) > ptr) {
            return first;
        }
        if (*((unsigned long *)(*(first + 1))) % ALIGNMENT == 0) {
            return first;
        }
        first = (unsigned long *)(*(first + 1));
    }
    return first;
}

/* This function rewires the list when a new free block pointed
 * to by ptr is added so that the next_free and previous_free 
 * pointers of free blocks are correct. The next_free_block is 
 * determined by stepping throught the blocks and finding the next 
 * free block. The previous free block is found using a helper function.
*/
void add_to_list(unsigned long *ptr) {
    unsigned long *next_free_block = NULL;
    unsigned long *previous_free_block = NULL;
    unsigned long *position = ptr;
    while (*position % ALIGNMENT == 0) {  // While position is used.
        position += (*position + HEADER_SIZE) / 8;
        // If it reached the end.
        if (position >= (segment_start + (segment_size / 8))) {
            break;
        }
    }
    // If not at the end.
    if (position < (segment_start + (segment_size / 8))) {
        if (*position % ALIGNMENT != 0) {
            next_free_block = position;   
        }
    }
    
    if (nfree_blocks == 1) {
        previous_free_block = NULL;
    } else {
        previous_free_block = find_previous_free(ptr);
    }
    
    payload free_blocks = {next_free_block, previous_free_block};
    memcpy(ptr + 1, &free_blocks, sizeof(payload));
    if (next_free_block != NULL) {
        *(next_free_block + 2) = (unsigned long)ptr;
    }
    if (previous_free_block != NULL) {
        *(previous_free_block + 1) = (unsigned long)ptr;
    }
}

/* This function initializes global variables based on the specified
 * boundary parameters. It also adds the first header signifying the
 * entire heap segment as a free block of size heap_size.
*/
bool myinit(void *heap_start, size_t heap_size) {
    if (heap_size < (HEADER_SIZE + sizeof(payload))) {
        return false;
    }
    segment_start = (unsigned long *)heap_start;
    segment_size = heap_size;
    nused = 0;
    nblocks = 0;
    nfree_blocks = 0;
    make_new_free_header(segment_start, segment_size - HEADER_SIZE, NULL, NULL);
    first_free_block = segment_start;
    return true;
}

/* This function satisfies an allocation request by finding the smallest free
 * block of memory that is greater than or equal to the requested size by geting
 * the first free block and going to the next free blocks directly through the 
 * pointers in th payloads of the free blocks. 
 * If the best block found is larger than the needed size, a new free block is
 * created right after the allocated block to fill the extra space.
*/
void *mymalloc(size_t requested_size) {
    if (requested_size == 0 || requested_size > MAX_REQUEST_SIZE) {
         return NULL;
     }
     size_t needed = roundup(requested_size, ALIGNMENT);
     if (needed < sizeof(payload)) {
         needed = sizeof(payload);
     }
     if ((needed + nused + HEADER_SIZE) > segment_size) {
         return NULL;
     }
     unsigned long *position = first_free_block;
     unsigned long *best_position = NULL;
     for (int i = 0; i < nfree_blocks; i++) {
         if ((*position - 1) >= needed) {
             if (best_position == NULL) {
                 best_position = position;
             } else {
                 // If size of block is smaller than the best block, current block becomes best block.
                 best_position = (*position - 1) < (*best_position - 1) ? position : best_position;
             } 
         }
         position = (unsigned long *)(*(position + 1));  // Go to next free block.
     }
     if (best_position == NULL) {
         return NULL;
     }
     unsigned long *next_free_block = (unsigned long *)(*(best_position + 1));
     unsigned long *previous_free_block = (unsigned long *)(*(best_position + 2));
     size_t previous_block_size = (*best_position - 1);
     make_used_header(best_position, needed);
     // If there is enough space to split the block and create a new free block.
     if ((previous_block_size - needed) >= (sizeof(payload) + HEADER_SIZE)) {
         make_new_free_header(best_position + ((*best_position + HEADER_SIZE) / 8),
                              previous_block_size - (*best_position + HEADER_SIZE),
                              next_free_block, previous_free_block);
         unsigned long * new_free_block = best_position + ((*best_position + HEADER_SIZE) / 8);
         *new_free_block -= 1;  // Pass it in to add_to_list as used.
         add_to_list(new_free_block);
         *new_free_block += 1;  // Make it free again.
         if (*first_free_block % ALIGNMENT == 0) {
             first_free_block = new_free_block;
         }
     } else {  // rewire list
         if (needed != previous_block_size) {
             add_padding(best_position, previous_block_size - needed);
         }
         if (previous_free_block != NULL) {
             position = previous_free_block;
             // previous free blocks next becomes next_free_block
             *(position + 1) = (unsigned long)next_free_block;
         }
         if (next_free_block != NULL) {
             position = next_free_block;
             // next free blocks previous becomes previous_free_block
             *(position + 2) = (unsigned long)previous_free_block;  
         }
         first_free_block = find_first_free();
     }
     return best_position + 1;
}

/* This function frees a block of memory that is pointed to by ptr.
 * It also checks if the block next to the new free block is free 
 * and if it is they are merged.
*/
void myfree(void *ptr) {
    if (ptr == NULL) {
        return;
    }
    unsigned long *block = (unsigned long *)ptr;
    block--;  // access the header
    nused -= *block;
    nfree_blocks++;
    unsigned long *block_to_the_right = block + ((*block + HEADER_SIZE) / 8);
    if (*block_to_the_right % ALIGNMENT != 0) {  // If blocktotheright is free.
        merge_blocks(block);
        *block -= 1;
    }
    add_to_list(block);
    *block += 1;
    if (block < first_free_block) {
        first_free_block = block;
    }
}

/* This function satisfies requests for resizing previously-allocated memory
 * by first freeing that block of memory and then allocating a new block by
 * calling mymalloc. It then moves the payload data over to the new block.
 * It also checks if the block next to the block being resized is free and
 * if it is they merge. As a result it can support in-place realloc.
*/
void *myrealloc(void *old_ptr, size_t new_size) {
    if (old_ptr == NULL) {
        return mymalloc(new_size);
    }
    if (old_ptr != NULL && new_size == 0) {
        myfree(old_ptr);
        return NULL;
    }
    unsigned long *ptr = (unsigned long *)old_ptr;
    unsigned long payload_data_1 = *ptr;
    unsigned long payload_data_2 = *(ptr + 1);
    myfree(old_ptr);
    ptr -= 1;  // access the header.
    // If it is not the last block.
    if ((char *)ptr + (*ptr + HEADER_SIZE - 1) != (char *)segment_start + segment_size) {
        unsigned long *ptr_to_the_right = ptr + ((*ptr + HEADER_SIZE - 1) / 8);
        while (*ptr_to_the_right % ALIGNMENT != 0) {  // while ptrtotheright is free.
            *ptr -= 1;  // Pass ptr to mrege_blocks as used.
            merge_blocks(ptr);
            *ptr -= 1;  // Pass ptr to add_to_list as used.
            add_to_list(ptr);
            *ptr += 1;  // Make ptr free.
            // If ptr is the last block.
            if ((char *)ptr + (*ptr + HEADER_SIZE - 1) == (char *)segment_start + segment_size) {
                break;
            }
            ptr_to_the_right = ptr + ((*ptr + HEADER_SIZE - 1) / 8);
        } 
    }
    
    unsigned long *new_ptr = mymalloc(new_size);
    if (new_ptr == NULL) {
        return NULL;
    }
    memmove(new_ptr, old_ptr, new_size);
    *new_ptr = payload_data_1;
    *(new_ptr + 1) = payload_data_2;
    return new_ptr;
}

/* This function checks for potential errors/inconsistencies in the heap data
 * structures and returns false if there were issues, or true otherwise.
*/
bool validate_heap() {
    int count_free = 0;
    // If alocator used more space than available.
    if (nused > segment_size) {
        breakpoint();
        return false;
    }
    // Iterate by each block and if the difference in adresses is not a multiple of 8, return false.
    unsigned long *cur = segment_start;
    unsigned long *previous_cur = cur;
    // By iterating this way if the size of a block is unresonable, there will be a segmentation fault.
    for (int i = 0; i < nblocks; i++) {
        if (*cur % ALIGNMENT == 0) {  // If block is used.
            previous_cur = cur;
            cur += (*cur + HEADER_SIZE) / 8;
            if (((char *)cur - (char *)previous_cur) % ALIGNMENT != 0) {
                breakpoint();
                return false;
            }
        } else {  // If block is free.
            previous_cur = cur;
            count_free++;
            cur += ((*cur - 1) + HEADER_SIZE) / 8;
            if (((char *)cur - (char *)previous_cur) % ALIGNMENT != 0) {
                breakpoint();
                return false;
           }
        }
    }
    // If the number of free blocks does not match nfree_blocks return false.
    if (count_free != nfree_blocks) {
        return false;
    }
    return true;
}

/* This function is for debugging purposes.
 * It iterates through each block and prints the information in the headers
 * and if a block is free it also prints the next free block and previous 
 * free block.
*/
void dump_heap() {
    printf("Heap segment starts at address %p, ends at %p. %lu bytes currently used. %d blocks\n", 
           segment_start, (char *)segment_start + segment_size, nused, nblocks);
    unsigned long *cur = segment_start;
    for (int i = 0; i < nblocks; i++) {
        if (*cur % ALIGNMENT == 0) {  // Used block
            printf("%p: %ld bytes, used\n", cur, *cur);
            cur += (*cur + HEADER_SIZE) / 8;
        } else {  // Free block
            printf("%p: %ld bytes, free. next_free: %ld, previous_free: %ld\n",
                   cur, (*cur - 1), *(cur + 1), *(cur + 2));
            cur += ((*cur - 1) + HEADER_SIZE) / 8;
        }
    }
}

