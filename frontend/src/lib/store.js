import { writable, derived } from 'svelte/store'

export const library = writable([])
export const liked = writable([])
export const playlists = writable([])
export const syncStatus = writable({ lastSyncTime: null, syncInProgress: false, rateLimited: false })
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
