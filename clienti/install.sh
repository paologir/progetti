#!/bin/bash
# Clienti CRM - Installation Script
# Automated setup for Linux/macOS systems

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Clienti CRM"
PYTHON_MIN_VERSION="3.11"
INSTALL_DIR="$(pwd)"
VENV_NAME="venv"
LOG_FILE="install.log"

# Utility functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

print_step() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"
    log "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Header
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    CLIENTI CRM INSTALLER                    ║"
    echo "║              Sistema CRM per Digital Marketing              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_greater_equal() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Check Python version
check_python() {
    print_step "Controllo versione Python..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python non trovato. Installa Python $PYTHON_MIN_VERSION+ e riprova."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_info "Trovato Python $PYTHON_VERSION"
    
    if version_greater_equal "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        print_success "Python version OK ($PYTHON_VERSION >= $PYTHON_MIN_VERSION)"
    else
        print_error "Python $PYTHON_MIN_VERSION+ richiesto, trovato $PYTHON_VERSION"
        exit 1
    fi
}

# Check pip
check_pip() {
    print_step "Controllo pip..."
    
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_error "pip non trovato. Installa pip e riprova."
        exit 1
    fi
    
    PIP_VERSION=$($PYTHON_CMD -m pip --version | cut -d' ' -f2)
    print_success "pip trovato (versione $PIP_VERSION)"
}

# Check system dependencies
check_dependencies() {
    print_step "Controllo dipendenze sistema..."
    
    local missing_deps=()
    
    # Check for essential commands
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    if ! command_exists sqlite3; then
        missing_deps+=("sqlite3")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_warning "Dipendenze mancanti: ${missing_deps[*]}"
        print_info "Su Ubuntu/Debian: sudo apt-get install ${missing_deps[*]}"
        print_info "Su macOS: brew install ${missing_deps[*]}"
        print_info "Continuando comunque..."
    else
        print_success "Dipendenze sistema OK"
    fi
}

# Create virtual environment
create_venv() {
    print_step "Creazione ambiente virtuale..."
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Ambiente virtuale esistente trovato"
        read -p "Vuoi ricreare l'ambiente virtuale? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
            print_info "Ambiente virtuale rimosso"
        else
            print_info "Mantengo ambiente virtuale esistente"
            return 0
        fi
    fi
    
    $PYTHON_CMD -m venv "$VENV_NAME"
    print_success "Ambiente virtuale creato in $VENV_NAME/"
}

# Activate virtual environment
activate_venv() {
    print_step "Attivazione ambiente virtuale..."
    
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        print_success "Ambiente virtuale attivato"
    else
        print_error "File di attivazione non trovato: $VENV_NAME/bin/activate"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_step "Installazione dipendenze Python..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "File requirements.txt non trovato"
        exit 1
    fi
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    print_success "Dipendenze Python installate"
}

# Initialize database
init_database() {
    print_step "Inizializzazione database..."
    
    if [ -f "database.db" ]; then
        print_warning "Database esistente trovato"
        read -p "Vuoi reinizializzare il database? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mv database.db database.db.backup
            print_info "Database esistente salvato come database.db.backup"
        else
            print_info "Database esistente mantenuto"
            return 0
        fi
    fi
    
    python clienti.py init
    print_success "Database inizializzato"
}

# Run basic tests
run_tests() {
    print_step "Test di base del sistema..."
    
    # Test help command
    if python clienti.py --help >/dev/null 2>&1; then
        print_success "Test help command: OK"
    else
        print_error "Test help command: FAILED"
        return 1
    fi
    
    # Test version command  
    if python clienti.py version >/dev/null 2>&1; then
        print_success "Test version command: OK"
    else
        print_error "Test version command: FAILED"
        return 1
    fi
    
    # Test database info
    if python clienti.py info >/dev/null 2>&1; then
        print_success "Test database: OK"
    else
        print_error "Test database: FAILED"
        return 1
    fi
    
    print_success "Tutti i test di base superati"
}

# Create alias script
create_alias() {
    print_step "Configurazione alias comando..."
    
    local script_dir="$(dirname "$0")"
    local full_path="$(realpath "$script_dir")"
    local alias_script="/usr/local/bin/clienti"
    
    # Try to create global alias
    if [ -w "/usr/local/bin" ]; then
        cat > "$alias_script" << EOF
#!/bin/bash
cd "$full_path"
source venv/bin/activate
python clienti.py "\$@"
EOF
        chmod +x "$alias_script"
        print_success "Alias globale creato: /usr/local/bin/clienti"
    else
        # Create local alias suggestion
        local bashrc_alias="alias clienti='$full_path/venv/bin/python $full_path/clienti.py'"
        
        print_warning "Non posso creare alias globale (permessi insufficienti)"
        print_info "Aggiungi questo al tuo ~/.bashrc o ~/.zshrc:"
        echo -e "${GREEN}$bashrc_alias${NC}"
        
        # Offer to add to bashrc
        if [ -f "$HOME/.bashrc" ]; then
            read -p "Vuoi che aggiunga l'alias al tuo ~/.bashrc? (y/N): " -r
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "" >> "$HOME/.bashrc"
                echo "# Clienti CRM alias" >> "$HOME/.bashrc"
                echo "$bashrc_alias" >> "$HOME/.bashrc"
                print_success "Alias aggiunto a ~/.bashrc"
                print_info "Esegui 'source ~/.bashrc' o riavvia il terminale"
            fi
        fi
    fi
}

# Create logs directory
create_directories() {
    print_step "Creazione directory necessarie..."
    
    mkdir -p logs
    mkdir -p data/backups
    mkdir -p templates/obsidian
    
    print_success "Directory create"
}

# Show completion message
show_completion() {
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   INSTALLAZIONE COMPLETATA!                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}🎉 $PROJECT_NAME è stato installato con successo!${NC}"
    echo ""
    echo -e "${BLUE}Per iniziare:${NC}"
    
    if [ -f "/usr/local/bin/clienti" ]; then
        echo -e "${GREEN}  clienti --help          ${NC}# Mostra tutti i comandi"
        echo -e "${GREEN}  clienti dashboard       ${NC}# Dashboard principale"
        echo -e "${GREEN}  clienti client add      ${NC}# Aggiungi primo cliente"
        echo -e "${GREEN}  clienti serve           ${NC}# Interfaccia web"
    else
        echo -e "${GREEN}  ./venv/bin/python clienti.py --help     ${NC}# Mostra tutti i comandi"
        echo -e "${GREEN}  ./venv/bin/python clienti.py dashboard  ${NC}# Dashboard principale"
        echo -e "${YELLOW}  # Oppure aggiungi l'alias suggerito sopra${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Interfaccia Web:${NC}"
    echo -e "${GREEN}  clienti serve            ${NC}# Avvia su http://127.0.0.1:8080"
    echo ""
    echo -e "${BLUE}Documentazione:${NC}"
    echo -e "${GREEN}  README.md                ${NC}# Guida completa"
    echo -e "${GREEN}  clienti --help           ${NC}# Help contestuale"
    echo -e "${GREEN}  config.toml              ${NC}# Configurazione"
    echo ""
    echo -e "${BLUE}File importanti:${NC}"
    echo -e "${GREEN}  database.db              ${NC}# Database SQLite"
    echo -e "${GREEN}  logs/clienti.log         ${NC}# Log applicazione"
    echo -e "${GREEN}  data/backups/            ${NC}# Backup automatici"
    echo ""
    echo -e "${YELLOW}Nota: Prima di utilizzare in produzione, leggi README.md per configurazione avanzata.${NC}"
}

# Main installation function
main() {
    clear
    print_header
    
    # Start logging
    echo "=== CLIENTI CRM INSTALLATION LOG ===" > "$LOG_FILE"
    log "Installation started"
    log "Install directory: $INSTALL_DIR"
    log "Python command: ${PYTHON_CMD:-unknown}"
    
    # Pre-flight checks
    check_python
    check_pip
    check_dependencies
    
    # Create directories
    create_directories
    
    # Virtual environment setup
    create_venv
    activate_venv
    
    # Install dependencies
    install_dependencies
    
    # Initialize system
    init_database
    
    # Run tests
    run_tests
    
    # Create command alias
    create_alias
    
    # Show completion
    show_completion
    
    log "Installation completed successfully"
    
    exit 0
}

# Error handling
trap 'print_error "Installazione fallita. Controlla $LOG_FILE per dettagli."; exit 1' ERR

# Run main installation
main "$@"