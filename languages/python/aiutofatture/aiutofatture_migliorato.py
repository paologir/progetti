#!/usr/bin/env python3

import os
import json
import sys
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime


@dataclass
class Voce:
    """Rappresenta una voce di fattura/avviso"""
    descrizione: str
    importo: Decimal
    
    def __str__(self):
        return f"{self.descrizione}: €{self.importo:.2f}"


@dataclass
class Cliente:
    """Rappresenta un cliente"""
    nome: str
    cf: str
    piva: str
    indirizzo: str
    citta: str
    cap: str
    provincia: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            nome=data.get('Cliente', ''),
            cf=data.get('CF', ''),
            piva=data.get('PIVA', ''),
            indirizzo=data.get('Indirizzo', ''),
            citta=data.get('Città', ''),
            cap=data.get('CAP', ''),
            provincia=data.get('Provincia', '')
        )


class GestoreClienti:
    """Gestisce il caricamento e la selezione dei clienti"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.clienti: List[Cliente] = []
        
    def carica_clienti(self) -> bool:
        """Carica i clienti dal file JSON"""
        try:
            if not os.path.exists(self.file_path):
                print(f"Errore: File {self.file_path} non trovato")
                return False
                
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.clienti = [Cliente.from_dict(c) for c in data.get('clienti', [])]
                return True
        except json.JSONDecodeError as e:
            print(f"Errore nel parsing del file JSON: {e}")
            return False
        except Exception as e:
            print(f"Errore nel caricamento clienti: {e}")
            return False
            
    def seleziona_cliente(self) -> Optional[Cliente]:
        """Permette all'utente di selezionare un cliente"""
        if not self.clienti:
            print("Nessun cliente disponibile")
            return None
            
        print("\nSeleziona un cliente:")
        for i, cliente in enumerate(self.clienti):
            print(f"{i + 1}. {cliente.nome}")
            
        while True:
            try:
                scelta = input("\nInserisci il numero del cliente (0 per annullare): ")
                if scelta == '0':
                    return None
                    
                indice = int(scelta) - 1
                if 0 <= indice < len(self.clienti):
                    return self.clienti[indice]
                else:
                    print("Numero non valido. Riprova.")
            except ValueError:
                print("Inserire un numero valido.")


class GestoreFatture:
    """Gestisce la creazione di fatture e avvisi"""
    
    CONTI = {
        1: "Unicredit banca - IBAN: IT86W0200860900000003387471 - BIC: UNCRITM1XXX",
        2: "Fideuram - IBAN: IT04D0329601601000067433373 - BIC: FIDEITM1XXX"
    }
    
    def __init__(self, voci_preimpostate_path: str):
        self.voci_preimpostate_path = voci_preimpostate_path
        self.voci_preimpostate: List[str] = []
        self.voci: List[Voce] = []
        
    def carica_voci_preimpostate(self) -> bool:
        """Carica le voci preimpostate dal file"""
        try:
            if os.path.exists(self.voci_preimpostate_path):
                with open(self.voci_preimpostate_path, 'r', encoding='utf-8') as file:
                    self.voci_preimpostate = [line.strip() for line in file if line.strip()]
                return True
            else:
                print(f"File {self.voci_preimpostate_path} non trovato. Continuo senza voci preimpostate.")
                return True
        except Exception as e:
            print(f"Errore nel caricamento voci preimpostate: {e}")
            return False
            
    def _input_importo(self, prompt: str = "Inserisci l'importo: €") -> Optional[Decimal]:
        """Richiede l'inserimento di un importo valido"""
        while True:
            try:
                valore = input(prompt).replace(',', '.')
                if not valore:
                    return None
                    
                importo = Decimal(valore)
                if importo < 0:
                    print("L'importo non può essere negativo.")
                    continue
                    
                return importo.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except:
                print("Importo non valido. Usa il formato: 123.45")
                
    def seleziona_voce_preimpostata(self) -> Optional[str]:
        """Permette di selezionare una voce preimpostata"""
        if not self.voci_preimpostate:
            return None
            
        print("\nVoci preimpostate disponibili:")
        for i, voce in enumerate(self.voci_preimpostate):
            print(f"{i + 1}. {voce}")
            
        print("0. Inserisci una nuova voce")
        
        while True:
            try:
                scelta = input("\nSeleziona una voce: ")
                if scelta == '0':
                    return None
                    
                indice = int(scelta) - 1
                if 0 <= indice < len(self.voci_preimpostate):
                    return self.voci_preimpostate[indice]
                else:
                    print("Numero non valido.")
            except ValueError:
                print("Inserire un numero valido.")
                
    def inserisci_voci(self):
        """Permette l'inserimento delle voci"""
        print("\n=== Inserimento Voci ===")
        print("(Lascia vuota la descrizione per terminare)")
        
        while True:
            # Mostra voci già inserite
            if self.voci:
                print("\nVoci inserite:")
                for i, voce in enumerate(self.voci):
                    print(f"  {i+1}. {voce}")
                    
            # Chiede se usare voce preimpostata
            if self.voci_preimpostate:
                usa_preimpostata = input("\nUsare una voce preimpostata? (s/n): ").lower() == 's'
                if usa_preimpostata:
                    descrizione = self.seleziona_voce_preimpostata()
                    if descrizione is None:
                        descrizione = input("Descrizione: ")
                else:
                    descrizione = input("Descrizione: ")
            else:
                descrizione = input("\nDescrizione: ")
                
            if not descrizione:
                break
                
            importo = self._input_importo()
            if importo is None:
                continue
                
            self.voci.append(Voce(descrizione, importo))
            
            # Opzione per modificare/eliminare
            if self.voci:
                azione = input("\n[Enter] per continuare, [m] per modificare una voce, [e] per eliminare: ").lower()
                if azione == 'm':
                    self._modifica_voce()
                elif azione == 'e':
                    self._elimina_voce()
                    
    def _modifica_voce(self):
        """Modifica una voce esistente"""
        if not self.voci:
            return
            
        while True:
            try:
                num = input("Numero voce da modificare (0 per annullare): ")
                if num == '0':
                    return
                    
                indice = int(num) - 1
                if 0 <= indice < len(self.voci):
                    voce = self.voci[indice]
                    print(f"\nModifica: {voce}")
                    
                    nuova_desc = input(f"Nuova descrizione (invio per mantenere): ")
                    if nuova_desc:
                        voce.descrizione = nuova_desc
                        
                    nuovo_importo = self._input_importo("Nuovo importo (invio per mantenere): €")
                    if nuovo_importo is not None:
                        voce.importo = nuovo_importo
                        
                    print("Voce modificata!")
                    return
                else:
                    print("Numero non valido.")
            except ValueError:
                print("Inserire un numero valido.")
                
    def _elimina_voce(self):
        """Elimina una voce"""
        if not self.voci:
            return
            
        while True:
            try:
                num = input("Numero voce da eliminare (0 per annullare): ")
                if num == '0':
                    return
                    
                indice = int(num) - 1
                if 0 <= indice < len(self.voci):
                    voce_rimossa = self.voci.pop(indice)
                    print(f"Rimossa: {voce_rimossa}")
                    return
                else:
                    print("Numero non valido.")
            except ValueError:
                print("Inserire un numero valido.")
                
    def calcola_totale(self) -> Tuple[Decimal, List[Voce]]:
        """Calcola il totale e aggiunge eventuali voci extra"""
        voci_complete = self.voci.copy()
        totale = sum(v.importo for v in voci_complete)
        
        # Marca da bollo
        if totale > Decimal('77.47'):  # Soglia corretta per marca da bollo
            print(f"\nImporto totale €{totale:.2f} > €77.47")
            if input("Aggiungere marca da bollo €2.00? (s/n): ").lower() == 's':
                voci_complete.append(Voce("Marca da bollo su fattura elettronica", Decimal('2.00')))
                totale += Decimal('2.00')
                
        # Rivalsa previdenziale
        if input("\nApplicare rivalsa previdenziale 4%? (s/n): ").lower() == 's':
            importo_rivalsa = (totale * Decimal('0.04')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            voci_complete.append(Voce("Rivalsa previdenziale 4%", importo_rivalsa))
            totale += importo_rivalsa
            
        return totale, voci_complete
        
    def seleziona_conto(self) -> str:
        """Seleziona il conto bancario"""
        print("\nSeleziona conto di pagamento:")
        for num, conto in self.CONTI.items():
            print(f"{num}. {conto.split(' - ')[0]}")
            
        while True:
            try:
                scelta = int(input("Numero conto: "))
                if scelta in self.CONTI:
                    return self.CONTI[scelta]
                else:
                    print("Scelta non valida.")
            except ValueError:
                print("Inserire un numero valido.")
                
    def genera_output(self, cliente: Cliente, totale: Decimal, voci: List[Voce], 
                     conto: str, tipo_documento: str) -> str:
        """Genera il testo di output"""
        tipo = "AVVISO DI PARCELLA" if tipo_documento == 'a' else "FATTURA"
        data_oggi = datetime.now().strftime("%d/%m/%Y")
        
        output = f"# {tipo}\n\n"
        output += f"**Data:** {data_oggi}\n\n"
        output += f"## Cliente\n"
        output += f"**{cliente.nome}**\n"
        output += f"{cliente.indirizzo}\n"
        output += f"{cliente.cap} {cliente.citta} ({cliente.provincia})\n"
        output += f"P.IVA: {cliente.piva}\n"
        if cliente.cf:
            output += f"C.F.: {cliente.cf}\n"
        output += "\n"
        
        output += "## Dettaglio\n\n"
        output += "| Descrizione | Importo |\n"
        output += "|-------------|--------:|\n"
        
        for voce in voci:
            output += f"| {voce.descrizione} | €{voce.importo:.2f} |\n"
            
        output += f"| **TOTALE** | **€{totale:.2f}** |\n\n"
        
        output += f"## Modalità di pagamento\n"
        output += f"Bonifico bancario:\n"
        output += f"{conto}\n"
        
        return output
        
    def salva_output(self, output: str, cliente: Cliente, tipo_documento: str):
        """Salva o copia l'output"""
        print("\n" + "="*50)
        print(output)
        print("="*50)
        
        print("\nOpzioni:")
        print("1. Salva in file Markdown")
        print("2. Copia negli appunti")
        print("3. Entrambi")
        print("0. Nessuna azione")
        
        scelta = input("\nScelta: ")
        
        if scelta in ['1', '3']:
            # Genera nome file con data e cliente
            data_file = datetime.now().strftime("%Y%m%d")
            tipo = "avviso" if tipo_documento == 'a' else "fattura"
            nome_cliente = cliente.nome.replace(' ', '_').lower()
            filename = f"{tipo}_{nome_cliente}_{data_file}.md"
            
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(output)
                print(f"\nFile salvato: {filename}")
            except Exception as e:
                print(f"Errore nel salvataggio: {e}")
                
        if scelta in ['2', '3']:
            try:
                import pyperclip
                pyperclip.copy(output)
                print("\nCopiato negli appunti!")
            except ImportError:
                print("\nErrore: pyperclip non installato. Installa con: pip install pyperclip")
            except Exception as e:
                print(f"\nErrore nella copia: {e}")


def main():
    print("=== GESTIONE FATTURE E AVVISI ===\n")
    
    # Percorsi file
    file_clienti = "clienti.json"
    file_voci = "voci_preimpostate.txt"
    
    # Inizializza gestori
    gestore_clienti = GestoreClienti(file_clienti)
    gestore_fatture = GestoreFatture(file_voci)
    
    # Carica dati
    if not gestore_clienti.carica_clienti():
        return
        
    if not gestore_fatture.carica_voci_preimpostate():
        return
        
    # Tipo documento
    while True:
        tipo = input("Tipo documento - [a]vviso di parcella o [f]attura (q per uscire): ").lower()
        if tipo == 'q':
            print("Arrivederci!")
            return
        if tipo in ['a', 'f']:
            break
        print("Scelta non valida.")
        
    # Seleziona cliente
    cliente = gestore_clienti.seleziona_cliente()
    if not cliente:
        print("Operazione annullata.")
        return
        
    # Inserisci voci
    gestore_fatture.inserisci_voci()
    if not gestore_fatture.voci:
        print("Nessuna voce inserita. Operazione annullata.")
        return
        
    # Calcola totale
    totale, voci_complete = gestore_fatture.calcola_totale()
    
    # Seleziona conto
    conto = gestore_fatture.seleziona_conto()
    
    # Genera e salva output
    output = gestore_fatture.genera_output(cliente, totale, voci_complete, conto, tipo)
    gestore_fatture.salva_output(output, cliente, tipo)
    
    print("\nOperazione completata!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperazione interrotta dall'utente.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErrore imprevisto: {e}")
        sys.exit(1)