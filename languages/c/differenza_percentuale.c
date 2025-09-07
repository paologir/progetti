/**
 * differenza_percentuale.c
 * Calcola la differenza percentuale tra due valori numerici.
 * 
 * Compilazione: gcc -O3 -Wall -Wextra -o differenza_percentuale differenza_percentuale.c -lm
 * Uso: ./differenza_percentuale valore1 valore2
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <errno.h>
#include <string.h>
#include <float.h>

/**
 * Calcola la differenza percentuale tra due numeri.
 * Formula: ((valore2 - valore1) / |valore1|) * 100
 * 
 * @param valore1 Valore di riferimento
 * @param valore2 Valore da confrontare
 * @return La differenza percentuale o NAN in caso di errore
 */
double calcola_differenza_percentuale(double valore1, double valore2) {
    // Controllo se il valore1, usato come divisore, è troppo vicino a zero
    if (fabs(valore1) < DBL_EPSILON) {
        fprintf(stderr, "Errore: Il valore di riferimento è troppo vicino a zero.\n");
        return NAN;
    }
    
    return ((valore2 - valore1) / fabs(valore1)) * 100.0;
}

/**
 * Converte una stringa in double con controllo degli errori.
 * 
 * @param str Stringa da convertire
 * @param risultato Puntatore dove salvare il risultato
 * @return 0 in caso di successo, -1 in caso di errore
 */
int converti_a_double(const char *str, double *risultato) {
    char *end;
    errno = 0;
    
    *risultato = strtod(str, &end);
    
    // Controlla errori di conversione
    if (errno == ERANGE) {
        fprintf(stderr, "Errore: Valore fuori dal range consentito.\n");
        return -1;
    }
    
    // Controlla se sono stati elaborati tutti i caratteri
    if (*end != '\0') {
        fprintf(stderr, "Errore: '%s' non è un numero valido.\n", str);
        return -1;
    }
    
    return 0;
}

/**
 * Mostra le istruzioni d'uso del programma.
 * 
 * @param nome_programma Nome del programma
 */
void mostra_aiuto(const char *nome_programma) {
    printf("Utilizzo: %s valore1 valore2\n\n", nome_programma);
    printf("Calcola la differenza percentuale tra due valori numerici.\n");
    printf("Formula: ((valore2 - valore1) / |valore1|) * 100\n\n");
    printf("Esempio: %s 100 150\n", nome_programma);
    printf("Output: Differenza percentuale: +50.00%%\n\n");
}

int main(int argc, char *argv[]) {
    double valore1, valore2, differenza;
    
    // Controlla se sono stati forniti argomenti sufficienti
    if (argc != 3) {
        mostra_aiuto(argv[0]);
        return EXIT_FAILURE;
    }
    
    // Converte il primo argomento in double
    if (converti_a_double(argv[1], &valore1) != 0) {
        return EXIT_FAILURE;
    }
    
    // Converte il secondo argomento in double
    if (converti_a_double(argv[2], &valore2) != 0) {
        return EXIT_FAILURE;
    }
    
    // Calcola la differenza percentuale
    differenza = calcola_differenza_percentuale(valore1, valore2);
    
    // Verifica se il calcolo è riuscito
    if (isnan(differenza)) {
        return EXIT_FAILURE;
    }
    
    // Mostra il risultato con segno + o - e due decimali
    printf("Differenza percentuale: %+.2f%%\n", differenza);
    
    return EXIT_SUCCESS;
}
