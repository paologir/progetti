# Carico le librerie
library(googleAnalyticsR)
library(dplyr)
library(tidyr)
library(ggplot2)
library(UsingR)
library(outliers)
library(moments)
library(zoo)

###################
# Recupero i dati #
###################

# Autorizzo Google Analytics. 
ga_auth()

my_property_id <- "284950831"

# Scelgo la data di inizio
# Scelgo la data di fine
datainizio <- "2021-10-01"
datafine <- "2023-02-28"

# Imposta i parametri di query
datiweb <- ga_data(
  my_property_id,
  date_range = c(datainizio, datafine),
  dimensions = c("date","firstUserMedium"),
  dim_filters = ga_data_filter(firstUserMedium=="organic"),
  metrics = c("totalUsers"),
  orderBys = ga_data_order(+date),
  limit = -1,
)

datiweb <- datiweb [,-2]
datiweb <- rename(datiweb, data = date, utenti = totalUsers) 

write.csv(datiweb, "/tmp/utentimaspe.csv", row.names = FALSE)

ggplot(datiweb, aes(x = data, y = utenti)) +
  geom_line() +
  labs(x = "Data", y = "Utenti", title = "Andamento degli utenti nel tempo")

# dati basici
mean(datiweb$utenti)
fivenum(datiweb$utenti)
hist(datiweb$utenti)
boxplot(datiweb$utenti)

# cerco outliers
Q1 <- quantile(datiweb$utenti, 0.25)
Q3 <- quantile(datiweb$utenti, 0.75)
IQR <- Q3 - Q1
cat("IQR=",IQR)
#calcolo dei limiti di accettabilità per gli outliers
lower_limit <- Q1 - 1.5*IQR
upper_limit <- Q3 + 1.5*IQR

# stampa i limiti outliers
cat("Limiti outliers: ", lower_limit, " - ", upper_limit)

simple.eda(datiweb$utenti)

# sostituisco gli outliers con la mediana e creo un nuovo dataframe
pulita_utenti <- rm.outlier(datiweb$utenti, fill = TRUE, median=TRUE, opposite = FALSE)
pulita <- data_frame(datiweb$data, pulita_utenti)
names(pulita) <- c("data", "utenti")
simple.eda(pulita$utenti)

cat("Test di normalita' di Shapiro Wilk. (p < 0.1 adeguato)")
shapiro.test(datiweb$utenti)
shapiro.test(pulita$utenti)

# asimmetria della distribuzione
# 0=simmetrica, >0 asimmetria destra, <0 asimmetria sinistra
# i valori sono in genere compresi tra -3 e 3
asimmetria=skewness(pulita$utenti)
print(asimmetria)
if (asimmetria < 0) { cat ('La distribuzione presenta asimmetria sinistra')
} else if(asimmetria > 0) {cat('La distribuzione presenta asimmetria destra')
} else {cat('distribuzione perfettamente normale')}

# curtosi della distribuzione
# <3 platicurtica, =3 mesocurtica, >3 leptocurtica
curtosi=kurtosis(pulita$utenti)
print(curtosi)
if (curtosi < 3) { cat ('distribuzione platicurtica')
} else if(curtosi > 3) {cat('distribuzione leptocurtica')
} else {cat('distribuzione perfettamente normale')}

# qui scelgo 12,5% e 87,5%
cat("Calcolo l'intervallo tra i quantili 12,5% e 87,5%")
quantile(pulita$utenti, probs = c(0.125,0.875))

ggplot(data=pulita,aes(x=data,y=utenti))  + 
  geom_smooth() +
  labs(x="giorni",y="utenti",title="utenti temporale", subtitle="andamento temporale - smoothing")

# trasformo il dataset in ts
mydata <- ts(datiweb[,-1], frequency = 365, start = c(2021, 10, 01))
plot.ts(mydata)

# calcolo le medie mobili a 7 e 30 giorni
mm7g <- rollmean(pulita$utenti,7)
# mm7g

mm30g <- rollmean(pulita$utenti,30)
# mm30g

mm90g <- rollmean(pulita$utenti,90)
# mm90g


# le disegno sul grafico
par(mfrow=c(1,1))
plot(mm7g, type="l", lwd="3", main="Medie mobili a 7, 30 e 90 giorni", xlab="tempo",ylab="utenti")
lines(mm30g, type="l", lwd="3",col="red")
lines(mm90g, type="l", lwd="3",col="green")
# aggiungo la legenda
legend("topright", text.font=1, legend=c("media 7g", "media 30g", "media 90g"),
       col=c("black", "red", "green"), lty=1, cex=0.8)

# guardo le 3 medie mobili 
par(mfrow=c(3,1))
plot(mm7g, type="l", main="Media mobile a 7 giorni", xlab="tempo",ylab="utenti")
plot(mm30g, type="l", main="Media mobile a 30 giorni", xlab="tempo",ylab="utenti")
plot(mm90g, type="l", main="Media mobile a 90 giorni", xlab="tempo",ylab="utenti")
par(mfrow=c(1,1))

# traccio i boxplot raggruppati per mese. Assegno un colore ad ogni mese per
# un facile confronto
boxplot(pulita$utenti ~ reorder(format(pulita$data,'%b %y'),pulita$data), outline = FALSE, main="Boxplot mensile - segmento organico", xlab="data", ylab="utenti", col=(c("gold","green","blue","black","red","orange","cyan","darkgrey","deeppink","coral","brown","aliceblue"))) 
