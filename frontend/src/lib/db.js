const DB_NAME = 'ytmusic'
const DB_VERSION = 2

let _dbPromise = null

function open() {
  if (!_dbPromise) {
    _dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION)
      req.onupgradeneeded = e => {
        const db = e.target.result
        if (!db.objectStoreNames.contains('cache')) {
          db.createObjectStore('cache', { keyPath: 'key' })
        }
        if (!db.objectStoreNames.contains('thumbnails')) {
          db.createObjectStore('thumbnails', { keyPath: 'videoId' })
        }
      }
      req.onsuccess = e => resolve(e.target.result)
      req.onerror = e => reject(e.target.error)
    })
  }
  return _dbPromise
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

export async function thumbGet(videoId) {
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('thumbnails', 'readonly')
    const req = tx.objectStore('thumbnails').get(videoId)
    req.onsuccess = e => {
      const row = e.target.result
      if (!row) { resolve(null); return }
      resolve(URL.createObjectURL(new Blob([row.data], { type: row.type })))
    }
    req.onerror = e => reject(e.target.error)
  })
}

export async function thumbSet(videoId, cdnUrl) {
  const resp = await fetch(cdnUrl)
  if (!resp.ok) return
  const type = resp.headers.get('content-type') || 'image/jpeg'
  const data = await resp.arrayBuffer()
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('thumbnails', 'readwrite')
    tx.objectStore('thumbnails').put({ videoId, data, type })
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}

export async function thumbClear() {
  const db = await open()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('thumbnails', 'readwrite')
    tx.objectStore('thumbnails').clear()
    tx.oncomplete = () => resolve()
    tx.onerror = e => reject(e.target.error)
  })
}
