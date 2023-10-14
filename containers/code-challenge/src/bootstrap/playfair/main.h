#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>

void ex(char* f) {
    if (access(f, F_OK) != 0) {
        printf("%s not found. aborting", f);
        exit(1);
    }
}

FILE* rd(char* f, char *t) {
    FILE* fp = fopen(f, t);
    if (fp == NULL) {
        return NULL;
    }
    return fp;
}

char* ld(FILE* f) {
    char* b = 0;
    size_t l = 0;

    fseek(f, 0, SEEK_END);
    l = ftell(f);
    fseek(f, 0, SEEK_SET);

    b = (char*)malloc((l+1)*sizeof(char));
    fread(b, sizeof(char), l, f);

    return b;
}

char** gen(char* key) {
    char** tcb = (char**)malloc(5*sizeof(char*));
    for (int a = 0; a < 5; a++) {
        tcb[a] = (char*)malloc(5*sizeof(char));
    }

    int pc = 0;
    char pld[50] = {0};
    int cr = 0;
    int cc = 0;
    for (int a = 0; a < strlen(key); a++) {
        char c = tolower(key[a]);
        if (isalpha(c) == 0){
            continue;
        }
        int plf = 0;
        for (int b = 0; b < sizeof(pld); b++) {
            if (c == pld[b]) {
                plf = 1;
                break;
            }
        }
        if (plf == 1) {
            continue;
        }
        pld[pc] = c;
        pc++;
        if (c == 'j') {
            c = 'i';
        }
        tcb[cr][cc] = c;
        cc++;
        if (cc == 5) {
            cc = 0;
            cr++;
        }
    }

    int val = 97;
    while (pc < 25) {
        if (val == 106) {
            val++;
        }
        char c = val;
        int plf = 0;
        for (int b = 0; b < sizeof(pld); b++) {
            if (c == pld[b]) {
                plf = 1;
                break;
            }
        }
        if (plf == 1) {
            val++;
            continue;
        }
        pld[pc] = c;
        pc++;
        tcb[cr][cc] = c;
        cc++;
        if (cc == 5) {
            cc = 0;
            cr++;
        }
    }

    return tcb;
}

int pir(char* t) {
    int c = 0;
    for (int a=0; a <= strlen(t); a+=2) {
        if (a+1 <= strlen(t)) {
            if (t[a] == t[a+1]) {
                c++;
            }
        }
    }

    return c;
}

char* par(char* t) {
    char* p1 = (char*)malloc(strlen(t)+1);
    int a = 0, b = 0;
    while (t[a] != '\0') {
        if (isalpha(t[a]) == 0) {
            a++;
            continue;
        }
        p1[b] = t[a];
        if (p1[b] == 'j') {
            p1[b] = 'i';
        }
        p1[b] = tolower(p1[b]);
        a++;
        b++;
    }

    p1[b] = '\0';

    char* p2 = (char*)malloc(strlen(p1)+pir(p1)+1);
    int c = 0, d = 0;
    while (p1[c] != '\0') {
        p2[d] = p1[c];
        if (c+1 <= strlen(p1)) {
            if (p1[c] == p1[c+1]) {
                p2[d+1] = 'x';
                p2[d+2] = p1[c+1];
                d += 1;
            }
        }
        d++;
        c++;
    }
    free(p1);
    p2[d] = '\0';
    if (strlen(p2) % 2 == 0) {
        return p2;
    }

    char* p3 = (char*)malloc(strlen(p2)+2);
    int e = 0;
    while (p2[e] != '\0') {
        p3[e] = p2[e];
        e++;
    }
    p3[e] = 'x';
    p3[e+1] = '\0';
    free(p2);
    return p3;
}

char* ent(char* t, char** tcb) {
    char* tt = (char*)malloc(strlen(t) + 1);
    int len = strlen(t);

    for (int i = 0; i < len ; i += 2) {
        int r1, c1, r2, c2 = -1;

        for (int row = 0; row < 5; ++row) {
            for (int col = 0; col < 5; ++col) {
                if (tcb[row][col] == t[i]) {
                    r1 = row;
                    c1 = col;
                }
                if (tcb[row][col] == t[i+1]) {
                    r2 = row;
                    c2 = col;
                }
            }
        }

        if (r1 == r2) {
            tt[i] = tcb[r1][(c1 + 1) % 5];
            tt[i+1] = tcb[r2][(c2 + 1) % 5];
        } else if (c1 == c2) {
            tt[i] = tcb[(r1 + 1) % 5][c1];
            tt[i+1] = tcb[(r2 + 1) % 5][c2];
        } else {
            tt[i] = tcb[r1][c2];
            tt[i+1] = tcb[r2][c1];
        }
    }

    tt[len] = '\0';
    return tt;
}
