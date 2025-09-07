/**
 * bond_duration.c
 * Calcola il rendimento lordo e netto, la duration e l'importo a scadenza di un'obbligazione.
 * 
 * Compilazione: gcc -O3 -Wall -Wextra -o bond_duration bond_duration.c -lm
 * Uso: ./bond_duration [opzioni]
 * Opzioni:
 *   -h, --help     Mostra questo messaggio di aiuto
 *   -p PREZZO      Prezzo di acquisto dell'obbligazione
 *   -f VALORE      Valore nominale dell'obbligazione
 *   -c TASSO       Tasso di cedola (es. 0.04 per 4%)
 *   -m ANNI        Scadenza in anni
 *   -q FREQUENZA   Frequenza di pagamento della cedola (volte all'anno)
 *   -i             Modalità interattiva
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <getopt.h>
#include <ctype.h>
#include <errno.h>

#define MAX_ITERATIONS 100
#define TOLERANCE 1e-9
#define MAX_MATURITY 100
#define MAX_FREQUENCY 12
#define TAX_RATE 0.125  /* Tassazione del 12.5% sulle obbligazioni */

/* Struttura per memorizzare i parametri dell'obbligazione */
typedef struct {
    double price;           /* Prezzo in percentuale (es. 96.24) */
    double face_value;      /* Valore nominale unitario (tipicamente 100) */
    double coupon_rate;     /* Tasso cedola annuo */
    int maturity;           /* Scadenza in anni */
    int frequency;          /* Frequenza pagamento cedole */
    double amount;          /* Importo nominale acquistato */
} BondParams;

/* Struttura contenente i risultati del calcolo */
typedef struct {
    double yield_rate;
    double duration;
    double modified_duration;
    double convexity;
    double net_yield_rate;
    double total_coupons;
    double net_total_at_maturity;
} BondResults;

/**
 * Mostra il messaggio di aiuto
 */
void show_help(const char *program_name) {
    printf("Utilizzo: %s [opzioni]\n\n", program_name);
    printf("Descrizione: Calcola il rendimento lordo e netto, la duration e l'importo\n");
    printf("             complessivo netto a scadenza di un'obbligazione.\n\n");
    printf("Opzioni:\n");
    printf("  -h, --help     Mostra questo messaggio di aiuto\n");
    printf("  -p PREZZO      Prezzo di acquisto (in %% del nominale, es. 96.24)\n");
    printf("  -f VALORE      Valore nominale unitario (default: 100)\n");
    printf("  -c TASSO       Tasso di cedola annuo (es. 0.04 per 4%%)\n");
    printf("  -m ANNI        Scadenza in anni\n");
    printf("  -q FREQUENZA   Frequenza di pagamento della cedola (volte all'anno)\n");
    printf("  -a IMPORTO     Importo nominale acquistato (es. 10000)\n");
    printf("  -i             Modalità interattiva\n\n");
    printf("Note:\n");
    printf("  - I numeri decimali possono essere inseriti sia con il punto che con la virgola\n");
    printf("  - La tassazione applicata è del 12.5%% sui rendimenti\n");
    printf("  - Se non specificato, l'importo nominale è 100\n\n");
    printf("Esempio di utilizzo:\n");
    printf("  %s -p 96.24 -c 0.0315 -m 19 -a 10000\n", program_name);
    printf("  %s -i\n\n", program_name);
}

/**
 * Verifica la validità dei parametri dell'obbligazione
 * 
 * @param params Parametri dell'obbligazione
 * @return 0 se validi, -1 altrimenti
 */
int validate_params(const BondParams *params) {
    if (params->price <= 0) {
        fprintf(stderr, "Errore: Il prezzo deve essere positivo\n");
        return -1;
    }
    
    if (params->face_value <= 0) {
        fprintf(stderr, "Errore: Il valore nominale deve essere positivo\n");
        return -1;
    }
    
    if (params->coupon_rate < 0) {
        fprintf(stderr, "Errore: Il tasso di cedola non può essere negativo\n");
        return -1;
    }
    
    if (params->maturity <= 0 || params->maturity > MAX_MATURITY) {
        fprintf(stderr, "Errore: La scadenza deve essere tra 1 e %d anni\n", MAX_MATURITY);
        return -1;
    }
    
    if (params->frequency <= 0 || params->frequency > MAX_FREQUENCY) {
        fprintf(stderr, "Errore: La frequenza deve essere tra 1 e %d volte all'anno\n", MAX_FREQUENCY);
        return -1;
    }
    
    return 0;
}

/**
 * Calcola il valore attuale netto dell'obbligazione dato un rendimento
 * 
 * @param params Parametri dell'obbligazione
 * @param yield_rate Rendimento da testare
 * @return Valore attuale netto
 */
double calculate_npv(const BondParams *params, double yield_rate) {
    int i;
    int n_payments = params->maturity * params->frequency;
    double coupon_amount = params->face_value * params->coupon_rate / params->frequency;
    double npv = 0.0;
    double discount_rate = 1.0 + yield_rate / params->frequency;
    double discount_factor = 1.0;
    
    for (i = 1; i <= n_payments; i++) {
        discount_factor *= 1.0 / discount_rate;
        
        double cash_flow = coupon_amount;
        if (i == n_payments) {
            cash_flow += params->face_value;
        }
        
        npv += cash_flow * discount_factor;
    }
    
    return npv - params->price;
}

/**
 * Calcola la derivata della funzione NPV rispetto al rendimento
 * 
 * @param params Parametri dell'obbligazione
 * @param yield_rate Rendimento
 * @return Derivata del NPV
 */
double calculate_npv_derivative(const BondParams *params, double yield_rate) {
    int i;
    int n_payments = params->maturity * params->frequency;
    double coupon_amount = params->face_value * params->coupon_rate / params->frequency;
    double derivative = 0.0;
    double discount_rate = 1.0 + yield_rate / params->frequency;
    double discount_factor = 1.0;
    
    for (i = 1; i <= n_payments; i++) {
        discount_factor *= 1.0 / discount_rate;
        
        double cash_flow = coupon_amount;
        if (i == n_payments) {
            cash_flow += params->face_value;
        }
        
        derivative -= (i * cash_flow * discount_factor) / (params->frequency * discount_rate);
    }
    
    return derivative;
}

/**
 * Calcola il rendimento utilizzando il metodo di Newton-Raphson
 * 
 * @param params Parametri dell'obbligazione
 * @return Rendimento calcolato o NAN in caso di errore
 */
double calculate_yield(const BondParams *params) {
    int i;
    double yield_rate = params->coupon_rate; /* Valore iniziale */
    double npv, derivative;
    
    for (i = 0; i < MAX_ITERATIONS; i++) {
        npv = calculate_npv(params, yield_rate);
        
        /* Se NPV è abbastanza vicino a zero, abbiamo trovato il rendimento */
        if (fabs(npv) < TOLERANCE) {
            return yield_rate;
        }
        
        derivative = calculate_npv_derivative(params, yield_rate);
        
        /* Se la derivata è troppo piccola, rischiamo una divisione per zero */
        if (fabs(derivative) < DBL_EPSILON) {
            fprintf(stderr, "Errore: Derivata troppo piccola nel calcolo del rendimento\n");
            return NAN;
        }
        
        double delta = npv / derivative;
        yield_rate -= delta;
        
        /* Controllo per evitare rendimenti negativi non realistici */
        if (yield_rate < -0.9 / params->frequency) {
            yield_rate = -0.9 / params->frequency;
        }
        
        /* Se la variazione è abbastanza piccola, abbiamo convergenza */
        if (fabs(delta) < TOLERANCE) {
            return yield_rate;
        }
    }
    
    fprintf(stderr, "Avviso: Raggiunto il numero massimo di iterazioni nel calcolo del rendimento\n");
    return yield_rate; /* Ritorniamo il valore corrente anche se non abbiamo raggiunto la precisione desiderata */
}

/**
 * Calcola duration, modified duration e convexity dell'obbligazione
 * 
 * @param params Parametri dell'obbligazione
 * @param yield_rate Rendimento calcolato
 * @param results Struttura dove salvare i risultati
 */
void calculate_bond_metrics(const BondParams *params, double yield_rate, BondResults *results) {
    int i;
    int n_payments = params->maturity * params->frequency;
    double coupon_amount = params->face_value * params->coupon_rate / params->frequency;
    double discount_rate = 1.0 + yield_rate / params->frequency;
    double discount_factor = 1.0;
    
    double weighted_time_sum = 0.0;
    double weighted_time_squared_sum = 0.0;
    double present_value_sum = 0.0;
    
    for (i = 1; i <= n_payments; i++) {
        discount_factor *= 1.0 / discount_rate;
        
        double cash_flow = coupon_amount;
        if (i == n_payments) {
            cash_flow += params->face_value;
        }
        
        double present_value = cash_flow * discount_factor;
        double time_in_years = (double)i / params->frequency;
        
        weighted_time_sum += time_in_years * present_value;
        weighted_time_squared_sum += time_in_years * time_in_years * present_value;
        present_value_sum += present_value;
    }
    
    /* Calcolo della duration in anni */
    results->duration = weighted_time_sum / params->price;
    
    /* Calcolo della modified duration */
    results->modified_duration = results->duration / discount_rate;
    
    /* Calcolo della convexity */
    results->convexity = weighted_time_squared_sum / (params->price * pow(discount_rate, 2));
}

/**
 * Legge un double valido dallo stdin
 * 
 * @param prompt Messaggio da mostrare all'utente
 * @param min_value Valore minimo consentito
 * @param max_value Valore massimo consentito
 * @return Valore letto o NAN in caso di errore
 */
double read_double(const char *prompt, double min_value, double max_value) {
    char buffer[256];
    double value;
    char *endptr;
    
    while (1) {
        printf("%s", prompt);
        
        if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
            return NAN;
        }
        
        /* Rimuove spazi iniziali e finali */
        char *start = buffer;
        while (isspace((unsigned char)*start)) {
            start++;
        }
        
        char *end = start + strlen(start) - 1;
        while (end > start && isspace((unsigned char)*end)) {
            *end-- = '\0';
        }
        
        if (*start == '\0') {
            printf("Errore: Inserire un valore valido\n");
            continue;
        }
        
        /* Sostituisce le virgole con i punti per gestire l'input con virgola decimale */
        char *comma = strchr(start, ',');
        if (comma != NULL) {
            *comma = '.';
        }
        
        /* Converte la stringa in double */
        errno = 0;
        value = strtod(start, &endptr);
        
        if (errno != 0 || *endptr != '\0') {
            printf("Errore: Inserire un numero valido (es. 1000 oppure 1000.50 oppure 1000,50)\n");
            continue;
        }
        
        if (value < min_value || value > max_value) {
            printf("Errore: Il valore deve essere compreso tra %g e %g\n", min_value, max_value);
            continue;
        }
        
        return value;
    }
}

/**
 * Legge un intero valido dallo stdin
 * 
 * @param prompt Messaggio da mostrare all'utente
 * @param min_value Valore minimo consentito
 * @param max_value Valore massimo consentito
 * @return Valore letto o -1 in caso di errore
 */
int read_int(const char *prompt, int min_value, int max_value) {
    char buffer[256];
    int value;
    char *endptr;
    
    while (1) {
        printf("%s", prompt);
        
        if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
            return -1;
        }
        
        /* Rimuove spazi iniziali e finali */
        char *start = buffer;
        while (isspace((unsigned char)*start)) {
            start++;
        }
        
        char *end = start + strlen(start) - 1;
        while (end > start && isspace((unsigned char)*end)) {
            *end-- = '\0';
        }
        
        if (*start == '\0') {
            printf("Errore: Inserire un valore valido\n");
            continue;
        }
        
        /* Converte la stringa in intero */
        errno = 0;
        value = (int)strtol(start, &endptr, 10);
        
        if (errno != 0 || *endptr != '\0') {
            printf("Errore: Inserire un numero intero valido\n");
            continue;
        }
        
        if (value < min_value || value > max_value) {
            printf("Errore: Il valore deve essere compreso tra %d e %d\n", min_value, max_value);
            continue;
        }
        
        return value;
    }
}

/**
 * Richiede i parametri dell'obbligazione in modalità interattiva
 * 
 * @param params Struttura dove salvare i parametri
 * @return 0 in caso di successo, -1 in caso di errore
 */
int read_params_interactive(BondParams *params) {
    double amount = read_double("Inserisci l'importo nominale da acquistare (es. 10000): ", 1.0, 100000000.0);
    if (isnan(amount)) return -1;
    params->amount = amount;
    
    double price = read_double("Inserisci il prezzo di acquisto (in % del nominale, es. 96.24): ", 0.01, 200.0);
    if (isnan(price)) return -1;
    params->price = price;
    
    params->face_value = 100.0; /* Valore nominale unitario standard */
    
    double coupon_rate = read_double("Inserisci il tasso di cedola annuo (4% va indicato come 0.04): ", 0.0, 1.0);
    if (isnan(coupon_rate)) return -1;
    params->coupon_rate = coupon_rate;
    
    int maturity = read_int("Inserisci la scadenza dell'obbligazione (in anni): ", 1, MAX_MATURITY);
    if (maturity == -1) return -1;
    params->maturity = maturity;
    
    int frequency = read_int("Inserisci la frequenza di pagamento della cedola (numero di volte all'anno): ", 1, MAX_FREQUENCY);
    if (frequency == -1) return -1;
    params->frequency = frequency;
    
    return 0;
}

/**
 * Funzione principale
 */
int main(int argc, char *argv[]) {
    BondParams params = {0};
    BondResults results = {0};
    int opt, interactive = 0;
    int params_set = 0;
    
    /* Opzioni lunghe corrispondenti alle opzioni brevi */
    static struct option long_options[] = {
        {"help", no_argument, 0, 'h'},
        {"price", required_argument, 0, 'p'},
        {"face", required_argument, 0, 'f'},
        {"coupon", required_argument, 0, 'c'},
        {"maturity", required_argument, 0, 'm'},
        {"frequency", required_argument, 0, 'q'},
        {"amount", required_argument, 0, 'a'},
        {"interactive", no_argument, 0, 'i'},
        {0, 0, 0, 0}
    };
    
    /* Valori di default */
    params.face_value = 100.0;
    params.amount = 100.0;
    
    /* Parsing delle opzioni */
    while ((opt = getopt_long(argc, argv, "hp:f:c:m:q:a:i", long_options, NULL)) != -1) {
        switch (opt) {
            case 'h':
                show_help(argv[0]);
                return EXIT_SUCCESS;
            case 'p':
                /* Sostituisce virgole con punti per gestire input con virgola decimale */
                {
                    char *comma = strchr(optarg, ',');
                    if (comma != NULL) {
                        *comma = '.';
                    }
                }
                params.price = atof(optarg);
                params_set |= 1;
                break;
            case 'f':
                /* Sostituisce virgole con punti per gestire input con virgola decimale */
                {
                    char *comma = strchr(optarg, ',');
                    if (comma != NULL) {
                        *comma = '.';
                    }
                }
                params.face_value = atof(optarg);
                params_set |= 2;
                break;
            case 'c':
                /* Sostituisce virgole con punti per gestire input con virgola decimale */
                {
                    char *comma = strchr(optarg, ',');
                    if (comma != NULL) {
                        *comma = '.';
                    }
                }
                params.coupon_rate = atof(optarg);
                params_set |= 4;
                break;
            case 'm':
                params.maturity = atoi(optarg);
                params_set |= 8;
                break;
            case 'q':
                params.frequency = atoi(optarg);
                params_set |= 16;
                break;
            case 'a':
                /* Sostituisce virgole con punti per gestire input con virgola decimale */
                {
                    char *comma = strchr(optarg, ',');
                    if (comma != NULL) {
                        *comma = '.';
                    }
                }
                params.amount = atof(optarg);
                params_set |= 32;
                break;
            case 'i':
                interactive = 1;
                break;
            default:
                fprintf(stderr, "Prova '%s --help' per maggiori informazioni.\n", argv[0]);
                return EXIT_FAILURE;
        }
    }
    
    /* Se non sono stati specificati i parametri obbligatori, usa la modalità interattiva */
    int required_params = 1 | 4 | 8 | 16; /* p, c, m, q sono obbligatori */
    if ((params_set & required_params) != required_params && !interactive) {
        if (params_set == 0) {
            interactive = 1;
        } else {
            fprintf(stderr, "Errore: Devono essere specificati almeno prezzo, cedola, scadenza e frequenza\n");
            fprintf(stderr, "Prova '%s --help' per maggiori informazioni.\n", argv[0]);
            return EXIT_FAILURE;
        }
    }
    
    if (interactive) {
        if (read_params_interactive(&params) != 0) {
            fprintf(stderr, "Errore nella lettura dei parametri\n");
            return EXIT_FAILURE;
        }
    }
    
    /* Validazione dei parametri */
    if (validate_params(&params) != 0) {
        return EXIT_FAILURE;
    }
    
    /* Calcolo del rendimento */
    results.yield_rate = calculate_yield(&params);
    if (isnan(results.yield_rate)) {
        fprintf(stderr, "Errore nel calcolo del rendimento\n");
        return EXIT_FAILURE;
    }
    
    /* Calcolo di duration, modified duration e convexity */
    calculate_bond_metrics(&params, results.yield_rate, &results);
    
    /* Calcolo del rendimento netto e degli importi */
    results.net_yield_rate = results.yield_rate * (1 - TAX_RATE);
    
    /* Calcolo del totale delle cedole */
    int n_payments = params.maturity * params.frequency;
    double coupon_amount_per_unit = params.face_value * params.coupon_rate / params.frequency;
    double coupon_amount = coupon_amount_per_unit * params.amount / params.face_value;
    results.total_coupons = coupon_amount * n_payments;
    
    /* Calcolo dell'importo complessivo netto a scadenza */
    /* Le cedole sono tassate al 12.5% */
    double net_coupons = results.total_coupons * (1 - TAX_RATE);
    
    /* Il capital gain (o loss) è tassato al 12.5% solo se positivo */
    double price_paid = params.price * params.amount / 100.0;
    double capital_gain = params.amount - price_paid;
    double net_capital_gain = capital_gain;
    if (capital_gain > 0) {
        net_capital_gain = capital_gain * (1 - TAX_RATE);
    }
    
    /* L'importo netto totale a scadenza è: prezzo pagato + cedole nette + capital gain netto */
    results.net_total_at_maturity = price_paid + net_coupons + net_capital_gain;
    
    /* Stampa dei risultati */
    printf("\n=== RISULTATI DELL'ANALISI ===\n");
    printf("\nRendimenti:\n");
    printf("  Rendimento lordo: %.2f%%\n", results.yield_rate * 100);
    printf("  Rendimento netto: %.2f%% (tassazione %.1f%%)\n", results.net_yield_rate * 100, TAX_RATE * 100);
    
    printf("\nMetriche di durata:\n");
    printf("  Duration: %.2f anni\n", results.duration);
    printf("  Modified duration: %.2f\n", results.modified_duration);
    printf("  Convexity: %.4f\n", results.convexity);
    
    double cap_gain = params.amount - price_paid;
    
    printf("\nDati dell'investimento:\n");
    printf("  Importo nominale: %.2f\n", params.amount);
    printf("  Prezzo di acquisto: %.2f%% del nominale\n", params.price);
    printf("  Importo pagato: %.2f\n", price_paid);
    
    printf("\nImporti a scadenza:\n");
    printf("  Valore nominale a scadenza: %.2f\n", params.amount);
    printf("  Totale cedole lorde: %.2f\n", results.total_coupons);
    printf("  Totale cedole nette: %.2f (tassate al %.1f%%)\n", results.total_coupons * (1 - TAX_RATE), TAX_RATE * 100);
    
    if (cap_gain > 0) {
        printf("  Capital gain lordo: %.2f\n", cap_gain);
        printf("  Capital gain netto: %.2f (tassato al %.1f%%)\n", cap_gain * (1 - TAX_RATE), TAX_RATE * 100);
    } else if (cap_gain < 0) {
        printf("  Capital loss: %.2f (non tassato)\n", cap_gain);
    }
    
    printf("  Importo lordo totale: %.2f\n", params.amount + results.total_coupons);
    printf("  Importo netto totale: %.2f\n", results.net_total_at_maturity);
    printf("  Rendimento netto totale: %.2f\n", results.net_total_at_maturity - price_paid);
    
    /* Stima della variazione di prezzo */
    printf("\nAnalisi di sensibilità al tasso di interesse:\n");
    double price_change_1bp = -results.modified_duration * price_paid * 0.0001;
    printf("  Variazione per +1 basis point (0.01%%): %.2f\n", price_change_1bp);
    printf("  Variazione per +100 basis point (1%%): %.2f\n", price_change_1bp * 100);
    
    return EXIT_SUCCESS;
}
