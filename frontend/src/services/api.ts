const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

type ApiRequestOptions = Omit<RequestInit, 'body'> & {
  body?: unknown
}

export async function apiFetch<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error(
      'API_BASE_URL is not configured. Check your frontend environment variables.',
    )
  }

  const headers = new Headers(options.headers)

  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(
    `${API_BASE_URL.replace(/\/+$/, '')}/${path.replace(/^\/+/, '')}`,
    {
      ...options,
      headers,
      body:
        options.body === undefined
          ? undefined
          : JSON.stringify(options.body),
    },
  )

  if (!response.ok) {
    const errorMessage = await response.text()

    throw new Error(
      errorMessage || `API request failed with status ${response.status}`,
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
