const DB_NAME = 'ytmusic'
const DB_VERSION = 1

function open() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = e => {
      const db = e.target.result
      if (!db.objectStoreNames.contains('cache')) {
        db.createObjectStore('cache', { keyPath: 'key' })
      }
    }
    req.onsuccess = e => resolve(e.target.result)
    req.onerror = e => reject(e.target.error)
  })
}

export async function dbGet(key) {
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('cache', 'readonly')
    const req = tx.objectStore('cache').get(key)
    req.onsuccess = e => resolve(e.target.result?.value ?? null)
    req.onerror = e => reject(e.target.error)
  })
}

export async function dbSet(key, value) {
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('cache', 'readwrite')
    tx.objectStore('cache').put({ key, value })
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}
