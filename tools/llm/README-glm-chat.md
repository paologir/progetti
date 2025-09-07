# GLM-4.5 Flash Chat CLI

Un'interfaccia chat da terminale confortevole e ben progettata per interagire con il modello GLM-4.5-flash tramite API.

## Caratteristiche

- 🎨 **Interfaccia colorata**: Distinzione chiara tra prompt utente e risposte AI
- 💬 **Conversazione multiturno**: Mantiene la cronologia della conversazione
- 🎯 **System prompt personalizzabile**: Imposta il comportamento dell'AI all'avvio
- 📋 **Salvataggio flessibile**: Copia risposte nella clipboard o salva su file
- 📝 **Input multilinea**: Supporto per messaggi complessi su più righe
- ⚡ **Streaming in tempo reale**: Visualizza le risposte mentre vengono generate
- 🔧 **Comandi speciali**: `/exit`, `/clear`, `/system`, `/save`

## Installazione

### Metodo Automatico (Consigliato)

Usa lo script di setup che gestisce automaticamente l'ambiente virtuale:

```bash
# 1. Esegui il setup (solo la prima volta)
./setup-glm-chat.sh

# 2. Usa il launcher per avviare la chat
./glm-chat-launcher
```

### Metodo Manuale (Ambiente Virtuale)

Se preferisci gestire manualmente l'ambiente virtuale:

```bash
# Crea ambiente virtuale
python3 -m venv .venv-glm

# Attiva ambiente virtuale
source .venv-glm/bin/activate

# Installa dipendenze
pip install -r requirements-glm.txt

# Esegui
python3 glm-chat
```

2. **Configura la chiave API**:

Puoi configurare la chiave API in due modi:

**Opzione A - Variabile d'ambiente** (consigliato):
```bash
export GLM_API_KEY="tua-chiave-api"
# oppure
export ZAI_API_KEY="tua-chiave-api"
```

**Opzione B - Input interattivo**: Il programma ti chiederà la chiave se non la trova nell'ambiente.

Per ottenere una chiave API, registrati su https://z.ai/manage-apikey/apikey-list

## Utilizzo

```bash
# Se hai usato il setup automatico
./glm-chat-launcher

# O se hai attivato manualmente il venv
source .venv-glm/bin/activate
python3 glm-chat
```

## Comandi Disponibili

### Modalità di Input

- **Messaggio normale**: Scrivi e premi Invio per inviare subito
- **Messaggio multilinea**: Termina la prima riga con `\` per entrare in modalità multilinea, poi usa `EOF` per inviare

### Comandi Speciali

- `/exit` - Esci dalla chat (invio immediato)
- `/clear` - Pulisci la cronologia della conversazione
- `/system` - Cambia il system prompt
- `/save` - Salva l'intera conversazione in un file Markdown

## Esempio di Utilizzo

```
╔════════════════════════════════════════════════════════════╗
║              GLM-4.5 Flash Chat CLI Interface              ║
║                                                            ║
║  Commands:                                                 ║
║  /exit     - Exit the chat                                ║
║  /clear    - Clear conversation history                    ║
║  /system   - Change system prompt                          ║
║  /save     - Save entire conversation to file              ║
║  \         - Add backslash for multiline input             ║
╚════════════════════════════════════════════════════════════╝

Would you like to set a custom system prompt? (y/n):
> y
Enter your system prompt (type 'EOF' on a new line to finish):
Sei un assistente esperto in programmazione Python. 
Rispondi in modo conciso e con esempi di codice quando appropriato.
EOF
✓ System prompt set

Chat started. Press Enter to send, add \ for multiline.

You> Come posso leggere un file JSON in Python?

GLM> Per leggere un file JSON in Python, usa il modulo `json`:

```python
import json

# Lettura del file JSON
with open('data.json', 'r') as file:
    data = json.load(file)

print(data)
```

Save response? (c=clipboard, f=file, n=no):
> c
✓ Response copied to clipboard
```

## Funzionalità Dettagliate

### System Prompt Personalizzabile
All'avvio puoi impostare un system prompt per definire il comportamento dell'AI. Questo è utile per:
- Definire un ruolo specifico (es. "Sei un esperto di Python")
- Impostare uno stile di risposta (es. "Rispondi in modo conciso")
- Aggiungere contesto persistente

### Input Multilinea
Per messaggi complessi o codice:
1. Scrivi il tuo messaggio e termina con `\`
2. Continua a scrivere su più righe
3. Scrivi `EOF` su una nuova riga per inviare

Esempio:
```
You> Ecco il mio codice Python:\
(multiline mode - type 'EOF' alone to send)
... def hello():
...     print("Hello World")
... EOF
```

### Salvataggio Risposte
Dopo ogni risposta, puoi:
- **c**: Copiare nella clipboard
- **f**: Salvare in un file (ti verrà chiesto il nome)
- **n**: Non salvare

### Esportazione Conversazione
Usa `/save` per salvare l'intera conversazione in formato Markdown con:
- Timestamp
- System prompt utilizzato
- Tutti i turni di conversazione formattati

## Modelli Supportati

Per default usa `glm-4.5-flash`, ma supporta tutti i modelli GLM disponibili tramite l'API Z.AI:
- glm-4.5-flash (raccomandato per velocità)
- glm-4.5
- glm-4.5-air

## Troubleshooting

### "API key not found"
Assicurati di aver configurato la chiave API come variabile d'ambiente o inseriscila quando richiesto.

### "zai-sdk not installed"
Installa il SDK con: `pip install zai-sdk`

### Errori di connessione
Verifica:
1. La connessione internet
2. La validità della chiave API
3. I limiti di rate della tua chiave

## Note

- Le conversazioni non sono salvate automaticamente tra sessioni
- Usa `/save` prima di uscire se vuoi conservare la conversazione
- Il modello GLM-4.5-flash è ottimizzato per risposte rapide mantenendo alta qualità