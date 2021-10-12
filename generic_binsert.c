/* Contains generic binsert function which does binary search on an array and if the element is
 * not found it is inserted at the correct index.
*/
#include <string.h>
#include "samples/prototypes.h"

// Does binary search and if element is not found it is inserted at the correc position.
void *binsert(const void *key, void *base, size_t *p_nelem, size_t width,
              int (*compar)(const void *, const void *)) {
    void *temp = base;
    for (size_t nremain = *p_nelem; nremain != 0; nremain >>= 1) {
        void *p = (char *)base + (nremain >> 1) * width;
        int sign = compar(key, p);
        if (sign == 0) {
            return p;
        }
        if (sign > 0) {  /* key > p: move right */
            base = (char *)p + width;
            nremain--;
        }  /* else move left */
    }
    // How many bytes to move in memmove.
    size_t size_to_move = (width * (*p_nelem)) - ((char *)base - (char *)temp);
    // Move the entire array after the base over by one position.
    memmove((char *)base + width, (char *)base, size_to_move);
    // Insert the key at the  base.
    memcpy(base, key, width);
    (*p_nelem)++;
    return base;   
}
