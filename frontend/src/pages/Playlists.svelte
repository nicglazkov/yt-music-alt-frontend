<script>
  import { playlists, showToast } from '../lib/store.js'
  import { post, del, get as apiGet } from '../lib/api.js'
  import Playlist from './Playlist.svelte'

  let openPlaylistId = null
  let creating = false
  let newTitle = ''

  async function createPlaylist() {
    if (!newTitle.trim()) return
    try {
      await post('/api/playlists', { title: newTitle.trim() })
      newTitle = ''
      creating = false
      playlists.set(await apiGet('/api/playlists'))
    } catch {
      showToast('Failed to create playlist')
    }
  }

  async function deletePlaylist(id) {
    if (!confirm('Delete this playlist?')) return
    try {
      await del(`/api/playlists/${id}`)
      playlists.update(p => p.filter(pl => pl.playlistId !== id))
    } catch {
      showToast('Failed to delete playlist')
    }
  }
</script>

{#if openPlaylistId}
  <Playlist playlistId={openPlaylistId} on:back={() => (openPlaylistId = null)} />
{:else}
  <div class="page">
    <div class="toolbar">
      <h2>Playlists</h2>
      <button on:click={() => (creating = true)}>+ New</button>
    </div>

    {#if creating}
      <div class="new-form">
        <input bind:value={newTitle} placeholder="Playlist name" autofocus />
        <button on:click={createPlaylist}>Create</button>
        <button on:click={() => (creating = false)}>Cancel</button>
      </div>
    {/if}

    <div class="grid">
      {#each $playlists as pl (pl.playlistId)}
        <div class="card" on:click={() => (openPlaylistId = pl.playlistId)}>
          <div class="thumb">
            {#if pl.thumbnails?.[0]?.url}
              <img src={pl.thumbnails[0].url} alt="" />
            {:else}
              <div class="placeholder">♪</div>
            {/if}
          </div>
          <div class="info">
            <span class="name">{pl.title}</span>
            <span class="count">{pl.count ?? '?'} songs</span>
          </div>
          <button class="del" on:click|stopPropagation={() => deletePlaylist(pl.playlistId)}>✕</button>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .page { display:flex; flex-direction:column; height:100%; padding:1rem; }
  .toolbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; }
  h2 { color:#fff; margin:0; font-size:1.1rem; }
  .toolbar button { background:#ff0033; color:#fff; border:none; border-radius:4px; padding:0.4rem 0.8rem; cursor:pointer; }
  .new-form { display:flex; gap:0.5rem; margin-bottom:1rem; }
  .new-form input { flex:1; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.4rem 0.6rem; }
  .new-form button { background:#333; color:#fff; border:none; border-radius:4px; padding:0.4rem 0.8rem; cursor:pointer; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:1rem; overflow-y:auto; }
  .card { background:#1a1a1a; border-radius:8px; overflow:hidden; cursor:pointer; position:relative; }
  .card:hover { background:#222; }
  .thumb { width:100%; aspect-ratio:1; background:#111; display:flex; align-items:center; justify-content:center; }
  .thumb img { width:100%; height:100%; object-fit:cover; }
  .placeholder { color:#444; font-size:2rem; }
  .info { padding:0.5rem; }
  .name { display:block; color:#fff; font-size:0.82rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .count { color:#666; font-size:0.75rem; }
  .del { display:none; position:absolute; top:4px; right:4px; background:rgba(0,0,0,.6); border:none; color:#aaa; border-radius:50%; width:22px; height:22px; cursor:pointer; align-items:center; justify-content:center; font-size:0.75rem; }
  .card:hover .del { display:flex; }
</style>
