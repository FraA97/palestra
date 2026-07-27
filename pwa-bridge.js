import { salvaScheda, getBackupSettings, saveBackupSettings } from './db.js?v=20260727-3';

function safeFilename(value) {
  const name = String(value || 'scheda.html').replace(/[^a-z0-9._-]/gi, '_');
  return name.toLowerCase().endsWith('.html') ? name : `${name}.html`;
}
function download(html, filename) {
  const url = URL.createObjectURL(new Blob([html], { type: 'text/html;charset=utf-8' }));
  const a = document.createElement('a'); a.href = url; a.download = safeFilename(filename);
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1500);
}

async function writeGlobalBackup(html,filename){
  if(!('showDirectoryPicker' in window))return false;
  const settings=await getBackupSettings();const dir=settings?.directoryHandle;if(!dir)return false;
  if(await dir.queryPermission({mode:'readwrite'})!=='granted')return false;
  const file=await dir.getFileHandle(safeFilename(filename),{create:true});const out=await file.createWritable();await out.write(html);await out.close();
  await saveBackupSettings({...settings,lastSuccessAt:Date.now(),lastFilename:safeFilename(filename)});return true;
}
async function storeGenerated(html, filename, source = 'generated', shouldDownload = true, shouldOpen = true) {
  const clean = safeFilename(filename);
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.replace(/<[^>]+>/g, '').trim() || clean.replace(/\.html$/i, '');
  const id = `${clean.replace(/\.html$/i, '').toLowerCase()}-${Date.now().toString(36)}`;
  const record = await salvaScheda(id, html, { filename: clean, title, source });
  try { await writeGlobalBackup(html, clean); } catch(error) { console.warn('Backup cartella non riuscito',error); }
  if (shouldDownload) download(html, clean);
  if (shouldOpen) {
    if ('serviceWorker' in navigator) await navigator.serviceWorker.ready;
    location.href = `./schede/${encodeURIComponent(record.id)}.html`;
  }
  return record;
}
window.GymSheetPWA = { ...(window.GymSheetPWA || {}), storeGenerated, downloadHtml: download };
