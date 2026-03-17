import { describe, it, expect, beforeEach } from 'vitest'
import { get } from 'svelte/store'
import { library, selection, toggleSelect, clearSelection, selectRange } from './store.js'

describe('store', () => {
  beforeEach(() => {
    clearSelection()
  })

  it('library starts empty', () => {
    expect(get(library)).toEqual([])
  })

  it('toggleSelect adds to selection', () => {
    clearSelection()
    toggleSelect('aaa')
    expect(get(selection).has('aaa')).toBe(true)
  })

  it('toggleSelect removes already-selected item', () => {
    clearSelection()
    toggleSelect('aaa')
    toggleSelect('aaa')
    expect(get(selection).has('aaa')).toBe(false)
  })

  it('clearSelection empties set', () => {
    toggleSelect('aaa')
    clearSelection()
    expect(get(selection).size).toBe(0)
  })

  it('selectRange selects items between two indices inclusive', () => {
    const songs = [{ videoId: 'a' }, { videoId: 'b' }, { videoId: 'c' }, { videoId: 'd' }]
    library.set(songs)
    clearSelection()
    selectRange(songs, 1, 3)
    const sel = get(selection)
    expect(sel.has('b')).toBe(true)
    expect(sel.has('c')).toBe(true)
    expect(sel.has('d')).toBe(true)
    expect(sel.has('a')).toBe(false)
  })
})
