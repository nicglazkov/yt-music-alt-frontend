<script>
  import { createEventDispatcher } from 'svelte'
  import { selectionCount, clearSelection } from '../lib/store.js'
  export let actions = []  // [{ label, event }]
  const dispatch = createEventDispatcher()
</script>

{#if $selectionCount > 0}
  <div class="bar">
    <span class="count">{$selectionCount} selected</span>
    {#each actions as action}
      <button on:click={() => dispatch(action.event)}>{action.label}</button>
    {/each}
    <button class="clear" on:click={clearSelection}>✕ Clear</button>
  </div>
{/if}

<style>
  .bar { display:flex; align-items:center; gap:0.5rem; padding:0.5rem 1rem; background:#1e1a2e; border-top:1px solid #332244; flex-shrink:0; }
  .count { color:#aaa; font-size:0.85rem; margin-right:0.5rem; }
  button { background:#333; border:none; color:#fff; padding:0.35rem 0.75rem; border-radius:4px; cursor:pointer; font-size:0.85rem; }
  button:hover { background:#444; }
  .clear { background:none; color:#888; }
</style>
