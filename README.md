# 🏋️ GymSheet — Schede di allenamento mobile-friendly

Converti qualsiasi scheda di allenamento in PDF in un'**app web** ottimizzata per smartphone, con salvataggio delle sessioni, storico e progressioni.

---

## 📱 Demo

Apri direttamente da GitHub Pages → [`scheda.html`](./scheda.html)

---

## 🗂️ File del progetto

| File | Descrizione |
|---|---|
| [`converter.html`](./converter.html) | Converti un PDF in un'app HTML — tutto nel browser |
| [`editor_scheda.html`](./editor_scheda.html) | Editor guidato per creare la scheda senza PDF |
| [`istruzioni_template.html`](./istruzioni_template.html) | Guida per gli istruttori + scarica il template |
| [`template_scheda.csv`](./template_scheda.csv) | Template CSV da compilare in Excel / Google Sheets |
| [`genera_scheda.py`](./genera_scheda.py) | Convertitore da riga di comando (Python) |
| [`scheda.html`](./scheda.html) | Esempio di scheda generata (Artibani Francesco) |

---

## 🚀 Come si usa

### Opzione 1 — Editor guidato (consigliato)
1. Apri **`editor_scheda.html`** nel browser
2. Aggiungi sezioni ed esercizi compilando i campi
3. Clicca **"Genera HTML"** → scarica l'app per il tuo cliente

### Opzione 2 — Converti un PDF
1. Prepara il PDF seguendo il formato descritto in [`istruzioni_template.html`](./istruzioni_template.html)
2. Apri **`converter.html`** nel browser
3. Trascina il PDF nella pagina → viene generato e scaricato l'HTML

### Opzione 3 — Python CLI
```bash
pip install pdfplumber
python3 genera_scheda.py scheda.pdf output.html
```

---

## 📋 Formato del PDF supportato

Il PDF deve contenere una tabella con queste colonne:

| Esercizio | Prog A | Prog B | Prog C | Link |
|---|---|---|---|---|
| Squat | 4x8 70% R90" | 3x10 65% | 5x5 75% | https://... |

- Le **intestazioni di sezione** sono righe con solo il nome nella colonna Esercizio (es. `PARTE INFERIORE`)
- I parametri sono **flessibili**: l'ordine non è fisso, molti formati sono accettati

### Formati parametri accettati

**Serie × Ripetizioni** — il numero più piccolo viene sempre identificato come le serie:
```
3x10 · 4 serie x 8 · 10x3 · 3 set x 12 · 10 rip x 3 serie · AMRAP 10min · EMOM 12
```

**Recupero:**
```
90s · 1min · 2' · 1'30" · R45sec · 2 minuti
```

**Carico:**
```
70% · 20 kg · 45 lbs · RPE 8 · RIR 2 · BW · peso corporeo
```

---

## 📲 Funzionalità dell'app generata

- **Tabs A / B / C** — programmi settimanali con navigazione rapida
- **Badge colorati** — serie, recupero e carico evidenziati visivamente
- **▶ YouTube** — apre il video dimostrativo direttamente dall'esercizio
- **📝 Note** — annotazioni per ogni esercizio, salvate nel browser
- **💾 Salva allenamento** — registra ogni sessione con data e programma
- **📊 Storico** — visualizza le sessioni passate e la progressione dei carichi
- Funziona **offline** dopo il primo caricamento

---

## 🛠️ Requisiti tecnici

- Nessun server necessario — tutto gira nel browser
- Il convertitore usa [PDF.js](https://mozilla.github.io/pdf.js/) via CDN
- Python 3 + `pdfplumber` solo per il CLI
- I dati vengono salvati nel `localStorage` del browser

---

## 📄 Licenza

MIT — libero uso, modifica e distribuzione.
