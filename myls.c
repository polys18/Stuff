/* This program prints entries in a given directory(s) which is provided as command line argument(s).
 * Entries are sorted by name by default but if invoked with the -z flag entries are sorted by type
 * so that directories come before non directories.
 * If invoked with the -a flag it also prints entries that start with '.'
*/
#include <dirent.h>
#include <error.h>
#include <getopt.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { SORT_BY_NAME, SORT_BY_TYPE };
enum { EXCLUDE_DOT, INCLUDE_DOT };

/* This fully implemented function returns whether the dirent pointed to by
 * the given pointer represents a directory.  (Note: on the myth filesystem,
 * the only file type information that is accurate is directory/not-directory
 * used here. Other type info in struct dirent is not reliable).
 */
bool is_dir(const struct dirent *dirptr) {
    return dirptr->d_type == DT_DIR;
}

// Returns 1 if there is no dot at the start and 0 if there is.
int exclude_dot(const struct dirent *dir) {
    if (dir->d_name[0] == '.') {
        return 0;
    }
    return 1;
}

// Compares two strings using strcmp
int compare_by_name(const struct dirent **dir_1, const struct dirent **dir_2) {
    return strcmp((*dir_1)->d_name, (*dir_2)->d_name);
}

/* Comparison function. Directories are prioritized over non-directories.
 * If both are directories they are compared lexicographically.
*/
int compare_by_type(const struct dirent **dir_1, const struct dirent **dir_2) {
    if ((is_dir(*dir_1) && is_dir(*dir_2)) || (!is_dir(*dir_1) && !is_dir(*dir_2))) {
        return strcmp((*dir_1)->d_name, (*dir_2)->d_name);
    }
    if (is_dir(*dir_1) && !is_dir(*dir_2)) {
        return -1;
    }
    return 1;
}

/* Prints entries in dirpath sorted by name by default. If invoked with -z flag entries
 * are sorted by type. If invoked with the -a flag entries that start with '.' are also
 * printed.
*/
void ls(const char *dirpath, int filter, int order) {
    struct dirent **namelist = NULL;
    int n = 0;
    if (filter == INCLUDE_DOT) {
        n = order == SORT_BY_NAME ? scandir(dirpath, &namelist, NULL, compare_by_name) :
            scandir(dirpath, &namelist, NULL, compare_by_type);
        if (n == -1) {
            error(0, 0, "cannot access %s", dirpath);
            return;
        }
    } else {
        n = order == SORT_BY_NAME ? scandir(dirpath, &namelist, exclude_dot, compare_by_name) :
            scandir(dirpath, &namelist, exclude_dot, compare_by_type);
        if (n == -1) {
            error(0, 0, "cannot access %s", dirpath);
            return;
        }
    }
    for (int i = 0; i < n; i++) {
        if (is_dir(namelist[i])) {
            printf("%s/\n", namelist[i]->d_name);
            free(namelist[i]);
        } else {
            printf("%s\n", namelist[i]->d_name);
            free(namelist[i]);
        }
    }
    free(namelist);    
}

// ------- DO NOT EDIT ANY CODE BELOW THIS LINE (but do add comments!)  -------

// Processes command line arguments and flags and calls ls.
int main(int argc, char *argv[]) {
    int order = SORT_BY_NAME;
    int filter = EXCLUDE_DOT;

    int opt = getopt(argc, argv, "az");  // Parses command line arguments.
    while (opt != -1) {
        if (opt == 'a') {  // If -a is present.
            filter = INCLUDE_DOT;
        } else if (opt == 'z') {  // If -z is present.
            order = SORT_BY_TYPE;
        } else {
            return 1;
        }

        opt = getopt(argc, argv, "az");
    }
    
    if (optind < argc - 1) {  // If there is more than 1 command line argument.
        for (int i = optind; i < argc; i++) {
            printf("%s:\n", argv[i]);
            ls(argv[i], filter, order);
            printf("\n");
        }
    } else {
        ls(optind == argc - 1 ? argv[optind] : ".", filter, order);
    }
    
    return 0;
}
