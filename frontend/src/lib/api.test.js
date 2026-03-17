import { describe, it, expect, vi, beforeEach } from 'vitest'
import { login, get, post, patch, del } from './api.js'

describe('api', () => {
  beforeEach(() => {
    sessionStorage.clear()
    global.fetch = vi.fn()
  })

  it('login stores token in sessionStorage', async () => {
    global.fetch.mockResolvedValue({ ok: true, json: async () => ({ token: 'abc123' }) })
    await login('mypassword')
    expect(sessionStorage.getItem('token')).toBe('abc123')
  })

  it('login throws on bad password', async () => {
    global.fetch.mockResolvedValue({ ok: false, status: 401 })
    await expect(login('wrong')).rejects.toThrow()
  })

  it('get attaches Authorization header', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: true, json: async () => [] })
    await get('/api/library')
    expect(global.fetch.mock.calls[0][1].headers['Authorization']).toBe('Bearer mytoken')
  })

  it('post sends JSON body', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: true, status: 204 })
    await post('/api/liked', { videoIds: ['x'] })
    expect(JSON.parse(global.fetch.mock.calls[0][1].body).videoIds).toEqual(['x'])
  })

  it('patch clears token and throws on 401', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: false, status: 401 })
    await expect(patch('/api/playlists/PL1', { title: 'x' })).rejects.toThrow('Unauthorized')
    expect(sessionStorage.getItem('token')).toBeNull()
  })

  it('del clears token and throws on 401', async () => {
    sessionStorage.setItem('token', 'mytoken')
    global.fetch.mockResolvedValue({ ok: false, status: 401 })
    await expect(del('/api/playlists/PL1')).rejects.toThrow('Unauthorized')
    expect(sessionStorage.getItem('token')).toBeNull()
  })
})
