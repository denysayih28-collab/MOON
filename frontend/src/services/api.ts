type ApiRequestOptions = Omit<RequestInit, 'body'> & {
  body?: unknown
}

async function request<T>(
  basePath: string,
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers)

  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(
    `${basePath}/${path.replace(/^\/+/, '')}`,
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

/**
 * Backend principal : accès, profil, indicateurs,
 * mesures et alertes générales.
 */
export function mainApiFetch<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  return request<T>('/main-api', path, options)
}

/**
 * Backend Simulation : scénarios, simulations,
 * règles et alertes issues du moteur de simulation.
 */
export function simulationApiFetch<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  return request<T>('/simulation-api', path, options)
}

/**
 * Alias temporaire pour préserver les éventuels anciens appels.
 * Les nouveaux appels devront choisir explicitement leur backend.
 */
export const apiFetch = mainApiFetch
