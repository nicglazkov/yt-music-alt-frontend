<script>
  import { onMount } from 'svelte'
  import { get as apiGet, getToken } from './lib/api.js'
  import { dbGet, dbSet } from './lib/db.js'
  import { library, liked, playlists, syncStatus, toast, showToast } from './lib/store.js'
  import Login from './pages/Login.svelte'
  import Library from './pages/Library.svelte'
  import Playlists from './pages/Playlists.svelte'
  import Liked from './pages/Liked.svelte'
  import Search from './pages/Search.svelte'

  let authed = !!getToken()
  let activeTab = localStorage.getItem('activeTab') ?? 'library'

  function setTab(id) {
    activeTab = id
    localStorage.setItem('activeTab', id)
  }
  let loading = true
  const TABS = [
    { id: 'library', label: 'Library' },
    { id: 'playlists', label: 'Playlists' },
    { id: 'liked', label: 'Liked' },
    { id: 'search', label: 'Search' },
  ]

  async function loadData() {
    loading = true
    // Load IndexedDB immediately for instant display
    const cachedLib = await dbGet('library')
    if (cachedLib) library.set(cachedLib.songs)
    const cachedLiked = await dbGet('liked')
    if (cachedLiked) liked.set(cachedLiked.songs)
    const cachedPlaylists = await dbGet('playlists')
    if (cachedPlaylists) playlists.set(cachedPlaylists.items)
    loading = !cachedLib  // only show full-screen loader if nothing cached

    // Reconcile with server
    try {
      const status = await apiGet('/api/status')
      syncStatus.set(status)
      if (!cachedLib || status.lastSyncTime > (cachedLib.syncTime ?? 0)) {
        await refreshFromServer(status.lastSyncTime)
      }
    } catch {
      showToast('Failed to sync — using cached data')
    } finally {
      loading = false
    }
  }

  async function refreshFromServer(syncTime) {
    const [songs, likedSongs, playlistItems] = await Promise.all([
      apiGet('/api/library'),
      apiGet('/api/liked'),
      apiGet('/api/playlists'),
    ])
    library.set(songs)
    liked.set(likedSongs)
    playlists.set(playlistItems)
    await Promise.all([
      dbSet('library', { songs, syncTime }),
      dbSet('liked', { songs: likedSongs, syncTime }),
      dbSet('playlists', { items: playlistItems, syncTime }),
    ])
  }

  onMount(async () => {
    if (authed) await loadData()
  })
</script>

{#if !authed}
  <Login on:loggedin={async () => { authed = true; await loadData() }} />
{:else}
  <div class="app">
    <nav>
      <span class="logo">♪ YTM</span>
      {#each TABS as tab}
        <button class:active={activeTab === tab.id} on:click={() => setTab(tab.id)}>
          {tab.label}
        </button>
      {/each}
      {#if $syncStatus.syncInProgress}
        <span class="syncing">↻ Syncing</span>
      {:else if $syncStatus.rateLimited}
        <span class="rate-limited">Sync paused</span>
      {/if}
    </nav>
    <main>
      {#if loading}
        <div class="loading">Loading your library...</div>
      {:else if activeTab === 'library'}
        <Library />
      {:else if activeTab === 'playlists'}
        <Playlists />
      {:else if activeTab === 'liked'}
        <Liked />
      {:else if activeTab === 'search'}
        <Search />
      {/if}
    </main>
  </div>
  {#if $toast}
    <div class="toast">{$toast}</div>
  {/if}
{/if}

<style>
  :global(*, *::before, *::after) { box-sizing: border-box; }
  :global(body) { margin:0; background:#0f0f0f; color:#fff; font-family:system-ui,sans-serif; }
  .app { display:flex; flex-direction:column; height:100vh; }
  nav { display:flex; align-items:center; gap:0.25rem; padding:0 1rem; background:#1a1a1a; border-bottom:1px solid #222; flex-shrink:0; }
  .logo { font-weight:700; color:#ff0033; padding:0.75rem 0.5rem; margin-right:0.5rem; }
  nav button { background:none; border:none; color:#888; padding:0.75rem; cursor:pointer; font-size:0.9rem; border-bottom:2px solid transparent; }
  nav button.active { color:#fff; border-bottom-color:#ff0033; }
  .syncing { color:#888; font-size:0.78rem; margin-left:auto; }
  .rate-limited { color:#ff6b6b; font-size:0.78rem; margin-left:auto; }
  main { flex:1; overflow:hidden; }
  .loading { display:flex; align-items:center; justify-content:center; height:100%; color:#888; }
  .toast { position:fixed; bottom:1.5rem; left:50%; transform:translateX(-50%); background:#333; color:#fff; padding:0.6rem 1.2rem; border-radius:4px; font-size:0.9rem; z-index:100; }
</style>
