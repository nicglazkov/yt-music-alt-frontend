<script>
  import { liked, selection, toggleSelect, clearSelection } from '../lib/store.js'
  import VirtualList from '../components/VirtualList.svelte'
  import TrackRow from '../components/TrackRow.svelte'
  import BulkActionBar from '../components/BulkActionBar.svelte'
  import { post } from '../lib/api.js'

  let filter = ''

  $: filtered = $liked.filter(t =>
    !filter || t.title?.toLowerCase().includes(filter.toLowerCase())
  )

  async function unlike() {
    const videoIds = [...$selection]
    await post('/api/liked/unlike', { videoIds })
    liked.update(l => l.filter(t => !$selection.has(t.videoId)))
    clearSelection()
  }

  const bulkActions = [{ label: 'Unlike', event: 'unlike' }]

  let containerHeight = 500
  function measureHeight(node) {
    const obs = new ResizeObserver(e => (containerHeight = e[0].contentRect.height))
    obs.observe(node)
    return { destroy: () => obs.disconnect() }
  }
</script>

<div class="page">
  <div class="toolbar">
    <input class="filter" bind:value={filter} placeholder="Filter..." />
    <span class="count">{filtered.length} songs</span>
  </div>
  <div class="list" use:measureHeight>
    <VirtualList items={filtered} rowHeight={60} height={containerHeight}>
      <svelte:fragment slot="default" let:item>
        <TrackRow
          track={item}
          selected={$selection.has(item.videoId)}
          on:select={() => toggleSelect(item.videoId)}
        />
      </svelte:fragment>
    </VirtualList>
  </div>
  <BulkActionBar actions={bulkActions} on:unlike={unlike} />
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .toolbar { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .filter { flex:1; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.6rem; font-size:0.9rem; }
  .count { color:#666; font-size:0.82rem; white-space:nowrap; }
  .list { flex:1; overflow:hidden; }
</style>
