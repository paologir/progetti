# Piano di Risoluzione Blocchi Server AWS - TODO

## Problemi Identificati

### 🔴 CRITICI
- [ ] **Spazio disco all'85%** - Solo 5.9GB liberi su 39GB totali
- [ ] **PHP memory_limit alto** - 512M con max_execution_time a 1000s
- [ ] **Apache MaxRequestWorkers** - 150 processi possono esaurire la RAM

### 🟡 IMPORTANTI
- [ ] **Timeout Apache** - 300 secondi è troppo alto
- [ ] **MPM Prefork** - Meno efficiente per WordPress
- [ ] **MaxConnectionsPerChild** - A 0, processi mai riciclati
- [ ] **Log non accessibili** - Permessi insufficienti per analisi
- [ ] **WordPress debug** - Probabilmente disattivato

## Azioni da Implementare

### 1. 🚨 Liberare Spazio Disco (URGENTE)
- [ ] Pulire cache WordPress in `/var/www/*/wp-content/cache/`
- [ ] Rimuovere backup vecchi dal server
- [ ] Analizzare e pulire `/var/www/*/wp-content/uploads/`
- [ ] Verificare dimensione log Apache/MySQL e implementare rotation
- [ ] Controllare file temporanei in `/tmp` e `/var/tmp`

### 2. ⚙️ Ottimizzare Configurazione Apache
- [ ] Modificare `/etc/apache2/apache2.conf`:
  - [ ] Ridurre `Timeout` da 300 a 60
  - [ ] Verificare `KeepAliveTimeout` (attualmente 5s - OK)
- [ ] Modificare `/etc/apache2/mods-enabled/mpm_prefork.conf`:
  - [ ] Ridurre `MaxRequestWorkers` da 150 a 75
  - [ ] Impostare `MaxConnectionsPerChild` a 1000
  - [ ] Valutare `StartServers` e `MinSpareServers`
- [ ] Considerare migrazione a mpm_event (richiede test)

### 3. 🐘 Ottimizzare PHP
- [ ] Modificare `/etc/php/7.4/apache2/php.ini`:
  - [ ] Ridurre `max_execution_time` da 1000 a 300
  - [ ] Verificare `memory_limit` (512M potrebbe essere OK)
  - [ ] Configurare opcache:
    - [ ] `opcache.enable=1`
    - [ ] `opcache.memory_consumption=128`
    - [ ] `opcache.max_accelerated_files=4000`
- [ ] Installare e configurare PHP-FPM come alternativa

### 4. 🔧 Configurare WordPress
- [ ] Per entrambi i siti in `/var/www/`:
  - [ ] Aggiungere in `wp-config.php`:
    ```php
    define('WP_MEMORY_LIMIT', '256M');
    define('WP_MAX_MEMORY_LIMIT', '512M');
    define('WP_DEBUG', true);
    define('WP_DEBUG_LOG', true);
    define('WP_DEBUG_DISPLAY', false);
    ```
  - [ ] Limitare revisioni post:
    ```php
    define('WP_POST_REVISIONS', 3);
    ```
- [ ] Installare plugin cache (WP Rocket/W3 Total Cache)
- [ ] Installare plugin ottimizzazione database
- [ ] Disattivare plugin non necessari

### 5. 📊 Implementare Monitoring
- [ ] AWS CloudWatch:
  - [ ] Alarm per CPU > 80%
  - [ ] Alarm per memoria > 85%
  - [ ] Alarm per disco > 90%
  - [ ] Alarm per Apache/MySQL down
- [ ] Installare strumento monitoring:
  - [ ] htop per monitoring real-time
  - [ ] netdata per dashboard web
  - [ ] Configurare notifiche email/SMS
- [ ] Log rotation:
  - [ ] Configurare logrotate per Apache
  - [ ] Configurare logrotate per MySQL
  - [ ] Configurare logrotate per WordPress

### 6. 🛡️ Azioni Preventive
- [ ] Aumentare swap:
  ```bash
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```
- [ ] Configurare restart automatico servizi:
  - [ ] Creare script systemd per auto-restart
  - [ ] Implementare health checks
- [ ] Backup:
  - [ ] Configurare backup automatici S3
  - [ ] Testare procedura di restore
- [ ] Documentare configurazione attuale

### 7. 🔍 Analisi Approfondita
- [ ] Analizzare query MySQL lente
- [ ] Verificare presenza malware/backdoor
- [ ] Controllare attacchi brute-force su wp-login
- [ ] Verificare cron jobs WordPress
- [ ] Analizzare traffico con `netstat` e `ss`

## Comandi Utili per Diagnostica

```bash
# Monitoraggio real-time
htop
iostat -x 1
watch -n 1 'free -h'

# Analisi Apache
apache2ctl -S
apache2ctl -M

# Analisi MySQL
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW STATUS LIKE 'Threads%';"

# Analisi WordPress
wp core verify --path=/var/www/fondazionecarisap.it
wp plugin list --path=/var/www/fondazionecarisap.it

# Pulizia sicura
find /var/www -name "*.log" -mtime +30 -delete
journalctl --vacuum-time=7d
```

## Priorità Implementazione

1. **IMMEDIATO**: Liberare spazio disco
2. **OGGI**: Ridurre limiti Apache/PHP
3. **QUESTA SETTIMANA**: Implementare monitoring
4. **PROSSIMA SETTIMANA**: Ottimizzare WordPress
5. **PIANIFICARE**: Migrazione a configurazione più robusta

## Note
- Testare sempre le modifiche prima in ambiente di staging
- Fare backup completo prima di ogni modifica
- Documentare ogni cambio effettuato
- Monitorare per 24-48h dopo ogni modifica