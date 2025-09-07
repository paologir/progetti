# Carico le librerie
library(googleAnalyticsR)
library(txtplot)
library(dplyr)
library(tidyr)
library(UsingR)
library(outliers)
library(readr)
library(moments)
library(searchConsoleR)
library(ggplot2)


# Specifica il percorso della chiave JSON del service account
ga_auth(
  json_file = '/opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json',  # Sostituisci con il tuo percorso
  #  cache = FALSE  # Disabilita la cache per evitare errori in ambienti non interattivi
)

# Autorizzo Google Analytics. 
# ga_auth(email="gironipaolo@gmail.com")

my_property_id <- "353989568" # Maspe da marzo 2023 - ok tracciamenti

## Scelgo il range di date
# Richiedi all'utente di inserire la data di inizio nel formato corretto
cat("Inserisci data inizio nel formato YYYY-MM-DD: ")
datainizio <- readLines("stdin", n = 1)
# Richiedi all'utente di inserire la data di fine nel formato corretto
cat("Inserisci data fine nel formato YYYY-MM-DD: ")
datafine <- readLines("stdin", n = 1)
 
# Richiedo i dati
basic <- ga_data(
  my_property_id,
  metrics = c("TotalUsers","sessions"),
  dimensions = c("date"),
  date_range = c(datainizio, datafine),
  # dim_filters = ga_data_filter(sessionMedium=="organic"),
  limit = -1, # nessun limite, tutti i dati
  orderBys = ga_data_order(+date) # ordino per data (-date)=inverso
)

basic <- basic %>%
  mutate(id_progressivo = row_number())

# sessionMedium - ecco i possibili valori
# organic
# (none)
# cpc
# referral
# email
# (not set)

# Li stampo a video
basic

cat("============\n")
cat("\u001B[31mUtenti Maspe\u001B[0m\n")
cat("============\n\n")
cat("da",datainizio,"a",datafine,"\n")
cat("---------------------------")
num5<-fivenum(basic$TotalUsers)
media<-mean(basic$TotalUsers)
cat("\nMedia:\t\t",media,"\n")
cat("5Numeri:\t",num5)

# cerco outliers
Q1 <- quantile(basic$TotalUsers, 0.25)
Q3 <- quantile(basic$TotalUsers, 0.75)
IQR <- Q3 - Q1
cat("\nIQR:\t\t",IQR,"\n")
#calcolo dei limiti di accettabilità per gli outliers
lower_limit <- Q1 - 1.5*IQR
upper_limit <- Q3 + 1.5*IQR


cat("\n\n\u001B[1mSerie temporale\u001B[0m\n\n")
txtplot(basic$id_progressivo,basic$TotalUsers)

cat("\n\n\u001B[1mBoxplot\u001B[0m\n\n")
txtboxplot(basic$TotalUsers)
# stampa i limiti outliers
cat("Limiti outliers:\t", lower_limit, "-", upper_limit,"\n\n")

# Aggiungi una nuova colonna 'day_of_week' con il nome del giorno della settimana
basic$day_of_week <- weekdays(basic$date, abbreviate = FALSE)
# Riordina le colonne
basic <- basic[, c("id_progressivo","date", "day_of_week", "TotalUsers", "sessions")]

cat("\nSalvo i dati nel file mieidati.csv\n\n")
# datiweb <- basic %>%
#  select(data = date, utenti = TotalUsers)


# Salvo in organici gli utenti del segmento organico
utenti_totali <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date"),
  metrics = c("totalUsers"),
  orderBys = ga_data_order(+date),
  limit = -1,
)

utenti_totali <- rename(utenti_totali, data = date, utenti = totalUsers) 

# Salvo in organici gli utenti del segmento organico
organici <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date","firstUserMedium"),
  dim_filters = ga_data_filter(firstUserMedium=="organic"),
  metrics = c("totalUsers"),
  orderBys = ga_data_order(+date),
  limit = -1,
)

organici <- organici [,-2]
organici <- rename(organici, data = date, organici = totalUsers) 



# Trovo i moduli per data
conversioni <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date","eventName"),
  dim_filters = ga_data_filter(eventName=="modulo_generico" | eventName=="modulo_infoprodotto"),
  metrics = c("totalUsers"),
  orderBys = ga_data_order(+date),
  limit = -1,
)

conversioni <- rename(conversioni, data = date, utenti = totalUsers) 
# Recupero i costi giornalieri
costi <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date","googleAdsAccountName"),
  metrics = c("advertiserAdCost"),
  orderBys = ga_data_order(+date),
  limit = -1,
)

# Rinomina la colonna dei costi
costi <- rename(costi, data = date, costo = advertiserAdCost)

# Rimuovi la colonna "googleAdsAccountName" se non è necessaria
costi <- costi[,-2]

# Somma i costi per ogni data
costi <- costi %>%
  group_by(data) %>%
  summarise(costo = sum(costo, na.rm = TRUE))

# Crea un dataframe di date completo
date_complete <- data.frame(data = seq(min(utenti_totali$data), max(utenti_totali$data), by = "day"))


# Limita il valore decimale a 2 posti dopo la virgola
# costi$costo <- round(costi$costo, 2)

# Divide il dataframe 'conversioni' in due dataframe separati
conversioni_modulo_infoprodotto <- conversioni[conversioni$eventName == "modulo_infoprodotto", ]
conversioni_modulo_generico <- conversioni[conversioni$eventName == "modulo_generico", ]

# Rinomina le colonne 'utenti' nei nuovi dataframe
names(conversioni_modulo_infoprodotto)[names(conversioni_modulo_infoprodotto) == "utenti"] <- "modulo_infoprodotto"
names(conversioni_modulo_generico)[names(conversioni_modulo_generico) == "utenti"] <- "modulo_generico"

# Unisci i dataframe 'conversioni_modulo_infoprodotto' e 'conversioni_modulo_generico' con il dataframe di date
conversioni_modulo_infoprodotto <- merge(date_complete, conversioni_modulo_infoprodotto, by = "data", all.x = TRUE)
conversioni_modulo_generico <- merge(date_complete, conversioni_modulo_generico, by = "data", all.x = TRUE)

# Sostituisci i valori NA con 0
conversioni_modulo_infoprodotto[is.na(conversioni_modulo_infoprodotto)] <- 0
conversioni_modulo_generico[is.na(conversioni_modulo_generico)] <- 0

# Prosegui con l'unione dei dataframe come prima
df_unificato <- merge(utenti_totali, organici, by = "data")
df_unificato <- merge(df_unificato, conversioni_modulo_infoprodotto[, c("data", "modulo_infoprodotto")], by = "data")
df_unificato <- merge(df_unificato, conversioni_modulo_generico[, c("data", "modulo_generico")], by = "data")

# Aggiungi una nuova colonna 'moduli' che è la somma di 'modulo_infoprodotto' e 'modulo_generico'
df_unificato$moduli <- df_unificato$modulo_infoprodotto + df_unificato$modulo_generico

# Aggiungi i costi giornalieri al dataframe df_unificato
df_unificato <- merge(df_unificato, costi, by = "data", all.x = TRUE)

# Sostituisci i valori NA nella colonna dei costi con 0
df_unificato$costo[is.na(df_unificato$costo)] <- 0

# Aggiungi una nuova colonna 'day_of_week' con il nome del giorno della settimana
df_unificato$day_of_week <- weekdays(df_unificato$data, abbreviate = FALSE)

df_maspe <- df_unificato

write.csv(df_maspe, "/tmp/maspe-dati.csv", row.names = FALSE)

# Plot time series using ggplot2
p <- ggplot(df_unificato, aes(x = data)) +
  geom_line(aes(y = utenti), color = "blue") +
  geom_line(aes(y = organici), color = "red") +
  theme_minimal()

# Save the plot as a JPG file
ggsave(filename = "/tmp/ts-maspe.jpg", plot = p, device = "jpeg")



# dati basici
mean(df_maspe$utenti)
fivenum(df_maspe$utenti)


# cerco outliers
Q1 <- quantile(df_maspe$utenti, 0.25)
Q3 <- quantile(df_maspe$utenti, 0.75)
IQR <- Q3 - Q1
cat("IQR=",IQR)
#calcolo dei limiti di accettabilità per gli outliers
lower_limit <- Q1 - 1.5*IQR
cat("\n")
upper_limit <- Q3 + 1.5*IQR
cat("\n")
# stampa i limiti outliers
cat("Limiti outliers: ", lower_limit, " - ", upper_limit)
cat("\n")

# asimmetria della distribuzione
# 0=simmetrica, >0 asimmetria destra, <0 asimmetria sinistra
# i valori sono in genere compresi tra -3 e 3
asimmetria=skewness(df_maspe$utenti)
print(asimmetria)
if (asimmetria < 0) { cat ('La distribuzione presenta asimmetria sinistra')
} else if(asimmetria > 0) {cat('La distribuzione presenta asimmetria destra')
} else {cat('distribuzione perfettamente normale')}

cat("\n")

# curtosi della distribuzione
# <3 platicurtica, =3 mesocurtica, >3 leptocurtica
curtosi=kurtosis(df_maspe$utenti)
print(curtosi)
if (curtosi < 3) { cat ('distribuzione platicurtica')
} else if(curtosi > 3) {cat('distribuzione leptocurtica')
} else {cat('distribuzione perfettamente normale')}
cat("\n")

# qui scelgo 12,5% e 87,5%
cat("Calcolo l'intervallo tra i quantili 12,5% e 87,5%")
cat("\n")
quant<-quantile(df_maspe$utenti, probs = c(0.125,0.875))
print(quant)


# Imposta i parametri di query
campagne <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("campaignName"),
  metrics = c("AdvertiserAdCost","conversions:modulo_generico","conversions:modulo_infoprodotto"),
  limit = -1,
)

campagne

write.csv(campagne, "/tmp/maspe-campagne.csv", row.names = FALSE)

#########################
# Google Search Console #
#########################
## authentication similar to googleAnalyticsR
# Autenticazione con service account JSON invece di OAuth
scr_auth(
  json_file = '/opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json'
)


queries <-
  search_analytics("https://www.maspe.com",
                   start = datainizio, end = datafine,
                   dimensions = c("query"),
                   searchType = "web", rowLimit = 40)
pages <- 
  search_analytics("https://www.maspe.com",
                   start = datainizio, end = datafine,
                   dimensions = c("page"),
                   searchType = "web", rowLimit = 40)

# Modifica la colonna "ctr" in percentuale e arrotonda a due cifre decimali
queries$ctr <- round(queries$ctr * 100, 2)
# Arrotonda la colonna "position" a due cifre decimali
queries$position <- round(queries$position, 2)

queries

# Rimuovi "https://www.maspe.com/" dalla colonna "page"
pages$page <- gsub("https://www.maspe.com/", "", pages$page)

# Modifica la colonna "ctr" in percentuale e arrotonda a due cifre decimali
pages$ctr <- round(pages$ctr * 100, 2)
# Arrotonda la colonna "position" a due cifre decimali
pages$position <- round(pages$position, 2)


write.csv(pages, "/tmp/maspe-pagine.csv", row.names = FALSE)
write.csv(queries, "/tmp/maspe-queries.csv", row.names = FALSE)

#########################
### Analisi Bayesiana ###
#########################

# Calcola i totali accumulati
total_visitors <- sum(df_maspe$utenti)
total_conversions <- sum(df_maspe$moduli)

# Calcola gli parametri della distribuzione Beta
alpha <- total_conversions + 1  # assuming a weakly informative prior Beta(1,1)
beta <- total_visitors - total_conversions + 1

# Calcola l'intervallo credibile al 95%
ci <- qbeta(c(0.025, 0.975), alpha, beta)

# Arrotonda ai due decimali e converte in percentuale
lower_percent <- round(ci[1] * 100, 2)
upper_percent <- round(ci[2] * 100, 2)

# Stampa a video in modo leggibile
cat("\nStima percentuale conversione bayesiana:\n")
cat("Totali accumulati:\n")
cat("Utenti totali:", total_visitors, "\n")
cat("Moduli totali:", total_conversions, "\n")
cat("Intervallo credibile al 95%: [", lower_percent, "%, ", upper_percent, "%]\n")

