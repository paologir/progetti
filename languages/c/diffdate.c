#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void usage() {
    printf("Uso: %s data1 data2\n", "program_name");
    printf("Le date devono essere nel formato gg/mm/yyyy o gg-mm-yyyy\n");
    exit(1);
}

int is_valid_date(const char *date) {
    if (strlen(date) != 10) return 0;
    if ((date[2] == '/' || date[2] == '-') && (date[5] == '/' || date[5] == '-')) {
        for (int i = 0; i < 10; i++) {
            if (i == 2 || i == 5) continue;
            if (date[i] < '0' || date[i] > '9') return 0;
        }
        return 1;
    }
    return 0;
}

void convert_date(const char *input_date, char *output_date) {
    int day, month, year;
    if (input_date[2] == '/') {
        sscanf(input_date, "%d/%d/%d", &day, &month, &year);
    } else if (input_date[2] == '-') {
        sscanf(input_date, "%d-%d-%d", &day, &month, &year);
    } else {
        printf("Errore: formato data non valido.\n");
        usage();
    }
    sprintf(output_date, "%04d-%02d-%02d", year, month, day);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        usage();
    }

    char date1[11], date2[11];
    if (!is_valid_date(argv[1]) || !is_valid_date(argv[2])) {
        printf("Errore: formato data non valido.\n");
        usage();
    }

    char date1_converted[11], date2_converted[11];
    convert_date(argv[1], date1_converted);
    convert_date(argv[2], date2_converted);

    struct tm tm1 = {0}, tm2 = {0};
    strptime(date1_converted, "%Y-%m-%d", &tm1);
    strptime(date2_converted, "%Y-%m-%d", &tm2);

    time_t time1 = mktime(&tm1);
    time_t time2 = mktime(&tm2);

    double diff_in_seconds = difftime(time2, time1);
    int diff_in_days = diff_in_seconds / 86400;

    printf("La differenza in giorni tra %s e %s è: %d\n", argv[1], argv[2], diff_in_days);

    return 0;
}
