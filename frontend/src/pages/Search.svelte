<script>
  import { get as apiGet, post } from '../lib/api.js'

  let query = ''
  let results = []
  let loading = false
  let searched = false
  let debounceTimer

  function onInput() {
    clearTimeout(debounceTimer)
    if (query.length < 2) { results = []; searched = false; return }
    debounceTimer = setTimeout(search, 400)
  }

  async function search() {
    loading = true
    searched = true
    results = await apiGet(`/api/search?q=${encodeURIComponent(query)}`)
    loading = false
  }

  async function addToLibrary(r) {
    const feedbackToken = r.feedbackTokens?.add
    if (!feedbackToken) return
    await post('/api/library/save', { feedbackTokens: [feedbackToken] })
    results = results.map(x => x.videoId === r.videoId ? { ...x, inLibrary: true } : x)
  }

  async function like(videoId) {
    await post('/api/liked', { videoIds: [videoId] })
  }
</script>

<div class="page">
  <div class="toolbar">
    <input
      class="search-input"
      bind:value={query}
      on:input={onInput}
      placeholder="Search YouTube Music..."
    />
  </div>
  <div class="results">
    {#if loading}
      <p class="hint">Searching...</p>
    {:else if searched && results.length === 0}
      <p class="hint">No results found.</p>
    {:else if !searched}
      <p class="hint">Type to search the YouTube Music catalog.</p>
    {:else}
      {#each results as r (r.videoId)}
        <div class="row">
          <div class="info">
            <span class="title">{r.title}</span>
            <span class="meta">{r.artists?.map(a => a.name).join(', ') ?? ''}</span>
          </div>
          <button disabled={r.inLibrary} on:click={() => addToLibrary(r)}>
            {r.inLibrary ? 'In Library' : '+ Library'}
          </button>
          <button on:click={() => like(r.videoId)}>♥</button>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .page { display:flex; flex-direction:column; height:100%; }
  .toolbar { padding:0.5rem 1rem; background:#141414; border-bottom:1px solid #222; flex-shrink:0; }
  .search-input { width:100%; background:#111; border:1px solid #333; border-radius:4px; color:#fff; padding:0.5rem 0.75rem; font-size:1rem; box-sizing:border-box; }
  .results { flex:1; overflow-y:auto; }
  .hint { color:#555; padding:2rem 1rem; text-align:center; font-size:0.9rem; }
  .row { display:flex; align-items:center; gap:0.5rem; padding:0.6rem 1rem; border-bottom:1px solid #1e1e1e; }
  .row:hover { background:#1a1a1a; }
  .info { flex:1; min-width:0; }
  .title { display:block; color:#fff; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .meta { color:#666; font-size:0.78rem; }
  button { background:#333; border:none; color:#fff; padding:0.3rem 0.6rem; border-radius:4px; cursor:pointer; font-size:0.8rem; white-space:nowrap; }
  button:hover:not(:disabled) { background:#444; }
  button:disabled { opacity:0.5; cursor:default; }
</style>
