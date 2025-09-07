# Carico le librerie
library(googleAnalyticsR)
library(dplyr)
library(tidyr)
library(zoo)
library(ggplot2)

###################
# Recupero i dati #
###################

# Autorizzo Google Analytics. 
ga_auth()

my_property_id <- "292349835"

# Scelgo la data di inizio
# Scelgo la data di fine
datainizio <- "2022-06-01"
datafine <- "2023-02-15"

# Imposta i parametri di query
daticosto <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date","sessionGoogleAdsAccountName"),
  dim_filters = ga_data_filter(sessionGoogleAdsAccountName=="Cape Horn"),
  metrics = c("totalUsers", "advertiserAdCost", "purchaseRevenue"),
  orderBys = ga_data_order(-date),
  limit = -1,
)

datisito <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date", "defaultChannelGroup"),
  metrics = c("totalUsers","purchaseRevenue"),
  orderBys = ga_data_order(-date),
  limit = -1,
)

utenti <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date"),
  metrics = c("totalUsers","purchaseRevenue"),
  orderBys = ga_data_order(-date),
  limit = -1,
)


# Esegui la query di GA4 per gli utenti organici
utentiorganic <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date"),
  metrics = c("totalUsers"),
  orderBys = ga_data_order(-date),
  limit = -1,
  dim_filters = ga_data_filter(medium=="organic")
)




##################
# Pulisco i dati #
##################

# Rinomina la colonna "sessionGoogleAdsAccountName" in "medium"
daticosto <- daticosto %>% rename(medium = sessionGoogleAdsAccountName)

# Sostituisci tutti i valori "Cape Horn" con "cpc" nella colonna "medium"
daticosto <- daticosto %>% mutate(medium = ifelse(medium == "Cape Horn", "cpc", medium))

# Unisci i dataset utilizzando la funzione merge()
metrichesito <- merge(daticosto, datisito, by = c("date"))

# Seleziona solo le colonne necessarie per il nuovo dataset
metrichesito <- metrichesito[, c("date", "totalUsers.y", "defaultChannelGroup", "advertiserAdCost", "purchaseRevenue.y")]

# Rinomina le colonne del nuovo dataset
names(metrichesito)[2] <- "utenti"
names(metrichesito)[3] <- "canale"
names(metrichesito)[4] <- "costoads"
names(metrichesito)[5] <- "ricavi"

# Ordina il dataset per data
metrichesito <- metrichesito[order(metrichesito$date),]

# Usa la funzione pivot_wider() per trasformare il dataset
metrichesito <- metrichesito %>% 
  pivot_wider(names_from = canale, values_from = c(utenti, costoads, ricavi)) %>% 
  select(date, everything())

# Usa la funzione select() per rimuovere le colonne che non servono per indice numerico
# dati_elaborati <- dati_elaborati %>% select(-c(6, 8, 9))

metrichesito <- metrichesito %>% 
  rename(
    organic = "utenti_Organic Search",
    paid = "utenti_Paid Search",
    social = "utenti_Organic Social",
    direct = "utenti_Direct",
    other = "utenti_Paid Other",
    costo = "costoads_Paid Search",
    ricaviorganic = "ricavi_Organic Search",
    ricavicpc = "ricavi_Paid Search",
    ricavisocial = "ricavi_Organic Social",
    ricavidirect = "ricavi_Direct",
    ricaviother = "ricavi_Paid Other"
  )

# Unisci con il dataset utenti utilizzando la funzione merge()
datifinali <- merge(metrichesito, utenti, by = c("date"))

# sostituire i valori NA con 0 
datifinali$social <- ifelse(is.na(datifinali$social), 0, datifinali$social)
datifinali$organic <- ifelse(is.na(datifinali$organic), 0, datifinali$organic)
datifinali$direct <- ifelse(is.na(datifinali$direct), 0, datifinali$direct)
datifinali$other <- ifelse(is.na(datifinali$other), 0, datifinali$other)
datifinali$paid <- ifelse(is.na(datifinali$paid), 0, datifinali$paid)

datifinali$costo <- ifelse(is.na(datifinali$costo), 0, datifinali$costo)

datifinali$ricavisocial <- ifelse(is.na(datifinali$ricavisocial), 0, datifinali$ricavisocial)
datifinali$ricaviother <- ifelse(is.na(datifinali$ricaviother), 0, datifinali$ricaviother)
datifinali$ricaviorganic <- ifelse(is.na(datifinali$ricaviorganic), 0, datifinali$ricaviorganic)
datifinali$ricavicpc <- ifelse(is.na(datifinali$ricavicpc), 0, datifinali$ricavicpc)


# Rirdino le colonne
datifinali <- datifinali %>%
  select(date, totalUsers, costo, purchaseRevenue, organic, paid, social, direct, other, ricaviorganic, ricavicpc, ricavisocial, ricavisocial, ricaviother)

datifinali

# impostare la zona di 2 righe per 2 colonne per i grafici
par(mfrow=c(2,2))

# produrre il primo grafico con datifinali$date in ascissa e datifinali$organic in ordinata
plot(datifinali$date, datifinali$organic, main = "Organic", xlab = "Date", ylab = "Organic", type = "l")

# produrre il secondo grafico con datifinali$date in ascissa e datifinali$paid in ordinata
plot(datifinali$date, datifinali$paid, main = "Paid", xlab = "Date", ylab = "Paid", type = "l")

# produrre il terzo grafico con datifinali$date in ascissa e datifinali$social in ordinata
plot(datifinali$date, datifinali$social, main = "Social", xlab = "Date", ylab = "Social", type = "l")

# produrre il quarto grafico con datifinali$date in ascissa e datifinali$direct in ordinata
plot(datifinali$date, datifinali$direct, main = "Direct", xlab = "Date", ylab = "Direct", type = "l")

par(mfrow=c(1,1))

# produrre il primo grafico con datifinali$date in ascissa e datifinali$organic in ordinata
plot(datifinali$date, datifinali$totalUsers, main = "Utenti", xlab = "Date", ylab = "Utenti", type = "l")

plot(datifinali$date, datifinali$purchaseRevenue, main = "Entrate", xlab = "Date", ylab = "Entrate", type = "l")


# salvare il dataset come file CSV
write.csv(datifinali, "/tmp/datifinali.csv", row.names = FALSE)


# converto gli organici in serie temporale
ts_traffico <- ts(utentiorganic$totalUsers, start = c(2022, 06), end = c(2023, 01), frequency = 7)
# applico media mobile a 7 giorni
media_mobile <- rollmean(ts_traffico, k = 7, align = "right")



# Creazione del dataframe con la serie temporale e la media mobile
df <- data.frame(data = time(ts_traffico), 
                 traffico = as.numeric(ts_traffico), 
                 media_mobile = as.numeric(media_mobile))

# Creazione del grafico
ggplot(df, aes(x = data)) + 
  geom_line(aes(y = traffico, color = "Traffico organico")) + 
  geom_line(aes(y = media_mobile, color = "Media mobile a 7 giorni")) + 
  labs(title = "Traffico organico e media mobile a 7 giorni", 
       x = "Data", y = "Numero di utenti") + 
  scale_color_manual(name = "", 
                     values = c("Traffico organico" = "blue", "Media mobile a 7 giorni" = "red"))


# Analisi di regressione multipla


# Esegui la regressione lineare multipla
model <- lm(purchaseRevenue ~ organic + paid + direct, data = datifinali)

# Visualizza il riassunto del modello
summary(model)

plot(model)


# cerco outliers
Q1 <- quantile(datifinali$totalUsers, 0.25)
Q3 <- quantile(datifinali$totalUsers, 0.75)
IQR <- Q3 - Q1
# cancello outliers
datifinali <- datifinali[datifinali$totalUsers >= lower.limit & datifinali$totalUsers <= upper.limit, ]

