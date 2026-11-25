
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let csrfToken = null


// GET A CSRF TOKEN FROM THE BACKEND
async function getCsrfToken() {
  const response = await fetch(`${API_URL}/auth/csrf`, {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error('Unable to initialize security token.')
  }

  const data = await response.json()

  if (!data.csrf_token) {
    throw new Error('Security token was not received.')
  }

  csrfToken = data.csrf_token

  return csrfToken
}


// SHARED API REQUEST FUNCTION
export async function apiFetch(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase()

  const unsafeMethods = ['POST', 'PUT', 'PATCH', 'DELETE']
  const headers = new Headers(options.headers || {})

  // Automatically obtain a CSRF token for unsafe requests
  if (unsafeMethods.includes(method)) {
    if (!csrfToken) {
      await getCsrfToken()
    }

    headers.set('X-CSRF-Token', csrfToken)
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    method,
    headers,
    credentials: 'include',
  })

  // Update the token when the backend rotates it after login
  if (response.ok && path === '/auth/login') {
    const data = await response.clone().json()

    if (data.csrf_token) {
      csrfToken = data.csrf_token
    }
  }

  // Clear the in-memory token after logout
  if (response.ok && path === '/auth/logout') {
    csrfToken = null
  }

  return response
}

export { API_URL }
