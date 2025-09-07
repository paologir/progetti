#!/bin/bash

# Imposta le variabili d'ambiente
export OPENAI_API_BASE="http://localhost:8080/v1"
export OPENAI_API_KEY="na"

# Esegui il comando aider con le opzioni specificate
aider --model openai/devstral --no-show-model-warnings
