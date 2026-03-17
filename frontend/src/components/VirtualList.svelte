<script>
  export let items = []
  export let rowHeight = 60
  export let height = 600

  let scrollTop = 0
  const BUFFER = 5

  $: total = items.length * rowHeight
  $: startIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - BUFFER)
  $: endIndex = Math.min(items.length, Math.ceil((scrollTop + height) / rowHeight) + BUFFER)
  $: visible = items.slice(startIndex, endIndex)
  $: offsetY = startIndex * rowHeight
</script>

<div
  style="height:{height}px;overflow-y:auto;"
  on:scroll={e => (scrollTop = e.currentTarget.scrollTop)}
>
  <div style="height:{total}px;position:relative;">
    <div style="transform:translateY({offsetY}px);">
      {#each visible as item, i (item.videoId ?? startIndex + i)}
        <div data-index={startIndex + i} style="height:{rowHeight}px;">
          <slot {item} index={startIndex + i} />
        </div>
      {/each}
    </div>
  </div>
</div>
