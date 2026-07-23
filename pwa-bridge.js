import { salvaScheda } from './db.js';

function safeFilename(value) {
  const name = String(value || 'scheda.html').replace(/[^a-z0-9._-]/gi, '_');
  return name.toLowerCase().endsWith('.html') ? name : `${name}.html`;
}
function download(html, filename) {
  const url = URL.createObjectURL(new Blob([html], { type: 'text/html;charset=utf-8' }));
  const a = document.createElement('a'); a.href = url; a.download = safeFilename(filename);
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1500);
}
async function storeGenerated(html, filename, source = 'generated', shouldDownload = true) {
  const clean = safeFilename(filename);
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.replace(/<[^>]+>/g, '').trim() || clean.replace(/\.html$/i, '');
  const id = `${clean.replace(/\.html$/i, '').toLowerCase()}-${Date.now().toString(36)}`;
  const record = await salvaScheda(id, html, { filename: clean, title, source });
  if (shouldDownload) download(html, clean);
  return record;
}
window.GymSheetPWA = { ...(window.GymSheetPWA || {}), storeGenerated, downloadHtml: download };
