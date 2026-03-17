<script>
  import { login } from '../lib/api.js'
  import { createEventDispatcher } from 'svelte'

  const dispatch = createEventDispatcher()
  let password = ''
  let error = ''
  let loading = false

  async function handleSubmit() {
    error = ''
    loading = true
    try {
      await login(password)
      dispatch('loggedin')
    } catch {
      error = 'Incorrect password'
    } finally {
      loading = false
    }
  }
</script>

<div class="wrap">
  <div class="box">
    <h1>YT Music</h1>
    <form on:submit|preventDefault={handleSubmit}>
      <input
        type="password"
        bind:value={password}
        placeholder="Password"
        autocomplete="current-password"
        disabled={loading}
      />
      {#if error}<p class="error">{error}</p>{/if}
      <button type="submit" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  </div>
</div>

<style>
  .wrap { display:flex; align-items:center; justify-content:center; height:100vh; background:#0f0f0f; }
  .box { background:#1a1a1a; border-radius:8px; padding:2rem; width:300px; }
  h1 { color:#fff; margin:0 0 1.5rem; font-size:1.3rem; }
  input { width:100%; padding:0.6rem 0.8rem; background:#111; border:1px solid #333; border-radius:4px; color:#fff; font-size:1rem; box-sizing:border-box; }
  button { width:100%; margin-top:0.75rem; padding:0.6rem; background:#ff0033; color:#fff; border:none; border-radius:4px; font-size:1rem; cursor:pointer; }
  button:disabled { opacity:0.6; cursor:not-allowed; }
  .error { color:#ff6b6b; font-size:0.85rem; margin:0.4rem 0 0; }
</style>
