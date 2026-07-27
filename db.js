const DB_NAME = 'GymAppDB';
const DB_VERSION = 2;
const STORE_NAME = 'schede';

function requestToPromise(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error('Errore IndexedDB'));
  });
}

export function openGymDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('updatedAt', 'updatedAt');
        store.createIndex('createdAt', 'createdAt');
      }
      if (!db.objectStoreNames.contains('fileHandles')) db.createObjectStore('fileHandles', { keyPath: 'id' });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error('Impossibile aprire GymAppDB'));
    request.onblocked = () => reject(new Error('Aggiornamento database bloccato da un’altra scheda aperta'));
  });
}

async function run(storeMode, action) {
  const db = await openGymDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, storeMode);
    const store = tx.objectStore(STORE_NAME);
    let result;
    try { result = action(store); } catch (error) { db.close(); reject(error); return; }
    tx.oncomplete = async () => {
      try { resolve(result instanceof IDBRequest ? result.result : result); }
      catch (error) { reject(error); }
      finally { db.close(); }
    };
    tx.onerror = () => { db.close(); reject(tx.error || new Error('Transazione IndexedDB non riuscita')); };
    tx.onabort = () => { db.close(); reject(tx.error || new Error('Transazione IndexedDB annullata')); };
  });
}

export async function salvaScheda(id, htmlString, metaData = {}) {
  if (!id) throw new Error('ID scheda obbligatorio');
  if (typeof htmlString !== 'string' || !htmlString.trim()) throw new Error('HTML scheda non valido');
  const existing = await getSchedaById(id);
  const now = Date.now();
  const record = {
    id,
    htmlString,
    metaData: { ...(existing?.metaData || {}), ...metaData },
    createdAt: existing?.createdAt || now,
    updatedAt: now
  };
  await run('readwrite', store => store.put(record));
  return record;
}

export async function getSchede() {
  const db = await openGymDB();
  try {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const records = await requestToPromise(tx.objectStore(STORE_NAME).getAll());
    return (records || []).sort((a, b) => b.updatedAt - a.updatedAt);
  } finally { db.close(); }
}

export async function getSchedaById(id) {
  const db = await openGymDB();
  try {
    const tx = db.transaction(STORE_NAME, 'readonly');
    return (await requestToPromise(tx.objectStore(STORE_NAME).get(id))) || null;
  } finally { db.close(); }
}

export async function aggiornaDatiScheda(id, nuoviDatiHTML, metaData = {}) {
  const existing = await getSchedaById(id);
  if (!existing) throw new Error('Scheda non trovata');
  return salvaScheda(id, nuoviDatiHTML, { ...existing.metaData, ...metaData });
}

export async function eliminaScheda(id) {
  await run('readwrite', store => store.delete(id));
}

export async function clearSchede() {
  await run('readwrite', store => store.clear());
}
