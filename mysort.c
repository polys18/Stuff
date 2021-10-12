/* This program prints out the contents of a file (or standard input) in sorted order.
 * It sorts alphabetiacally by default. If invoked with the -l flag it sorts by increasing 
 * length. If invoked with the -n flag it sorts by string numerical value. if invoked with
 * the -r flag the order is reversed and if it is invoked with the -u flag, it disgards 
 * duplicate lines.
*/
#include <assert.h>
#include <errno.h>
#include <error.h>
#include <getopt.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "samples/prototypes.h"
#define MAX_LINE_LEN 4096
#define MIN_NLINES 100

typedef int (*cmp_fn_t)(const void *p, const void *q);

// Compares alphabetically.
int cmp_pstr(const void *p, const void *q) {
    char *str_p = *(char **)p;
    char *str_q = *(char **)q;
    return strcmp(str_p, str_q);
}

// Compares by length.
int cmp_pstr_len(const void *p, const void *q) {
    char *str_p = *(char **)p;
    char *str_q = *(char **)q;
    return strlen(str_p) - strlen(str_q);
}

// Compares by string numerical value.
int cmp_pstr_numeric(const void *p, const void *q) {
    char *str_p = *(char **)p;
    char *str_q = *(char **)q;
    return atoi(str_p) - atoi(str_q);
}

// Reads lines from the file and puts them in a sorted array which is then printed.
void sort_lines(FILE *fp, cmp_fn_t cmp, bool uniq, bool reverse) {
    char **lines = malloc(MIN_NLINES * sizeof(char *));
    assert(lines != NULL);
    size_t lines_size = 0;
    int realloc_index = 1;
    while (1) {
        if (lines_size == (MIN_NLINES * realloc_index)) {  // If array fills up.
            lines = realloc(lines, (lines_size * 2) * sizeof(char *));
            assert(lines != NULL);
            realloc_index *= 2;
        }
        char buf[MAX_LINE_LEN];
        char *s = fgets(buf, MAX_LINE_LEN, fp);
        if (s == NULL) {
            break;
        }
        if (uniq == true) {
            int temp = lines_size;
            char **added = binsert(&s, lines, &lines_size, sizeof(char *), cmp);
            if (temp != lines_size) {
                char *line = strdup(s);
                assert(line != NULL);
                // Substitute stack allocated string in the array with heap applocted string.
                *added = line;
            }
        } else {
            char *line = strdup(s);
            assert(s != NULL);
            lines[lines_size] = line;
            lines_size++;
        }
    }
    qsort(lines, lines_size, sizeof(char *), cmp);
    if (reverse == true) {
        for (int i = lines_size - 1; i >= 0; i--) {
            printf("%s\n", lines[i]);
            free(lines[i]);
        }
       
    } else {
        for (int i = 0; i < lines_size; i++) {
            printf("%s\n", lines[i]);
            free(lines[i]);
        }
    }
    free(lines);
}

// Process command line arguments and call sort_lines.
int main(int argc, char *argv[]) {
    cmp_fn_t cmp = cmp_pstr;
    bool uniq = false;
    bool reverse = false;

    int opt = getopt(argc, argv, "lnru");  // Parses command line arguments.
    while (opt != -1) {
        if (opt == 'l') {
            cmp = cmp_pstr_len;
        } else if (opt == 'n') {
            cmp = cmp_pstr_numeric;
        } else if (opt == 'r') {
            reverse = true;
        } else if (opt == 'u') {
            uniq = true;
        } else {
            return 1;
        }

        opt = getopt(argc, argv, "lnru");
    }

    FILE *fp = stdin;
    if (optind < argc) {
        fp = fopen(argv[optind], "r");
        if (fp == NULL) {
            error(1, 0, "cannot access %s", argv[optind]);
        }
    }
    sort_lines(fp, cmp, uniq, reverse);
    fclose(fp);
    return 0;
}
