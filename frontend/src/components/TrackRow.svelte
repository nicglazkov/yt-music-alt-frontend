<script>
  import { createEventDispatcher } from 'svelte'
  export let track
  export let selected = false
  const dispatch = createEventDispatcher()

  $: thumb = track?.thumbnails?.[0]?.url ?? null
  let thumbError = false
  $: thumb, (thumbError = false)
</script>

{#if track}
<div class="row" class:selected>
  <input
    type="checkbox"
    checked={selected}
    on:click|stopPropagation={e => dispatch('select', { videoId: track.videoId, shiftKey: e.shiftKey })}
  />
  {#if thumb && !thumbError}
    <img class="thumb" src={thumb} alt="" aria-hidden="true" on:error={() => thumbError = true} />
  {:else}
    <div class="thumb thumb-placeholder"></div>
  {/if}
  <div class="info">
    <span class="title">{track.title}</span>
    <span class="meta">
      <span class="artists">{track.artists?.map(a => a.name).join(', ') ?? ''}</span>{#if track.album?.name}<span class="album"> · {track.album.name}</span>{/if}
    </span>
  </div>
</div>
{/if}

<style>
  .row { display:flex; align-items:center; gap:0.75rem; padding:0 1rem; height:100%; border-bottom:1px solid #1e1e1e; }
  .row:hover { background:#1a1a1a; }
  .row.selected { background:#1e1a2e; }
  input[type="checkbox"] { flex-shrink:0; accent-color:#ff0033; cursor:pointer; }
  .thumb { width:40px; height:40px; object-fit:cover; border-radius:3px; flex-shrink:0; }
  .thumb-placeholder { background:#2a2a2a; border-radius:3px; }
  .info { display:flex; flex-direction:column; gap:2px; min-width:0; }
  .title { color:#fff; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .meta { color:#666; font-size:0.78rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
</style>
