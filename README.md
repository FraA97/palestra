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
| [`scheda.html`](./scheda.html) | Esempio di scheda generata (Mario Rossi) |

---

## 🚀 Come si usa

### Opzione 1 — Editor guidato (consigliato)
1. Apri **`editor_scheda.html`** nel browser
2. Aggiungi sezioni ed esercizi compilando i campi
3. Clicca **"Genera App"** → scarica l'app per il tuo cliente

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

## ✨ Converter universale AI

Il nuovo `converter_universale.html` accetta PDF, DOCX, XLSX, XLS, CSV, TSV e TXT e invia il file al backend Cloudflare Worker. Il backend:

1. verifica formato, dimensione e firma del file;
2. applica rate limiting tramite KV;
3. invia il documento al provider AI usando una chiave conservata esclusivamente come secret server-side;
4. richiede un output conforme a `workout-plan.schema.json`;
5. valida e normalizza il risultato;
6. restituisce il piano JSON alla pagina di revisione.

Dal piano revisionato il browser genera deterministicamente:

- `scheda_normalizzata.csv` compatibile con il formato GymSheet;
- backup JSON versionato;
- app HTML standalone con tab persistenti, video esterni, note/storico e warning non bloccante.

### Deploy backend

1. Copia `wrangler.toml.example` in `wrangler.toml` e configura URL e KV ID.
2. Configura i secret sul Worker:

```bash
wrangler secret put OPENAI_API_KEY
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put STRIPE_WEBHOOK_SECRET
wrangler secret put RESEND_API_KEY
```

3. Pubblica il Worker:

```bash
wrangler deploy
```

4. Verifica `GET /ai/health`.
5. Se l'hostname del Worker è diverso, aggiorna `API_BASE` in `converter_universale.html`.
6. Pubblica i file statici su GitHub Pages.

### Configurazione AI

Le variabili non segrete sono in `wrangler.toml`:

```toml
AI_MODEL = "gpt-4.1"
AI_RATE_LIMIT_PER_HOUR = "10"
```

`OPENAI_API_KEY` non deve essere inserita nel repository né nel codice frontend.

### Contratto dati

`workout-plan.schema.json` è il formato canonico. Il CSV è un formato di compatibilità/export; non è la fonte dati interna.

### Sicurezza implementata

- allowlist dei formati;
- limite applicativo di 8 MB;
- controllo firma PDF/ZIP Office/XLS e rifiuto di contenuto binario nei file testuali;
- sanitizzazione del filename;
- CORS limitabile tramite `FRONTEND_URL`;
- rate limiting per IP via KV;
- prompt che tratta il documento come dato non attendibile;
- JSON Schema strict e validazione business server-side;
- nessuna chiave AI nel codice pubblico;
- nessuna persistenza del file sorgente nell'implementazione corrente.

### Limiti intenzionali dell'MVP

- `.doc` legacy e immagini non sono nella allowlist iniziale;
- il risultato AI deve sempre essere revisionato dall'utente prima dell'export;
- la conversione è sincrona e non mantiene job in background;
- i crediti AI non sono ancora scalati dai pacchetti trainer: il rate limit impedisce abuso di base, ma per monetizzazione va aggiunta una policy commerciale esplicita.

## Guida intelligente nell’editor

Ogni campo programma offre un catalogo di template con nome, descrizione, esempio e anteprima. I suggerimenti mostrano in tempo reale le card riconosciute e i vantaggi disponibili nell’app.

## Dialog personalizzate

Le pagine operative e le app generate utilizzano dialog GymSheet responsive al posto di `alert()`, `confirm()` e `prompt()`.

## Requisiti converter tradizionale

Il PDF deve contenere una tabella testuale con prima colonna `Esercizio`, colonne programma e link opzionale finale. La guida completa è in `istruzioni_template.html#formato-tradizionale`.


### Parser naturale e assistenza durante l’allenamento

Il parser accetta varianti come `4x10 rec 60`, `4 serie da 10 recupero 1 minuto` e `4 set da 10 con pause da 60"`. Le parti riconosciute diventano card interattive; ogni testo residuo resta visibile come nota. Le card serie/ripetizioni consentono di segnare le serie completate e avviare il recupero. Nell’app è sempre disponibile il pulsante timer con tempi rapidi e durata personalizzata.


### 📲 PWA local-first
- `index.html` è la libreria locale delle schede.
- `GymAppDB` / store `schede` conserva ogni HTML in IndexedDB.
- `sw.js` rende disponibili offline shell, converter e schede salvate.
- L’import/export usa direttamente file `.html`; il JSON non è più necessario.
- Quando disponibile, File System Access API sovrascrive il file scelto; sugli altri browser viene scaricata una nuova copia.
- I link email usano `?download_token=...`: la PWA riscatta il token, archivia e scarica la scheda.
