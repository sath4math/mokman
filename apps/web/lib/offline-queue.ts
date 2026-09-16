const DB_NAME = "mokman-field-offline";
const STORE_NAME = "pending-actions";
const DB_VERSION = 1;

export interface PendingAction {
  id: string;
  url: string;
  method: string;
  body: string | null;
  createdAt: number;
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function enqueueAction(action: { url: string; method: string; body?: object }): Promise<void> {
  const db = await openDb();
  const pending: PendingAction = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    url: action.url,
    method: action.method,
    body: action.body ? JSON.stringify(action.body) : null,
    createdAt: Date.now(),
  };
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.objectStore(STORE_NAME).add(pending);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

export async function listPending(): Promise<PendingAction[]> {
  const db = await openDb();
  const result = await new Promise<PendingAction[]>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const request = tx.objectStore(STORE_NAME).getAll();
    request.onsuccess = () => resolve(request.result as PendingAction[]);
    request.onerror = () => reject(request.error);
  });
  db.close();
  return result.sort((a, b) => a.createdAt - b.createdAt);
}

async function removePending(id: string): Promise<void> {
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.objectStore(STORE_NAME).delete(id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

/** Replays queued actions in order, stopping at the first one that still
 * fails (network still down, or a server error) so nothing is lost or
 * reordered. Safe to call repeatedly (e.g. on every `online` event). */
export async function flushPending(): Promise<{ flushed: number; remaining: number }> {
  const pending = await listPending();
  let flushed = 0;
  for (const action of pending) {
    try {
      const response = await fetch(action.url, {
        method: action.method,
        headers: action.body ? { "Content-Type": "application/json" } : undefined,
        body: action.body ?? undefined,
      });
      if (!response.ok && response.status >= 500) break;
      await removePending(action.id);
      flushed += 1;
    } catch {
      break;
    }
  }
  const remaining = (await listPending()).length;
  return { flushed, remaining };
}
