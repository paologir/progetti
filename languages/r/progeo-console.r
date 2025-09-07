# Carico le librerie necessarie
library(googleAnalyticsR)
library(dplyr)
library(ggplot2)
library(lubridate)
library(gridExtra)
library(moments)  # For skewness and kurtosis

# Funzione per l'autenticazione
authenticate_ga <- function() {
  tryCatch({
    ga_auth(
      json_file = '/opt/lavoro/maspe/api/alpine-surge-458108-h6-bf4746d1a5b7.json'
    )
    cat("Autenticazione riuscita.\n")
  }, error = function(e) {
    stop("Errore di autenticazione: ", e$message)
  })
}

# Funzione per l'input dell'utente
get_user_input <- function(prompt) {
  cat(prompt)
  readLines("stdin", n = 1)
}

# Funzione per selezionare la proprietà
select_property <- function() {
  properties <- c("nutrizione.com" = "321354469", "nutriverso" = "417933178", 
                  "progeo medical" = "321316124", "progeo shop" = "363800143")
  cat("Seleziona una proprietà:\n")
  for (i in seq_along(properties)) {
    cat(i, "-", names(properties)[i], "\n")
  }
  choice <- as.numeric(get_user_input("Inserisci il numero della proprietà: "))
  if (is.na(choice) || choice < 1 || choice > length(properties)) {
    stop("Scelta non valida.")
  }
  return(properties[choice])
}

# Funzione per selezionare il livello di raggruppamento
select_grouping <- function() {
  grouping_levels <- c("Giorno" = "day", "Settimana" = "week", "Mese" = "month")
  cat("Seleziona il livello di raggruppamento:\n")
  for (i in seq_along(grouping_levels)) {
    cat(i, "-", names(grouping_levels)[i], "\n")
  }
  choice <- as.numeric(get_user_input("Inserisci il numero della scelta: "))
  if (is.na(choice) || choice < 1 || choice > length(grouping_levels)) {
    stop("Scelta non valida.")
  }
  return(grouping_levels[choice])
}

# Funzione per verificare la validità delle date
validate_dates <- function(start_date, end_date) {
  if (!is.Date(start_date) || !is.Date(end_date)) {
    stop("Le date devono essere nel formato YYYY-MM-DD.")
  }
  if (start_date > end_date) {
    stop("La data di inizio deve essere precedente alla data di fine.")
  }
}

# Funzione per recuperare i dati da Google Analytics
fetch_ga_data <- function(property_id, start_date, end_date) {
  tryCatch({
    basic <- ga_data(
      property_id,
      metrics = c("totalUsers", "sessions", "conversions"),
      dimensions = c("date"),
      date_range = c(start_date, end_date),
      limit = -1,
      orderBys = ga_data_order(+date)
    )
    
    organici <- ga_data(
      property_id,
      date_range = c(start_date, end_date),
      dimensions = c("date", "firstUserMedium"),
      dim_filters = ga_data_filter(firstUserMedium == "organic"),
      metrics = c("totalUsers"),
      orderBys = ga_data_order(+date),
      limit = -1
    )
    
    list(basic = basic, organici = organici)
  }, error = function(e) {
    stop("Errore nel recupero dei dati: ", e$message)
  })
}

# Funzione per elaborare i dati
process_data <- function(basic, organici, grouping) {
  basic <- basic %>%
    mutate(data = as.Date(date),
           id_progressivo = row_number()) %>%
    select(id_progressivo, data, totalUsers, sessions, conversions)
  
  organici <- organici %>%
    select(-firstUserMedium) %>%
    rename(organici = totalUsers) %>%
    mutate(data = as.Date(date))
  
  data <- merge(basic, organici, by = "data", all.x = TRUE) %>%
    mutate(organici = coalesce(organici, 0),
           day_of_week = wday(data, label = TRUE, abbr = FALSE))
  
  if (grouping == "week") {
    data <- data %>%
      mutate(week = week(data)) %>%
      group_by(week) %>%
      summarise(id_progressivo = first(id_progressivo),
                data = first(data),
                totalUsers = sum(totalUsers),
                organici = sum(organici),
                sessions = sum(sessions),
                conversions = sum(conversions),
                day_of_week = first(day_of_week))
  } else if (grouping == "month") {
    data <- data %>%
      mutate(month = floor_date(data, "month")) %>%
      group_by(month) %>%
      summarise(id_progressivo = first(id_progressivo),
                data = first(data),
                totalUsers = sum(totalUsers),
                organici = sum(organici),
                sessions = sum(sessions),
                conversions = sum(conversions))
  }
  
  data
}

# Funzione per analizzare e visualizzare i dati
analyze_and_visualize <- function(data, start_date, end_date, property_name, grouping) {
  cat("\n============\n")
  cat("Analisi dati", property_name, "\n")
  cat("============\n\n")
  cat("Periodo: da", start_date, "a", end_date, "\n")
  cat("Raggruppamento:", grouping, "\n")
  cat("---------------------------\n")
  
  # Statistiche descrittive
  summary_stats <- summary(data$totalUsers)
  print(summary_stats)
  
  # Skewness and Kurtosis
  skew <- skewness(data$totalUsers)
  kurt <- kurtosis(data$totalUsers)
  cat("\nSkewness:", skew, "\n")
  if (skew < 0) {
    cat("La distribuzione presenta asimmetria sinistra.\n")
  } else if (skew > 0) {
    cat("La distribuzione presenta asimmetria destra.\n")
  } else {
    cat("La distribuzione è simmetrica.\n")
  }
  
  cat("\nKurtosis:", kurt, "\n")
  if (kurt < 3) {
    cat("Distribuzione platicurtica.\n")
  } else if (kurt > 3) {
    cat("Distribuzione leptocurtica.\n")
  } else {
    cat("Distribuzione mesocurtica.\n")
  }
  
  # Quantile calculations
  quantiles <- quantile(data$totalUsers, probs = c(0.125, 0.875))
  cat("\nQuantili 12.5% e 87.5%:\n")
  print(quantiles)
  
  # Bayesian analysis for conversion rates
  total_visitors <- sum(data$totalUsers)
  total_conversions <- sum(data$conversions)
  
  alpha <- total_conversions + 1
  beta <- total_visitors - total_conversions + 1
  
  ci <- qbeta(c(0.025, 0.975), alpha, beta)
  lower_percent <- round(ci[1] * 100, 2)
  upper_percent <- round(ci[2] * 100, 2)
  
  cat("\nStima percentuale conversione bayesiana:\n")
  cat("Totali accumulati:\n")
  cat("Utenti totali:", total_visitors, "\n")
  cat("Conversioni totali:", total_conversions, "\n")
  cat("Intervallo credibile al 95%: [", lower_percent, "%, ", upper_percent, "%]\n")
  
  # Outlier detection
  Q1 <- quantile(data$totalUsers, 0.25)
  Q3 <- quantile(data$totalUsers, 0.75)
  IQR <- Q3 - Q1
  cat("\nIQR:", IQR, "\n")
  lower_limit <- Q1 - 1.5 * IQR
  upper_limit <- Q3 + 1.5 * IQR
  cat("Limiti outliers:", lower_limit, "-", upper_limit, "\n")
  
  # Creazione dei grafici
  p1 <- plot_time_series(data, grouping)
  if (grouping == "month") {
    p2 <- plot_monthly_boxplots(data)
  } else {
    p2 <- plot_boxplot(data, grouping)
  }
  if (grouping == "week") {
    p3 <- plot_weekly_trend(data, grouping)
  } else {
    p3 <- ggplot()  # Placeholder plot
  }
  p4 <- plot_organic_vs_total(data, start_date, end_date, grouping)
  p5 <- plot_qqplot(data)
  p6 <- plot_histogram(data)
  
  # Salvataggio dei grafici in un unico file PDF
  pdf_path <- paste0("/tmp/grafici-", property_name, "-", grouping, ".pdf")
  pdf(pdf_path, width = 12, height = 16)
  grid.arrange(p1, p2, p3, p4, p5, p6, ncol = 2)
  dev.off()
  
  cat("\nGrafici salvati in:", pdf_path, "\n")
}

# Funzione per creare il grafico della serie temporale
plot_time_series <- function(data, grouping) {
  ggplot(data, aes(x = data, y = totalUsers)) +
    geom_line(color = "#0072B2", linewidth = 1) +
    geom_smooth(method = "loess", color = "#D55E00", se = FALSE) +
    labs(title = "Serie temporale degli utenti totali",
         subtitle = paste("Raggruppamento:", grouping),
         x = "Data", y = "Utenti totali") +
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", size = 14),
          plot.subtitle = element_text(size = 12),
          axis.title = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1))
}

# Funzione per creare il boxplot generale
plot_boxplot <- function(data, grouping) {
  ggplot(data, aes(y = totalUsers)) +
    geom_boxplot(fill = "#56B4E9", color = "#0072B2") +
    labs(title = "Distribuzione degli utenti totali",
         y = "Utenti totali") +
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", size = 14),
          axis.title = element_text(face = "bold"))
}

# Funzione per creare i boxplot mensili
plot_monthly_boxplots <- function(data) {
  data_monthly <- data %>%
    mutate(month = floor_date(data, "month")) %>%
    mutate(month = as.character(month))
  
  ggplot(data_monthly, aes(y = totalUsers)) +
    geom_boxplot() +
    facet_wrap(~ month, scales = "free") +
    labs(title = "Boxplot mensile degli utenti totali",
         y = "Utenti totali") +
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", size = 14),
          axis.title = element_text(face = "bold"))
}

# Funzione per creare il grafico del trend settimanale
plot_weekly_trend <- function(data, grouping) {
  if (grouping == "week") {
    data <- data %>%
      group_by(day_of_week) %>%
      summarise(avg_users = mean(totalUsers))
    
    ggplot(data, aes(x = day_of_week, y = avg_users)) +
      geom_bar(stat = "identity", fill = "#009E73") +
      labs(title = "Media utenti per giorno della settimana",
           x = "Giorno della settimana", y = "Media utenti") +
      theme_minimal() +
      theme(plot.title = element_text(face = "bold", size = 14),
            axis.title = element_text(face = "bold"),
            axis.text.x = element_text(angle = 45, hjust = 1))
  } else {
    ggplot()  # Placeholder plot
  }
}

# Funzione per creare il grafico degli utenti organici vs totali
plot_organic_vs_total <- function(data, start_date, end_date, grouping) {
  ggplot(data, aes(x = data)) +
    geom_line(aes(y = totalUsers, color = "Totali"), linewidth = 1) +
    geom_line(aes(y = organici, color = "Organici"), linewidth = 1) +
    labs(title = "Utenti totali vs Utenti organici",
         subtitle = paste("Periodo:", start_date, "al", end_date, "\nRaggruppamento:", grouping),
         x = "Data", y = "Numero di utenti", color = "Tipo di utenti") +
    scale_color_manual(values = c("Totali" = "#0072B2", "Organici" = "#D55E00")) +
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", size = 14),
          plot.subtitle = element_text(size = 12),
          axis.title = element_text(face = "bold"),
          axis.text.x = element_text(angle = 45, hjust = 1),
          legend.position = "bottom")
}

# Funzione per creare il Q-Q plot
plot_qqplot <- function(data) {
  ggplot(data, aes(sample = totalUsers)) +
    geom_qq() +
    geom_qq_line() +
    labs(title = "Q-Q Plot per normalità degli utenti totali",
         x = "Quantili teorici", y = "Quantili empirici") +
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", size = 14),
          axis.title = element_text(face = "bold"))
}

# Funzione per creare l'istogramma
plot_histogram <- function(data) {
  ggplot(data, aes(x = totalUsers)) +
    geom_histogram(binwidth = 100, fill = "#56B4E9", color = "#0072B2") +
    labs(title = "Distribuzione degli utenti totali",
         x = "Utenti totali", y = "Frequenza") +
    theme_minimal() +
    theme(plot.title = element_text(face = "bold", size = 14),
          axis.title = element_text(face = "bold"))
}

# Funzione per salvare i dati
save_data <- function(data, property_name, grouping) {
  file_path <- paste0("/tmp/", property_name, "-", grouping, "-data.csv")
  write.csv(data, file = file_path, row.names = FALSE)
  cat("\nDati salvati in:", file_path, "\n")
}

# Funzione principale
main <- function() {
  # Autenticazione
  authenticate_ga()
  
  # Selezione della proprietà
  property_id <- select_property()
  property_name <- names(property_id)
  property_id <- unname(property_id)
  
  # Selezione del raggruppamento
  grouping <- select_grouping()
  
  # Input date
  start_date <- as.Date(get_user_input("Inserisci data inizio (YYYY-MM-DD): "))
  end_date <- as.Date(get_user_input("Inserisci data fine (YYYY-MM-DD): "))
  
  # Validazione delle date
  validate_dates(start_date, end_date)
  
  # Recupero dati
  data <- fetch_ga_data(property_id, start_date, end_date)
  
  # Elaborazione dati
  data_processed <- process_data(data$basic, data$organici, grouping)
  
  # Analisi e visualizzazione
  analyze_and_visualize(data_processed, start_date, end_date, property_name, grouping)
  
  # Salvataggio dati
  save_data(data_processed, property_name, grouping)
}

# Esecuzione dello script
main()
