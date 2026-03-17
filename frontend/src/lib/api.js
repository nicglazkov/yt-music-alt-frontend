export const getToken = () => sessionStorage.getItem('token')

const authHeaders = () => {
  const t = getToken()
  return t ? { Authorization: `Bearer ${t}` } : {}
}

export async function login(password) {
  const resp = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
  if (!resp.ok) throw new Error('Invalid password')
  const { token } = await resp.json()
  sessionStorage.setItem('token', token)
  return token
}

export async function get(path) {
  const resp = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
  })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.json()
}

export async function post(path, body) {
  const resp = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.status === 204 ? null : resp.json()
}

export async function patch(path, body) {
  const resp = await fetch(path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return resp.status === 204 ? null : resp.json()
}

export async function del(path) {
  const resp = await fetch(path, { method: 'DELETE', headers: authHeaders() })
  if (resp.status === 401) { sessionStorage.removeItem('token'); throw new Error('Unauthorized') }
  if (!resp.ok) throw new Error(`Request failed: ${resp.status}`)
  return null
}
