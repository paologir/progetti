# Quanti utenti unici in totale hanno visitato il sito
# nel mese in esame

# Define default values
default_n <- 9723
default_k <- 49

# Check for command-line arguments
args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 2) {
  # Use command-line arguments if provided
  n <- as.numeric(args[1])
  k <- as.numeric(args[2])
  cat("Using command-line arguments: n =", n, ", k =", k, "\n")
} else if (interactive()) {
  # If no command-line arguments and running interactively, ask user for input
  use_default <- readline(prompt = paste("Do you want to use default values (n=", default_n, ", k=", default_k, ")? (yes/no): "))

  if (tolower(use_default) == "yes") {
    n <- default_n
    k <- default_k
    cat("Using default values: n =", n, ", k =", k, "\n")
  } else {
    # Get input from user interactively
    n <- as.numeric(readline(prompt = "Enter the total number of unique users (n): "))
    k <- as.numeric(readline(prompt = "Enter the number of users who generated a conversion (k): "))
  }
} else {
  # If not interactive and no command-line args, use defaults and warn
  n <- default_n
  k <- default_k
  cat("No command-line arguments or interactive session detected. Using default values: n =", n, ", k =", k, ".\n")
}

# Validate input values
if (is.na(n) || is.na(k) || n <= 1 || k <= 0 || k >= n) {
  cat("Errore: Valori di input non validi per n o k.\n")
  cat("Assicurati che n e k siano numeri validi e che 0 < k < n.\n")
  quit(save="no", status=1)
}

# Quanti utenti NON hanno generato una conversione, quindi n-k
beta <- n - k
# Calcolo il tasso di conversione medio 
conv <- k / n

# Plotto la distribuzione beta della probabilità di conversione
# Ensure the range for xs is valid after input validation
if (k > 0 && n > k) {
  # Adjust the range for xs dynamically based on the conversion rate if needed, or keep a sensible default
  # For now, keep the existing range as it seems reasonable for small conversion rates
  # xs <- seq(max(0.0001, conv - 3*sqrt(conv*(1-conv)/n)), min(0.9999, conv + 3*sqrt(conv*(1-conv)/n)), by=0.0001)
  xs <- seq(0.001,0.03,by=0.0001)
  
  # Ensure xs has valid range for plotting after input validation
  if(length(xs) > 1 && min(xs) < max(xs)) {
    plot(xs, dbeta(xs, k, beta), type="l", lwd=3,
         ylab="densità",
         xlab="probabilità di conversione",
         main="PDF Beta")
  } else {
    cat("Attenzione: Impossibile creare il grafico. L'intervallo per xs non è valido.\n")
  }
} else {
    cat("Attenzione: Impossibile creare il grafico. I valori di input n e k non sono validi per il calcolo della distribuzione beta.\n")
}

# Calcolo l'intervallo di confidenza al 95%
ci <- qbeta(c(0.025, 0.975), k, beta)

cat("Tasso medio di conversione = ", round(conv * 100,2), "%\n")

cat("Intervallo di confidenza al 95%: [", round(ci[1] * 100, 2), "%, ", round(ci[2] * 100, 2), "%]\n")


beta99 <- qbeta(0.999, k, beta)
cat("Il 99% delle conversioni è inferiore a = ", round(beta99 * 100,2), "%\n")
