#include <stdio.h>
#include <stdlib.h>
#include <string.h>

double calcola_differenza_percentuale(double valore1, double valore2) {
    return ((valore2 - valore1) / valore1) * 100;
}

double converti_numero(const char *input_string) {
    char *endptr;
    double numero = strtod(input_string, &endptr);
    if (*endptr != '\0') {
        // Se la conversione fallisce, prova a sostituire la virgola con il punto e poi convertire
        char *temp = strdup(input_string);
        for (char *p = temp; *p; p++) {
            if (*p == ',') *p = '.';
        }
        numero = strtod(temp, &endptr);
        free(temp);
        if (*endptr != '\0') {
            fprintf(stderr, "Errore: entrambi i valori devono essere numeri.\n");
            exit(1);
        }
    }
    return numero;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Uso: %s valore1 valore2\n", argv[0]);
        return 1;
    }

    double valore1 = converti_numero(argv[1]);
    double valore2 = converti_numero(argv[2]);

    if (valore1 == 0) {
        fprintf(stderr, "Errore: il primo valore non può essere zero.\n");
        return 1;
    }

    double differenza_percentuale = calcola_differenza_percentuale(valore1, valore2);
    printf("%.2f%%\n", differenza_percentuale);

    return 0;
}
