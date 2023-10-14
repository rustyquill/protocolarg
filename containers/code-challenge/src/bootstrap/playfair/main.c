#include <stdio.h>
#include "main.h"

int main(int argc, char* argv[]) {
    ex("IN");
    FILE* fpd = rd("IN", "r");
    char* i = ld(fpd);
    fclose(fpd);

    ex("KEY");
    FILE* fdk = rd("KEY", "r");
    char* k = ld(fdk);
    fclose(fdk);

    char* p = par(i);
    char** tcb = gen(k);
    char* out = ent(p, tcb);

    FILE* fpo = rd("OUT", "w");
    fprintf(fpo, "%s", out);
    fclose(fpo);
}
