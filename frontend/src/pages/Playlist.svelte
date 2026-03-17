<script>
  import { onMount, createEventDispatcher } from 'svelte'
  import { get as apiGet, post, patch } from '../lib/api.js'
  import { selection, toggleSelect, clearSelection } from '../lib/store.js'
  import VirtualList from '../components/VirtualList.svelte'
  import TrackRow from '../components/TrackRow.svelte'
  import BulkActionBar from '../components/BulkActionBar.svelte'

  export let playlistId
  const dispatch = createEventDispatcher()

  let playlist = null
  let tracks = []
  let loading = true
  let editing = false
  let newTitle = ''

  onMount(async () => {
    playlist = await apiGet(`/api/playlists/${playlistId}`)
    tracks = playlist.tracks ?? []
    loading = false
  })

  async function rename() {
    await patch(`/api/playlists/${playlistId}`, { title: newTitle })
    playlist = { ...playlist, title: newTitle }
    editing = false
  }

  async function removeTracks() {
    const toRemove = tracks.filter(t => $selection.has(t.videoId))
    const items = toRemove.map(t => ({ videoId: t.videoId, setVideoId: t.setVideoId }))
    const removeIds = new Set(toRemove.map(t => t.setVideoId))
    // Optimistic update
    const prev = [...tracks]
    tracks = tracks.filter(t => !removeIds.has(t.setVideoId))
    clearSelection()
    try {
      await post(`/api/playlists/${playlistId}/tracks/remove`, { items })
    } catch {
      tracks = prev  // rollback on failure
    }
  }

  const bulkActions = [{ label: 'Remove', event: 'remove' }]

  let containerHeight = 500
  function measureHeight(node) {
    const obs = new ResizeObserver(e => (containerHeight = e[0].contentRect.height))
    obs.observe(node)
    return { destroy: () => obs.disconnect() }
  }
</script>

<div class="page">
  <div class="header">
    <button class="back" on:click={() => dispatch('back')}>← Back</button>
    {#if editing}
      <input bind:value={newTitle} />
      <button on:click={rename}>Save</button>
      <button on:click={() => (editing = false)}>Cancel</button>
    {:else}
      <h2>{playlist?.title ?? ''}</h2>
      <button on:click={() => { editing = true; newTitle = playlist.title }}>Rename</button>
    {/if}
    <span class="count">{tracks.length} songs</span>
  </div>

  <div class="list" use:measureHeight>
    {#if loading}
      <p style="color:#888;padding:1rem">Loading...</p>
    {:else}
      <VirtualList items={tracks} rowHeight={60} height={containerHeight}>
        <svelte:fragment slot="default" let:item>
          <TrackRow
            track={item}
            selected={$selection.has(item.videoId)}
            on:select={() => toggleSelect(item.videoId)}
          />
        </svelte:fragment>
      </VirtualList>
    {/if}
  </div>

  <BulkActionBar actions={bulkActions} on:remove={removeTracks} />
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .header { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .back { background:none; border:none; color:#888; cursor:pointer; font-size:0.9rem; }
  h2 { color:#fff; margin:0; font-size:1rem; flex:1; }
  .header button:not(.back) { background:#333; border:none; color:#fff; padding:0.3rem 0.6rem; border-radius:4px; cursor:pointer; font-size:0.82rem; }
  .header input { background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.3rem 0.5rem; flex:1; }
  .count { color:#666; font-size:0.82rem; margin-left:auto; white-space:nowrap; }
  .list { flex:1; overflow:hidden; }
</style>
