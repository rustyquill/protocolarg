#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {
    char *pf = NULL;
    char *of = NULL;
    char *dir = NULL;

    if (argc < 2) {
        return 1;
    }

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-p") == 0 && i + 1 < argc) {
            pf = argv[++i];
        } else if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
            of = argv[++i];
        }
    }
    if (pf == NULL) {
        pf = "IN";
    }
    if (of == NULL) {
        of = "dokumente.7z";
    }
    dir = argv[argc - 1];

    char pw[25];
    FILE *fpd = fopen(pf, "r");
    if (fpd == NULL) {
        return 1;
    }
    int pwi = 0;
    while(1) {
        int c = fgetc(fpd);
        if ((char)c == '\n' || c == -1) {
            break;
        }
        if ((char)c == ' ') {
            continue;
        }
        pw[pwi] = (char)toupper(c);
        pwi++;
        if (pwi == 25) {
            break;
        }
    }
    pw[pwi] = '\0';

    char *cli = (char*)malloc(100 * sizeof(char));
    sprintf(cli, "7z a -p\"%s\" -mhe=on -t7z %s \"%s\"", pw, of, dir);
    system(cli);
}
