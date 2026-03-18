<script>
  import { library, selection, toggleSelect, selectRange, settings, ROW_SIZES } from '../lib/store.js'
  import VirtualList from '../components/VirtualList.svelte'
  import TrackRow from '../components/TrackRow.svelte'
  import BulkActionBar from '../components/BulkActionBar.svelte'

  let filter = ''
  let sortKey = 'title'
  let lastClickedIndex = null

  $: filtered = $library.filter(t =>
    !filter ||
    [t.title, ...(t.artists?.map(a => a.name) ?? []), t.album?.name]
      .some(s => s?.toLowerCase().includes(filter.toLowerCase()))
  )

  $: sorted = [...filtered].sort((a, b) => {
    if (sortKey === 'title')     return a.title.localeCompare(b.title)
    if (sortKey === 'artist')    return (a.artists?.[0]?.name ?? '').localeCompare(b.artists?.[0]?.name ?? '')
    if (sortKey === 'album')     return (a.album?.name ?? '').localeCompare(b.album?.name ?? '')
    if (sortKey === 'dateAdded') return 0  // preserve API order (already date-ordered from ytmusicapi)
    return 0
  })

  $: filter, sortKey, (lastClickedIndex = null)

  function handleSelect(e, index) {
    if (e.detail.shiftKey && lastClickedIndex !== null) {
      selectRange(sorted, lastClickedIndex, index)
    } else {
      toggleSelect(e.detail.videoId)
    }
    lastClickedIndex = index
  }

  const bulkActions = []

  let containerHeight = 500
  function measureHeight(node) {
    const obs = new ResizeObserver(entries => (containerHeight = entries[0].contentRect.height))
    obs.observe(node)
    return { destroy: () => obs.disconnect() }
  }
</script>

<div class="page">
  <div class="toolbar">
    <input class="filter" bind:value={filter} placeholder="Filter..." />
    <select bind:value={sortKey}>
      <option value="title">Title</option>
      <option value="artist">Artist</option>
      <option value="album">Album</option>
      <option value="dateAdded">Date Added</option>
    </select>
    <span class="count">{sorted.length} songs</span>
  </div>

  <div class="list" use:measureHeight>
    <VirtualList items={sorted} rowHeight={ROW_SIZES[$settings.rowSize].rowHeight} height={containerHeight}>
      <svelte:fragment slot="default" let:item let:index>
        <TrackRow
          track={item}
          selected={$selection.has(item.videoId)}
          on:select={e => handleSelect(e, index)}
        />
      </svelte:fragment>
    </VirtualList>
  </div>

  <BulkActionBar actions={bulkActions} />
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .toolbar { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .filter { flex:1; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.6rem; font-size:0.9rem; }
  select { background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.5rem; font-size:0.85rem; }
  .count { color:#666; font-size:0.82rem; white-space:nowrap; }
  .list { flex:1; overflow:hidden; }
</style>
