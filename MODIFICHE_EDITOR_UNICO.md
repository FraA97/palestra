# Editor unico GymSheet

- `converter_universale.html` non contiene più un secondo editor né un secondo generatore HTML.
- Dopo `/ai/convert`, il piano AI viene adattato al modello della bozza di `editor_scheda.html`.
- La pagina reindirizza a `editor_scheda.html?source=ai`.
- L'utente modifica la scheda usando esattamente lo stesso editor tradizionale.
- Anteprima, paywall e HTML finale usano quindi lo stesso `generateHtml()` V3 dell'editor tradizionale.
- Warning e confidence AI sono conservati in un report mostrato in alto nell'editor.
- `converter.html` resta invariato.
- `worker.js` include anche la correzione dello schema `schemaVersion.type`.
