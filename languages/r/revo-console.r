# Carico le librerie
library(googleAnalyticsR)
library(txtplot)
library(dplyr)
# Mi autentico con JSON service account
ga_auth(
  json_file = '/opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json'
)


# scelgo una proprieta'
my_property_id <- 395174045 # Revo

# Scelgo il range di date
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


basic <- basic %>%
  mutate(id_progressivo = row_number())
basic <- rename(basic,data = date)

# Unisci il dataframe 'costi' con il dataframe di date
revo <- merge(basic, organici, by = "data", all.x = TRUE)

# Sostituisci i valori NA con 0
revo$organici[is.na(revo$organici)] <- 0

revo <- revo[-4]

# clear screen
cat("\u001B[2J")

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
cat("\u001B[31mUtenti Revo\u001B[0m\n")
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
revo$day_of_week <- weekdays(revo$data, abbreviate = FALSE)


cat("\nSalvo i dati nel file revo-dati.csv\n\n")

write.csv(revo, file = "/tmp/revo-dati.csv")
