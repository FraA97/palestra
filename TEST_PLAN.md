# Test plan - Converter universale

## Backend
- `GET /ai/health` restituisce `ok: true`.
- assenza `OPENAI_API_KEY` -> HTTP 503.
- formato non consentito -> 415.
- estensione PDF con contenuto non PDF -> 415.
- file oltre 8 MB -> 413.
- limite orario superato -> 429.
- output AI non JSON -> 502.
- output non conforme -> 422 con `validationErrors`.
- URL in `prescription.raw` -> 422.
- URL in `videoUrl` -> accettato.
- `x 3 sfinimento` resta in `prescription.raw`, non diventa durata.

## Frontend
- drag/drop e selezione file;
- errore backend mostrato senza perdere la pagina;
- riepilogo programmi/esercizi/warning;
- modifica nome, prescrizione e video;
- modifica JSON avanzata con validazione;
- CSV UTF-8 BOM con intestazioni dinamiche;
- download JSON;
- generazione app HTML;
- JavaScript dell'HTML generato privo di errori sintattici.

## App generata
- tab programmi e storico;
- ultimo tab persistente dopo background/foreground;
- video aperto come link esterno;
- note vuote evidenziate;
- warning non bloccante al salvataggio incompleto;
- storico contenente solo esercizi annotati.
