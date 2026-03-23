import { writable, derived } from 'svelte/store'

export const ROW_SIZES = {
  small:  { rowHeight: 60, thumbSize: 40 },
  medium: { rowHeight: 76, thumbSize: 56 },
  large:  { rowHeight: 96, thumbSize: 72 },
}

const _defaultSettings = { rowSize: 'medium' }
const _savedSettings = (() => {
  try { return JSON.parse(localStorage.getItem('settings') ?? 'null') ?? _defaultSettings }
  catch { return _defaultSettings }
})()
export const settings = writable(_savedSettings)
settings.subscribe(v => { try { localStorage.setItem('settings', JSON.stringify(v)) } catch {} })

export const library = writable([])
export const liked = writable([])
export const playlists = writable([])
export const syncStatus = writable({ lastSyncTime: null, syncInProgress: false, rateLimited: false, authError: false, endpoints: {} })
export const selection = writable(new Set())

export const hasSelection = derived(selection, $s => $s.size > 0)
export const selectionCount = derived(selection, $s => $s.size)

export function toggleSelect(videoId) {
  selection.update(s => {
    const next = new Set(s)
    next.has(videoId) ? next.delete(videoId) : next.add(videoId)
    return next
  })
}

export function clearSelection() {
  selection.set(new Set())
}

export const toast = writable(null)

let _toastTimer = null

export function showToast(msg, duration = 3500) {
  if (_toastTimer) clearTimeout(_toastTimer)
  toast.set(msg)
  _toastTimer = setTimeout(() => { toast.set(null); _toastTimer = null }, duration)
}

export function selectRange(items, fromIndex, toIndex) {
  const [start, end] = fromIndex <= toIndex ? [fromIndex, toIndex] : [toIndex, fromIndex]
  selection.update(s => {
    const next = new Set(s)
    for (let i = start; i <= end; i++) {
      if (items[i]?.videoId) next.add(items[i].videoId)
    }
    return next
  })
}
