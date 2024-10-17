import random
import time
import cProfile
import pstats
import logging
import sys
from py3dbp.main import Packer, Bin, Item, Painter, set_external_logger  # Importa dal modulo esterno


def setup_logger(name, level=logging.DEBUG):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logger = setup_logger(__name__)

logger.info('Logger configurato correttamente nel modulo principale.')

# Passa il logger al modulo esterno
set_external_logger(logger)

#start = time.time()

# Crea un'istanza del profiler
#profiler = cProfile.Profile()
# Abilita il profiler, esegui la funzione, e disabilita il profiler
#profiler.enable()


tipi_bancale = {
    "Heavy": {
        "Quarter Pallet": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 100, "Peso massimo": 300, "Priority_pallet_choice": 2, "Color": "red"},
        "Half Pallet": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 150, "Peso massimo": 600, "Priority_pallet_choice": 5, "Color": "orange"},
        "Full Pallet": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 240, "Peso massimo": 1200, "Priority_pallet_choice": 7, "Color": "yellow"},
    },
    "Light": {
        "Light Pallet": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 240, "Peso massimo": 750, "Priority_pallet_choice": 6, "Color": "green"},
        "Extra Light Pallet": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 150, "Peso massimo": 450, "Priority_pallet_choice": 3, "Color": "olive"},
        "Ultra Light Pallet": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 240, "Peso massimo": 350, "Priority_pallet_choice": 4, "Color": "blue"},
        "Mini Quarter": {"Lunghezza massima": 120, "Larghezza massima": 100, "Altezza massima": 60, "Peso massimo": 150, "Priority_pallet_choice": 1, "Color": "pink"},
    },
    "Fuori Misura": {
        "Custom Pallet": {"Lunghezza massima": 1300, "Larghezza massima": 240, "Altezza massima": 240, "Peso massimo": 22000, "Priority_pallet_choice": 8, "Color": "brown"},
    }
}

pallets_dimensions = {
    "EUR": {"Lunghezza": 120, "Larghezza": 80, "Altezza": 15, "Peso": 25},
    "ISO": {"Lunghezza": 120, "Larghezza": 100, "Altezza": 15, "Peso": 28},
    "120x120": {"Lunghezza": 120, "Larghezza": 120, "Altezza": 15, "Peso": 30},
}

tutti_sottotipi_bancale = []
for tipo, sottotipo in tipi_bancale.items():
    for sottotipo, dimensioni in sottotipo.items():
        tutti_sottotipi_bancale.append((tipo, sottotipo, dimensioni))

sorted_all_types = sorted(tutti_sottotipi_bancale, key=lambda x: x[2]["Priority_pallet_choice"], reverse=True)

altezza_minima_possibile_pallet = sorted(pallets_dimensions.values(), key=lambda x: x["Altezza"])[0]["Altezza"]
#print(altezza_minima_possibile_pallet)
peso_minimo_possibile_pallet = sorted(pallets_dimensions.values(), key=lambda x: x["Peso"])[0]["Peso"]
#print(peso_minimo_possibile_pallet)

class Pallet:
    def __init__(self, tipo):
        self.tipo = tipo
        self.lunghezza = pallets_dimensions[tipo]["Lunghezza"]
        self.larghezza = pallets_dimensions[tipo]["Larghezza"]
        self.altezza = pallets_dimensions[tipo]["Altezza"]
        self.peso = pallets_dimensions[tipo]["Peso"]


class Collo:
    def __init__(self, lunghezza=120, larghezza=80, altezza=240, peso=1200, pallet=None, nome="ERRORE: Senza nome"):
        self.pallet = pallet
        #print(altezza, {self.pallet.altezza if self.pallet is not None else 0})
        self.altezza = altezza - (self.pallet.altezza if self.pallet is not None else 0)
        self.peso = peso - (self.pallet.peso if self.pallet is not None else 0)
        self.lunghezza, self.larghezza = max(lunghezza, larghezza), min(lunghezza, larghezza)
        self.volume = self.lunghezza * self.larghezza * self.altezza
        self.densità = self.peso / self.volume  # kg/cm^3
        self.nome = nome
        self.assegna_pallet_a_collo()


    def assegna_pallet_a_collo(self):
        if self.pallet is None:
            #print(f"Misure collo: Lunghezza={self.lunghezza}, Larghezza={self.larghezza}, Altezza={self.altezza}, Peso={self.peso}")
            # Riordina i pallet per larghezza in modo crescente
            pallets = sorted(pallets_dimensions, key=lambda x: pallets_dimensions[x]["Larghezza"], reverse=True)
            #print(pallets)
            pallets_classe = [Pallet(pallet) for pallet in pallets]

            # Trova il pallet con larghezza minima che sia sufficiente per il collo (partendo da quello più grande)
            for pallet in pallets_classe:
                if pallet.larghezza >= self.larghezza:
                    self.pallet = pallet

            # Se nessun pallet è sufficiente, assegna il pallet più grande
            if self.pallet is None:
                self.pallet = pallets_classe[-1]
            
            #print(f"Collo {self.nome} di larghezza {self.larghezza} assegnato a pallet {self.pallet.tipo}.")

            #print(F"Misure collo: Lunghezza={self.lunghezza}, Larghezza={self.larghezza}, Altezza={self.altezza}, Peso={self.peso}")
            #assicurati grandezze collo


class Bancale:
    def __init__(self, collo, baia=None, camion_assegnato=None, priorità=5, sovrapponibile=True, sovr_index=1):
        self.pallet = collo.pallet
        self.sovr_index = sovr_index
        self.sovrapponibile = sovrapponibile
        self.lunghezza = max(collo.lunghezza, self.pallet.lunghezza)
        self.larghezza = max(collo.larghezza, self.pallet.larghezza)
        self.altezza = collo.altezza + self.pallet.altezza
        self.peso = collo.peso + self.pallet.peso
        self.volume = self.lunghezza * self.larghezza * self.altezza
        self.densità = self.peso / self.volume # kg/cm^3
        self.nome = collo.nome
        self.position = None  # Aggiunta per tracciare la posizione del bancale nel camion
        self.sottotipo = None
        self.forma = "cube"
        self.priorità = priorità
        self.colore = None
        self.camion_assegnato = camion_assegnato
        self.baia = baia
        self.capacità_di_carico = self.sovrapponibilità_dinamica() # Call the method to calculate the dynamic load bearing capacity
        self.assegna_sottotipo_bancale_a_bancale()  # Call the method to assign the bancale type
        self.versione_Item = Item(partno=self.nome, name=self.sottotipo, typeof=self.forma, WHD=(self.larghezza, self.lunghezza, self.altezza), weight=self.peso, level=self.priorità, loadbear=self.capacità_di_carico, updown=False, color=self.colore, assigned_bin=(self.camion_assegnato.versione_bin if self.camion_assegnato is not None else None))

    def aggiorna_versione_Item(self):
        self.versione_Item = Item(partno=self.nome, name=self.sottotipo, typeof=self.forma, WHD=(self.larghezza, self.lunghezza, self.altezza), weight=self.peso, level=self.priorità, loadbear=self.capacità_di_carico, updown=False, color=self.colore, assigned_bin=(self.camion_assegnato.versione_bin if self.camion_assegnato is not None else None))

    def sovrapponibilità_dinamica(self):
        if self.sovrapponibile:
            # Calcola la capacità di carico basata sul peso e sull'indice di svrapponibilità
            return self.peso * self.sovr_index
        else:
            return 0

    def assegna_sottotipo_bancale_a_bancale(self):
        if self.larghezza > self.lunghezza:
            self.lunghezza, self.larghezza = self.larghezza, self.lunghezza
            print(f"Bancale {self.nome} con larghezza maggiore della lunghezza. Scambio delle due dimensioni.")

        sorted_all_types_copy = sorted_all_types[:]
        for tipo, sottotipo, dimensioni in sorted_all_types_copy:
            #print(f"Verifica tipo: {tipo}, nome: {nome}")
            #print(f"Dimensioni bancale: Lunghezza={self.lunghezza}, Larghezza={self.larghezza}, Altezza={self.altezza}, Peso={self.peso}")
            #print(f"Limiti: Lunghezza massima={dimensioni['Lunghezza massima']}, Larghezza massima={dimensioni['Larghezza massima']}, Altezza massima={dimensioni['Altezza massima']}, Peso massimo={dimensioni['Peso massimo']}")
            if (
                self.lunghezza <= dimensioni["Lunghezza massima"]
                and self.larghezza <= dimensioni["Larghezza massima"]
                and self.altezza <= dimensioni["Altezza massima"]
                and self.peso <= dimensioni["Peso massimo"]
            ):
                self.sottotipo = sottotipo  # Assign the bancale type to the attribute
                self.colore = dimensioni["Color"]  # Assign the color to the attribute
                #print(f"Tipo assegnato: {tipo}, Colore assegnato: {self.colore}")
                self.aggiorna_versione_Item()
        #print("Nessun tipo compatibile trovato")
        #self.aggiorna_versione_Item()
        #print(f"Bancale {self.nome} assegnato come {self.sottotipo}")
        #print(f"Dimensioni bancale: Lunghezza={self.lunghezza}, Larghezza={self.larghezza}, Altezza={self.altezza}, Peso={self.peso}")

class CamionCentinato:
    def __init__(self, lunghezza=1300, larghezza=240, altezza=240, peso_massimo=24000, targa="AA000AA", metodo_carico="Laterale", bancali_preesistenti_movimentabili=True, baia=None):
        self.lunghezza = lunghezza  # in cm
        self.larghezza = larghezza  # in cm
        self.altezza = altezza  # in cm
        self.peso_massimo = peso_massimo  # in kg
        self.bancali_caricati = []
        self.volume = self.lunghezza * self.larghezza * self.altezza
        self.peso_corrente = 0
        self.volume_corrente = 0
        self.targa = targa
        self.metodo_carico = metodo_carico
        self.baia = baia
        self.bancali_preesistenti = []
        self.bancali_preesistenti_movimentabili = bancali_preesistenti_movimentabili
        self.versione_bin = Bin(partno=self.targa, WHD=((self.larghezza, self.lunghezza, self.altezza)), max_weight=self.peso_massimo, corner=0, put_type=0)
        self.baia.packer.addBin(self.versione_bin)


    def considera_bancali_preesistenti(self, bancali_iniziali):

        # Aggiungi i nuovi bancali al packer
        # Aggiungi i bancali già caricati nel camion al packer
        # Di default i bancali non hanno posizione, a meno che non gli sia già stata data
        # Che sia già vuoto o no, non c'è differenza a meno che non vogliamo impostare i bancali preesistenti come fissi
        #print(f"**Bancali preesistenti per camion {self.targa}:**")
        for bancale in self.bancali_preesistenti:
            #print(bancale.nome)
            bancale.priorità = 1
            #position=bancale.position POSIZIONE NON MODIFICABILE ANCORA DA IMPLEMENTARE
            
            while not self.verifica_compatibilità_con_vettura(bancale):
                print(f"ERRORE: Il bancale preesistente {bancale.nome} non è compatibile con la vettura {self.targa} su cui è caricato.")
                print(f"Le dimensioni del bancale sono: Lunghezza={bancale.lunghezza}, Larghezza={bancale.larghezza}, Altezza={bancale.altezza}, Peso={bancale.peso}, Pallet={bancale.pallet.tipo}.")
                print(f"Le dimensioni della vettura sono: Lunghezza={self.lunghezza}, Larghezza={self.larghezza}, Altezza={self.altezza}, Peso={self.peso_massimo}.")
                print(f"Reinserire le dimensioni del bancale {bancale.nome}.")
                lunghezza_bancale = int(chiedi_valore("Lunghezza (se vuoto 120): ", 120, lambda x: x.isdigit()))
                larghezza_bancale = int(chiedi_valore("Larghezza (se vuoto 80): ", 80, lambda x: x.isdigit()))
                altezza_bancale = int(chiedi_valore("Altezza (se vuoto 240): ", 240, lambda x: x.isdigit()))
                peso_bancale = int(chiedi_valore("Peso (se vuoto 1200): ", 1200, lambda x: x.isdigit()))
                tipo_pallet = chiedi_valore("Tipo pallet (EUR/ISO/120x120) (se vuoto automatico): ", None, lambda x: x in ["EUR", "ISO", "120x120", ""])
                pallet_compreso = chiedi_valore("Pallet compreso nelle misure? (si/no) (se vuoto si): ", "si", lambda x: x.lower() in ["si", "no", ""]).lower()
                for collo in colli:
                    if collo.nome == bancale.nome:
                        collo.lunghezza = lunghezza_bancale
                        collo.larghezza = larghezza_bancale
                        collo.pallet = tipo_pallet
                        collo.altezza = altezza_bancale - ((collo.pallet.altezza if collo.pallet is not None else altezza_minima_possibile_pallet) if pallet_compreso == "si" else 0)
                        collo.peso = peso_bancale - ((collo.pallet.peso if collo.pallet is not None else peso_minimo_possibile_pallet) if pallet_compreso == "si" else 0)
                        collo.volume = collo.lunghezza * collo.larghezza * collo.altezza
                        collo.densità = collo.peso / collo.volume  # kg/cm^3
                        collo.assegna_pallet_a_collo()
                        bancale.pallet = collo.pallet
                        bancale.lunghezza = max(collo.lunghezza, collo.pallet.lunghezza)
                        bancale.larghezza = max(collo.larghezza, collo.pallet.larghezza)
                        bancale.altezza = collo.altezza + bancale.pallet.altezza
                        bancale.peso = collo.peso + bancale.pallet.peso
                        bancale.volume = bancale.lunghezza * bancale.larghezza * bancale.altezza
                        bancale.densità = bancale.peso / bancale.volume # kg/cm^3
                        bancale.capacità_di_carico = bancale.sovrapponibilità_dinamica()

            bancale.assegna_sottotipo_bancale_a_bancale()
            
            # Tentativo di caricamento del bancale
            if bancale not in self.bancali_caricati:
                if bancale.versione_Item not in self.baia.packer.items:
                    self.baia.packer.addItem(bancale.versione_Item)
                    print(f"Bancale {bancale.nome} preesistente aggiunto al packer della baia {bancale.camion_assegnato.baia.numero}. Confermato")
                    bancali_iniziali.remove(bancale)
                else:
                    print(f"ERRORE: Il bancale {bancale.nome} è già presente sia nel camion {self.targa} che nel packer di baia {self.baia.numero}.")
            else:
                print(f"ERRORE: Il bancale {bancale.nome} è già presente tra i caricati del camion {self.targa}.")
        #print("****bancali preesistenti finiti****")
    

    def verifica_compatibilità_con_vettura(self, bancale):
        if bancale.lunghezza <= self.lunghezza and \
           bancale.larghezza <= self.larghezza and \
           bancale.altezza <= self.altezza and \
           bancale.peso <= self.peso_massimo:
            return True
        else:
            #print(f"Concern: Il bancale {bancale.nome} non può essere caricato sul camion {self.targa}.")
            return False
        
class Baia:
    def __init__(self, numero, lunghezza, larghezza, altezza):
        self.numero = numero
        self.lunghezza = lunghezza
        self.larghezza = larghezza
        self.altezza = altezza
        self.bancali_in_baia = []
        self.volume = self.lunghezza * self.larghezza * self.altezza
        self.volume_corrente = sum([b.volume for b in self.bancali_in_baia])
        self.packer = Packer(self.numero)

    def aggiungi_bancale_in_baia(self, bancale_da_aggiungere_in_baia, bancali_iniziali):
        if self.verifica_compatibilità_con_baia(bancale_da_aggiungere_in_baia):
            if bancale_da_aggiungere_in_baia not in self.bancali_in_baia:
                self.bancali_in_baia.append(bancale_da_aggiungere_in_baia)
                bancali_iniziali.remove(bancale_da_aggiungere_in_baia)
            else:
                print(f"ERRORE: Il bancale {bancale_da_aggiungere_in_baia.nome} è già presente nella baia {self.numero}.")
                #bancali_iniziali.remove(b for b in bancali_iniziali if b.nome == bancale_da_aggiungere_in_baia.nome) #DA CORREGGERE
                #bancali_iniziali[:] = [bancale for bancale in bancali_iniziali if bancale.nome != bancale_da_aggiungere_in_baia.nome]
        else:
            print(f"Il bancale {bancale_da_aggiungere_in_baia.nome} non può essere caricato nella baia {self.numero}. Bancale scartato. Lunghezza {bancale.lunghezza} invece di {self.lunghezza}, larghezza {bancale.larghezza} invece di {self.larghezza}, altezza {bancale.altezza} invece di {self.altezza}")
            bancale.baia = None

    def verifica_compatibilità_con_baia(self, bancale):
        if bancale.lunghezza <= self.lunghezza and \
           bancale.larghezza <= self.larghezza and \
           bancale.altezza <= self.altezza:
            return True
        else:
            print(f"ERRORE: Il bancale {bancale.nome} non può essere caricato nella baia {self.numero}.")
            return False
        
    def carica_sui_camions(self, bancali_iniziali, camions_di_questa_baia, parametro_stabilità=0.9):

        # Aggiungi i nuovi bancali al packer di baia
        # Che sia già vuoto o no, non c'è differenza a meno che non vogliamo impostare i bancali preesistenti come fissi
        # Aggiungi i bancali già caricati nel camion al packer
        # Di default i bancali non hanno posizione, a meno che non gli sia già stata data
        #print(f"**Bancali preesistenti per camion {camion.targa}:**")
        #print(f"**{[b.nome for b in camion.bancali_preesistenti]}**")
        #for bancale in camion.bancali_preesistenti:
        #    print(f"Bancale {bancale.nome} assegnato a {bancale.camion_assegnato.targa}.") #DEBUG
        #print("ciao")

        for camion in camions_di_questa_baia:
            camion.considera_bancali_preesistenti(bancali_iniziali)
            print(f"Camion {camion.targa} con {len(camion.bancali_preesistenti)} bancali preesistenti + {len(camion.bancali_caricati)} già caricati.")
            for bancale in self.bancali_in_baia:
                #print(f"Bancale {bancale.nome} in baia {self.numero}.")
                # Tentativo di caricamento del bancale
                if camion.verifica_compatibilità_con_vettura(bancale):
                    if bancale.nome not in [item.partno for item in self.packer.items]: 
                        self.packer.addItem(bancale.versione_Item)
                        #print(f"Bancale {bancale.nome} aggiunto al packer della baia {self.numero}.")
                    #else:
                        #print(f"ERRORE: Il bancale {bancale.nome} è già presente nel packer di baia {self.numero}.")
                else:
                    print(f"Bancale {bancale.nome} non compatibile con vettura {camion.targa} quindi lasciato in baia")   
                    
        print(f"Lista item del packer di baia {self.numero} prima di paccare:")
        for item in self.packer.items:
            print(f"Item {item.partno} aggiunto a packer di baia {self.numero}")


        #print(f"Tutti bancali paked in baia {self.numero} prima del packing: {[item.partno for item in self.packer.items]}")

        # sembra che al momento del packing ci siano solo i bancali precaricati e non quelli in baia nella lista degli items di quella baia
        # Esegui il packing solo per i bancali senza posizione assegnata ANCORA DA IMPLEMENTARE
        self.packer.pack(
            bigger_first=True,                 # bigger item first.
            fix_point=True,                    # fix item floating problem.
            #binding=None,                      # make a set of items.
            distribute_items=True,             # If multiple bin, to distribute or not.
            check_stable=True,                 # check stability on item.
            support_surface_ratio=parametro_stabilità,        # set support surface ratio.
            number_of_decimals=0
        )

        # put order
        #self.packer.putOrder()

        # Segna bancale sul camion
        for camion in camions_di_questa_baia:
            for bin in self.packer.bins:
                if bin.partno == camion.targa:
                    lista = (self.bancali_in_baia + camion.bancali_preesistenti)[:]
                    for bancale in lista:
                        for item in bin.items:
                            if item.partno == bancale.nome:
                                bancale.position = item.position # Aggiorna la posizione del bancale
                                bancale.camion_assegnato = camion # Aggiorna il camion assegnato al bancale
                                camion.bancali_caricati.append(bancale) # Aggiungi il bancale alla lista dei bancali caricati sul camion
                                #print(f"Bancale {bancale.nome} caricato nel camion {camion.targa} con posizione x: {bancale.position[0]}, y: {bancale.position[1]}, z: {bancale.position[2]}")
                                bancale.baia = None # Rimuovi la baia dal bancale
                                camion.peso_corrente += item.weight # Aggiorna il peso corrente del camion
                                camion.volume_corrente += item.getVolume()  # Aggiorna il volume corrente del camion
                                #bancali_iniziali.remove(bancale) # rimuovi bancale da bancali bancali_iniziali (se è in questa lista) perchè piazzato su un camion
                                #bancali_iniziali[:] = [b for b in bancali_iniziali if b.nome != bancale.nome]
                                if bancale in self.bancali_in_baia:
                                    self.bancali_in_baia.remove(bancale) # Rimuovi il bancale dalla baia (se era in questa lista)
                                if bancale in camion.bancali_preesistenti:
                                    camion.bancali_preesistenti.remove(bancale)


def distribuisci_bancali_a_baie(bancali_da_distribuire_a_baie):
    #for bancale in bancali_da_distribuire_a_baie:
    #            print(f"Bancale {bancale.nome} assegnato a baia {bancale.baia.numero if bancale.baia is not None else 'NESSUNA'} all'inizio (in bancali_da_distribuire_a_baie).")
    bancali_da_distribuire_a_baie_copy = bancali_da_distribuire_a_baie[:]
    for bancale in bancali_da_distribuire_a_baie_copy:
        #print(f"Bancale {bancale.nome} assegnato a baia {bancale.baia.numero if bancale.baia is not None else 'NESSUNA'} durante il ciclo di assegnamento.")
        if bancale.baia:
            #print(f"Baia {bancale.baia.numero} bancali: {[bancale.nome for bancale in bancale.baia.bancali_in_baia]}")
            #print(f"Aggiungo il bancale {bancale.nome} alla baia {bancale.baia.numero}.")
            bancale.baia.aggiungi_bancale_in_baia(bancale, bancali_da_distribuire_a_baie)
            #print(f"Bancale {bancale.nome} assegnato alla baia {bancale.baia.numero} durante distribuzione.")
            #print(f"Rimanenti in bancali iniziali: {[b.nome for b in bancali_da_distribuire_a_baie]}")
            if bancale.camion_assegnato is not None and not bancale.camion_assegnato.versione_bin.items:
                bancale.priorità = 2
                # se ha una baia assegnata ed anche un camion assegnato, il camion se lo caricherà durante il packing
        else:
            #print(f"Baia del bancale vuota e ={bancale.baia}")
            if bancale.camion_assegnato is None:
                print(f"Concern: Il bancale {bancale.nome} non è assegnato a nessun camion e a nessuna baia.")
            #else:
                #bancale.camion_assegnato.bancali_preesistenti.append(bancale) viene già fatto inizialmente
    
def chiedi_valore(messaggio, valore_default, validazione):
    while True:
        valore_input = input(messaggio)
        if valore_input == "":
            return valore_default
        if validazione(valore_input):
            return valore_input
        else:
            print("Valore non valido. Per favore, riprova.")


# Inizializza le baie
baie = []
num_baie = 2 # random.randint(2, 3)
for i in range(num_baie):
    baia = Baia(numero=i, lunghezza=1300, larghezza=240, altezza=480)
    baie.append(baia)

# Inizializza i camion
camions = []
num_camions = random.randint(7, 8)
for _ in range(num_camions):
    class_camion = CamionCentinato(targa=f"AA{_}", baia=random.choice(baie))
    camions.append(class_camion)

# Creazione dei colli
colli = []
for _ in range(50):
    lunghezza = random.randint(20, 150)
    larghezza = random.randint(20, 150)
    altezza = random.randint(30, 245)
    volume = lunghezza * larghezza * altezza
    peso = int(volume * random.uniform(0.0001, 0.0005))
    pallet = Pallet(random.choice(["EUR", "ISO", "120x120"]))
    nome = f"{_}"
    collo = Collo(lunghezza=lunghezza, 
                   larghezza= larghezza, 
                     altezza=altezza, 
                       peso=peso,  
                        pallet=pallet, 
                        nome=nome)
    colli.append(collo)

# Trasforma i colli in bancali
bancali_iniziali_v1 = []
for collo in colli:
    baia = random.choice(baie)
    #sovrapponibile = random.choice([True, False])
    priorità = random.randint(3, 5)
    bancale = Bancale(collo=collo, baia=baia, priorità=priorità) # sovrapponibile=sovrapponibile
    sovr_index = random.random()   # random tra zero e 1
    if bancale.sottotipo is not None:  # Check if a valid type was assigned
        bancali_iniziali_v1.append(bancale)
    else:
        bancali_iniziali_v1.append(bancale) # prova ma da rimuovere dopo
        #print(f"Bancale scartato (teoricamente, non ora in prova): Bancale {bancale.nome} con Lunghezza={bancale.lunghezza}, Larghezza={bancale.larghezza}, Altezza={bancale.altezza}, Peso={bancale.peso} non può essere assegnato a nessun camion.")

# Assegna alcuni dei bancali appena creati a qualche camion come se li avesse già caricati sopra
for camion in camions:
    i += 3
    for bancale in bancali_iniziali_v1[i-4:i-1]:
        bancale.camion_assegnato = camion
        bancale.baia = None
        camion.bancali_preesistenti.append(bancale)
        #bancale.position = (0, 0, 0)
        #print(f"Bancale {bancale.nome} assegnato al camion {camion.targa}.")

    #print(f"Camion {camion.targa} con {len(camion.bancali_preesistenti)} bancali preesistenti.")
    #for bancale in camion.bancali_preesistenti:
    #    print(f"Bancale {bancale.nome} assegnato a {bancale.camion_assegnato.targa}.")

#for baia in baie:
#    print(f"Baia {baia.numero} bancali: {[bancale.nome for bancale in bancali_iniziali if bancale.baia == baia]}")

# Distribuzione dei bancali nelle baie
distribuisci_bancali_a_baie(bancali_da_distribuire_a_baie = bancali_iniziali_v1)

#for baia in baie:
#    print(f"Baia {baia.numero} bancali: {[bancale.nome for bancale in baia.bancali_in_baia]}")

#for bancale in bancali_iniziali:
    #print(f"Bancale {bancale.nome} assegnato a {bancale.camion_assegnato}.")

for camion in camions:
    print(f"Camion {camion.targa} con {len(camion.bancali_preesistenti)} bancali preesistenti.")
    for bancale in camion.bancali_preesistenti:
        print(f"Bancale {bancale.nome} assegnato a {bancale.camion_assegnato.targa} ovvero {camion.targa}.")

parametro_stabilità = 0.9


for baia in baie:
    camions_di_questa_baia = [camion for camion in camions if camion.baia == baia]
    print(f"Camion per baia {baia.numero}: {[camion.targa for camion in camions_di_questa_baia]}")
    # Caricamento dei colli sui camion
    baia.carica_sui_camions(bancali_iniziali = bancali_iniziali_v1, camions_di_questa_baia = camions_di_questa_baia, parametro_stabilità = parametro_stabilità)

    # Stampa dei bancali caricati
    print(f"**Bancali caricati da baia {baia.numero}**")
    for camion in camions_di_questa_baia:
        print(f"- Sul camion {camion.targa}:")
        for camion_bin in baia.packer.bins:
            if camion_bin.partno == camion.targa:
                #print(camion.bancali_caricati)
                for bancale in camion.bancali_caricati:
                    print(f"Bancale {bancale.nome} caricato nel camion {camion.targa} con posizione x: {bancale.position[0]}, y: {bancale.position[1]}, z: {bancale.position[2]}")
            #else:
                #print(f"ERRORE: Il camion {camion.targa} non è presente tra i bin di baia {baia.numero} (non matchano il camion.targa e baia.packer.bins.partno).")
                #print(camion_bin.partno)
                #print(camion.targa)
    print("Rimasti in baia:")
    for bancale in baia.bancali_in_baia:
        i=0
        for camion in camions_di_questa_baia:
            i+=1
            if camion.verifica_compatibilità_con_vettura(bancale):
                print(f"Bancale {bancale.nome} rimasto in baia perchè camion pieni. Misure accettabili")
                break
            if i==len(camions_di_questa_baia):
                print(f"Bancale {bancale.nome} rimasto in baia ma NON TRASPORTABILE. Misure: Lunghezza {bancale.lunghezza}, Larghezza {bancale.larghezza}, Altezza {bancale.altezza}")

    for bancale in bancali_iniziali_v1:
        if bancale.baia == baia:
            i=0
            for camion in camions_di_questa_baia:
                i+=1
                if camion.verifica_compatibilità_con_vettura(bancale):
                    print(f"ERRORE: Bancale {bancale.nome} assegnato a questa baia ({bancale.baia.numero}) ma mai entrato in baia. Misure trasportabili da almeno un camion")
                    break
                if i==len(camions_di_questa_baia):
                    print(f"Bancale {bancale.nome} assegnato a questa baia ({bancale.baia.numero}) ma mai entrato in baia. NON TRASPORTABILE. Misure: Lunghezza {bancale.lunghezza}, Larghezza {bancale.larghezza}, Altezza {bancale.altezza}")

    # put order
    # camion.packer.putOrder()

    # Stampa dei bancali caricati sul camion
    print("***************************************************")
    for camion in baia.packer.bins:
        print("**", camion.string(), "**")
        print("***************************************************")
        print("FITTED ITEMS:")
        print("***************************************************")
        volume = camion.width * camion.height * camion.depth
        volume_fitted_items = 0  # Total volume of fitted items
        for item in camion.items:
            """
            print("bancale numero : ", item.partno)
            print("tipo : ", item.name)
            print("colore : ", item.color)
            print("Posizione - ", end=" ")
            print("x : ", item.position[0], end=" ")
            print("      y : ", item.position[1], end=" ")
            print("      z : ", item.position[2])
            print("rotation type : ", item.rotation_type)
            print("Larg*Lung*Alt : ", str(item.width) + ' * ' + str(item.height) + ' * ' + str(item.depth))
            print("volume : ", int(item.width) * int(item.height) * int(item.depth))
            print("peso : ", int(item.weight))
            print("***************************************************")
            """
            volume_fitted_items += int(item.width) * int(item.height) * int(item.depth)

        print('space utilization : {}%'.format(round(volume_fitted_items / int(volume) * 100, 2)))
        print('residual volume : ', int(volume) - volume_fitted_items)
        print("gravity distribution : ", camion.gravity)
        print("***************************************************")

        #print(camion.items)
        # draw results
        painter = Painter(camion)
        fig = painter.plotBoxAndItems(
            title=camion.partno,
            alpha=0.6,   # Trasparenza
            write_num=True,
            fontsize=10,
            alpha_proportional=True,
            top_face_alpha_color=True
        )

    print("***************************************************")
    print(f"UNFITTED ITEMS (con misure accettabili) in baia {baia.numero}:")
    unfitted_names = ''
    volume_unfitted_items = 0  # Total volume of unfitted items
    for item in baia.packer.unfit_items:
        print("***************************************************")
        print("bancale numero : ", item.partno)
        print('tipo : ', item.name)
        print("colore : ", item.color)
        print("Larg*Lung*Alt : ", str(item.width) + ' * ' + str(item.height) + ' * ' + str(item.depth))
        print("volume : ", int(item.width) * int(item.height) * int(item.depth))
        print("peso : ", int(item.weight))
        volume_unfitted_items += int(item.width) * int(item.height) * int(item.depth)
        unfitted_names += '{},'.format(item.partno)
        print("***************************************************")
    print("***************************************************")
    #print(f'BANCALI con misure accettabili NON CARICATI in BAIA {baia.numero}: ', unfitted_names)
    print(f'VOLUME BANCALI con misure accettabili NON CARICATI in BAIA {baia.numero}: ', volume_unfitted_items)

#fig.show()

#profiler.disable()

# Stampa il report delle statistiche
#stats = pstats.Stats(profiler)
#stats.sort_stats('cumulative').print_stats(10)
#profiler.dump_stats('profilazione.prof')
#stop = time.time()
#print('used time : ', stop - start)
#logger.info('used time : %s', stop - start)

"""
for baia in baie:
    for camion in baia.packer.bins:
        print(f"Camion {camion.partno} con {len(camion.items)} bancali caricati.")
        print(f"Volume totale: {camion.getVolume()}")
        print(f"Peso totale: {camion.getTotalWeight()}")
        print(f"Dimensioni: Larghezza={camion.width}, Lung={camion.height}, Alt={camion.depth}")
        print(f"Gravità: {camion.gravity}")
        print(f"max_weight: {camion.max_weight}")
        print(f"corner: {camion.corner}")
        print(f"put_type: {camion.put_type}")
        print(f"fit_items: {camion.fit_items}")
        print(f"unfit_items: {camion.unfitted_items}")
        print(f"number_of_decimals: {camion.number_of_decimals}")
        print(f"fix_point: {camion.fix_point}")
        print(f"check_stable: {camion.check_stable}")
        print(f"support_surface_ratio: {camion.support_surface_ratio}")

        for item in camion.items:
            print(f"partno: {item.partno}")
            print(f"name: {item.name}")
            print(f"typeof: {item.typeof}")
            print(f"larghezza: {item.width}")
            print(f"lunghezza: {item.height}")
            print(f"altezza: {item.depth}")
            print(f"weight: {item.weight}")
            print(f"level: {item.level}")
            print(f"loadbear: {item.loadbear}")
            print(f"updown: {item.updown}")
            print(f"color: {item.color}")
            print(f"rotation_type: {item.rotation_type}")
            print(f"position: {item.position}")
            print(f"number_of_decimals: {item.number_of_decimals}")
            print(f"assigned_bin: {item.assigned_bin}")
            print(f"volume: {item.getVolume()}")
            print(f"max_area: {item.getMaxArea()}")
            print(f"dimension: {item.getDimension()}")
"""


"""
# Funzione obiettivo minimizzazione costo trazione
def calcolo_costo_trazione(collo):
    portata_massima_centinato = 25000  # Define the value of portata_massima_centinato
    indice_consumo_carburante = 1 + (max(0, portata_massima_centinato - 20000) / 500) * 0.005
    indice_difficolta_movimentazione = 1.1 if portata_massima_centinato > 10000 else 1  # Semplice esempio
    tassabile = (bancale(collo) * coefficiente_volume) + (portata_massima_centinato * coefficiente_peso)
    costo_trazione = base_costo + (tassabile * indice_consumo_carburante * indice_difficolta_movimentazione)
    return costo_trazione

# Esempio di calcolo del costo di trazione
# costo = calcolo_costo_trazione(collo)
# print(f"Costo totale della trazione: {costo} euro")
"""

print("***************************************************")
print("***************************************************")
print("***************************************************")
print("***************************************************")
print("***************************************************")
print("***************************************************")
print("***************************************************")

# Creazione dei colli aggiuntivi per packing 2
colli_aggiuntivi = []
for _ in range(51, 60):
    lunghezza = random.randint(20, 150)
    larghezza = random.randint(20, 150)
    altezza = random.randint(30, 245)
    volume = lunghezza * larghezza * altezza
    peso = int(volume * random.uniform(0.0001, 0.0005))
    pallet = Pallet(random.choice(["EUR", "ISO", "120x120"]))
    nome = f"{_}"
    collo = Collo(lunghezza=lunghezza, 
                   larghezza= larghezza, 
                     altezza=altezza, 
                       peso=peso,  
                        pallet=pallet, 
                        nome=nome)
    colli_aggiuntivi.append(collo)
    print(f"Nome collo aggiuntivo appena creato: {collo.nome}")


# Trasforma i colli aggiuntivi in bancali aggiuntivi
bancali_iniziali_v2 = []
for collo in colli_aggiuntivi:
    priorità = random.randint(3, 5)
    bancale = Bancale(collo=collo, priorità=priorità, baia=camions[0].baia)
    sovr_index = random.random()   # random tra zero e 1
    bancali_iniziali_v2.append(bancale)

# Assegna i bancali appena creati al camion 0
for bancale in bancali_iniziali_v2:
    bancale.camion_assegnato = camions[0]

distribuisci_bancali_a_baie(bancali_da_distribuire_a_baie=bancali_iniziali_v2)
camions_di_questa_baia_v2 = [camion for camion in camions if camion.baia == camions[0].baia]
camions[0].baia.carica_sui_camions(bancali_iniziali = bancali_iniziali_v2, camions_di_questa_baia = camions_di_questa_baia_v2, parametro_stabilità = parametro_stabilità)

# Stampa dei bancali caricati sul camion
print("***************************************************")
camion=camions[0].versione_bin
baia=camions[0].baia
print("**", camion.string(), "**")
print("***************************************************")
print("FITTED ITEMS:")
print("***************************************************")
volume = camion.width * camion.height * camion.depth
volume_fitted_items = 0  # Total volume of fitted items
for item in camion.items:
    """
    print("bancale numero : ", item.partno)
    print("tipo : ", item.name)
    print("colore : ", item.color)
    print("Posizione - ", end=" ")
    print("x : ", item.position[0], end=" ")
    print("      y : ", item.position[1], end=" ")
    print("      z : ", item.position[2])
    print("rotation type : ", item.rotation_type)
    print("Larg*Lung*Alt : ", str(item.width) + ' * ' + str(item.height) + ' * ' + str(item.depth))
    print("volume : ", int(item.width) * int(item.height) * int(item.depth))
    print("peso : ", int(item.weight))
    print("***************************************************")
    """
    volume_fitted_items += int(item.width) * int(item.height) * int(item.depth)

print('space utilization : {}%'.format(round(volume_fitted_items / int(volume) * 100, 2)))
print('residual volume : ', int(volume) - volume_fitted_items)
print("gravity distribution : ", camion.gravity)
print("***************************************************")

#print(camion.items)
# draw results
painter = Painter(camion)
fig = painter.plotBoxAndItems(
    title=camion.partno,
    alpha=0.6,   # Trasparenza
    write_num=True,
    fontsize=10,
    alpha_proportional=True,
    top_face_alpha_color=True
)

print("***************************************************")
print(f"UNFITTED ITEMS (con misure accettabili) in baia {baia.numero}:")
unfitted_names = ''
volume_unfitted_items = 0  # Total volume of unfitted items
for item in baia.packer.unfit_items:
    print("***************************************************")
    print("bancale numero : ", item.partno)
    print('tipo : ', item.name)
    print("colore : ", item.color)
    print("Larg*Lung*Alt : ", str(item.width) + ' * ' + str(item.height) + ' * ' + str(item.depth))
    print("volume : ", int(item.width) * int(item.height) * int(item.depth))
    print("peso : ", int(item.weight))
    volume_unfitted_items += int(item.width) * int(item.height) * int(item.depth)
    unfitted_names += '{},'.format(item.partno)
    print("***************************************************")
print("***************************************************")
#print(f'BANCALI con misure accettabili NON CARICATI in BAIA {baia.numero}: ', unfitted_names)
print(f'VOLUME BANCALI con misure accettabili NON CARICATI in BAIA {baia.numero}: ', volume_unfitted_items)
