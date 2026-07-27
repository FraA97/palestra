import { salvaScheda, getSchede, getSchedaById, eliminaScheda } from './db.js?v=20260727-1';

const WORKER_BASE = 'https://gymsheet-worker.francescoartibani.workers.dev';
const list = document.getElementById('sheet-list');
const statusBox = document.getElementById('app-status');
const importInput = document.getElementById('import-html');
const installButton = document.getElementById('install-app');
const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent);
const isStandalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
let deferredInstallPrompt = null;

function setStatus(message, type = '') {
  if (!statusBox) return;
  statusBox.textContent = message;
  statusBox.className = `status ${type}`;
  statusBox.hidden = !message;
}

function safeFilename(value) {
  const cleaned = String(value || 'scheda.html').replace(/[^a-z0-9._-]/gi, '_');
  return cleaned.toLowerCase().endsWith('.html') ? cleaned : `${cleaned}.html`;
}

function idFromFilename(filename) {
  const base = safeFilename(filename).replace(/\.html$/i, '').toLowerCase();
  return `${base}-${Date.now().toString(36)}-${crypto.getRandomValues(new Uint32Array(1))[0].toString(36)}`;
}

function titleFromHtml(html, fallback = 'Scheda GymSheet') {
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]
    ?.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').trim();
  return title || fallback;
}

function filenameFromDisposition(value) {
  if (!value) return '';
  const utf = value.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf) return decodeURIComponent(utf[1].replace(/["']/g, ''));
  return value.match(/filename="?([^";]+)"?/i)?.[1] || '';
}

export function downloadHtml(html, filename = 'scheda.html') {
  const url = URL.createObjectURL(new Blob([html], { type: 'text/html;charset=utf-8' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = safeFilename(filename);
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

export async function storeAndDownloadHtml(html, metaData = {}, options = {}) {
  const filename = safeFilename(metaData.filename || 'scheda.html');
  const id = metaData.id || idFromFilename(filename);
  const record = await salvaScheda(id, html, {
    filename,
    title: metaData.title || titleFromHtml(html, filename.replace(/\.html$/i, '')),
    source: metaData.source || 'local',
    importedAt: metaData.importedAt || new Date().toISOString()
  });
  if (options.download !== false) downloadHtml(html, filename);
  await renderLibrary();
  if (options.open !== false) await openSheet(record.id);
  return record;
}

export async function importHtmlFile(file) {
  if (!file || !/\.html?$/i.test(file.name)) throw new Error('Seleziona un file .html');
  const html = await file.text();
  if (!/<html[\s>]/i.test(html) || !/<\/html>/i.test(html)) throw new Error('Il file non contiene un documento HTML completo');
  return storeAndDownloadHtml(html, { filename: file.name, source: 'import' }, { download: false });
}

export async function openSheet(id) {
  const record = await getSchedaById(id);
  if (!record) throw new Error('Scheda non trovata');
  if ('serviceWorker' in navigator) await navigator.serviceWorker.ready;
  const route = `./schede/${encodeURIComponent(id)}.html`;
  window.location.href = route;
}

async function deleteSheet(id) {
  const record = await getSchedaById(id);
  if (!record) return;
  if (!confirm(`Eliminare "${record.metaData?.title || record.metaData?.filename || 'questa scheda'}" dal dispositivo?`)) return;
  await eliminaScheda(id);
  await renderLibrary();
}

async function exportStoredSheet(id) {
  const record = await getSchedaById(id);
  if (!record) return;
  downloadHtml(record.htmlString, record.metaData?.filename || `${id}.html`);
}

export async function renderLibrary() {
  if (!list) return;
  const records = await getSchede();
  if (!records.length) {
    list.innerHTML = '<div class="empty"><strong>Nessuna scheda salvata</strong><span>Importa un file HTML oppure genera una nuova scheda.</span></div>';
    return;
  }
  list.innerHTML = '';
  for (const record of records) {
    const card = document.createElement('article');
    card.className = 'sheet-card';
    const title = record.metaData?.title || record.metaData?.filename || 'Scheda GymSheet';
    const date = new Date(record.updatedAt).toLocaleString('it-IT', { dateStyle: 'medium', timeStyle: 'short' });
    card.innerHTML = `<div><h3></h3><p></p></div><div class="card-actions"><button class="open">Apri</button><button class="download">Scarica</button><button class="delete" aria-label="Elimina">🗑</button></div>`;
    card.querySelector('h3').textContent = title;
    card.querySelector('p').textContent = `Aggiornata ${date} · ${record.metaData?.source || 'locale'}`;
    card.querySelector('.open').onclick = () => openSheet(record.id).catch(error => setStatus(error.message, 'error'));
    card.querySelector('.download').onclick = () => exportStoredSheet(record.id);
    card.querySelector('.delete').onclick = () => deleteSheet(record.id);
    list.appendChild(card);
  }
}

async function redeemDownloadToken(token) {
  setStatus('Recupero della scheda acquistata…', 'working');
  const response = await fetch(`${WORKER_BASE}/download?token=${encodeURIComponent(token)}`, {
    headers: { Accept: 'text/html' }, cache: 'no-store'
  });
  if (!response.ok) {
    let message = `Download non disponibile (HTTP ${response.status})`;
    try { message = (await response.json()).error || message; } catch { /* response HTML/text */ }
    throw new Error(message);
  }
  const html = await response.text();
  const filename = safeFilename(filenameFromDisposition(response.headers.get('Content-Disposition')) || 'scheda-gymsheet.html');
  history.replaceState(null, '', `${location.pathname}${location.hash || ''}`);
  await storeAndDownloadHtml(html, { filename, source: 'email-token' }, { download: true, open: true });
}

async function registerPwa() {
  if ('serviceWorker' in navigator) {
    try { await navigator.serviceWorker.register('./sw.js', { scope: './' }); }
    catch (error) { console.error('Service worker non registrato', error); }
  }
  if (navigator.storage?.persist) {
    try { await navigator.storage.persist(); } catch { /* richiesta non concessa */ }
  }
}

window.addEventListener('beforeinstallprompt', event => {
  event.preventDefault();
  deferredInstallPrompt = event;
  if (installButton) installButton.hidden = false;
});

window.addEventListener('appinstalled', () => {
  deferredInstallPrompt = null;
  if (installButton) installButton.hidden = true;
  setStatus('GymSheet installata sul dispositivo.', 'success');
});

installButton?.addEventListener('click', async () => {
  if (isStandalone) { setStatus('GymSheet è già installata sul dispositivo.', 'success'); return; }
  if (!deferredInstallPrompt) {
    setStatus(isIos ? 'Su iPhone/iPad: apri questa pagina in Safari, tocca Condividi e scegli “Aggiungi alla schermata Home”.' : 'Apri il menu del browser e scegli “Installa app” oppure “Aggiungi alla schermata Home”.', 'info');
    return;
  }
  deferredInstallPrompt.prompt();
  await deferredInstallPrompt.userChoice;
  deferredInstallPrompt = null;
  installButton.hidden = true;
});

importInput?.addEventListener('change', async () => {
  try {
    const file = importInput.files?.[0];
    if (!file) return;
    setStatus('Importazione del file HTML…', 'working');
    await importHtmlFile(file);
    setStatus('Scheda importata e salvata sul dispositivo.', 'success');
  } catch (error) { setStatus(error.message, 'error'); }
  finally { importInput.value = ''; }
});

document.getElementById('import-trigger')?.addEventListener('click', () => importInput?.click());

window.GymSheetPWA = { storeAndDownloadHtml, importHtmlFile, downloadHtml, renderLibrary };

await registerPwa();
await renderLibrary();
const token = new URLSearchParams(location.search).get('download_token');
if (token) {
  try { await redeemDownloadToken(token); }
  catch (error) {
    history.replaceState(null, '', `${location.pathname}${location.hash || ''}`);
    setStatus(error.message, 'error');
  }
}
