import { getTelegramInitData } from './telegram'

export type Discipline = 'CS2' | 'DOTA2' | 'FC26'
export type RegistrationMode = 'team' | 'individual'

export type DraftPayload = {
  discipline: Discipline | null
  mode: RegistrationMode | null
  data: Record<string, unknown>
}

async function apiFetch(path: string, init: RequestInit) {
  const initData = getTelegramInitData()
  const headers = new Headers(init.headers || {})
  headers.set('Content-Type', 'application/json')
  if (initData) headers.set('X-Telegram-Init-Data', initData)

  const res = await fetch(`/api${path}`, { ...init, headers })
  if (!res.ok) {
    const txt = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${txt}`)
  }
  return res
}

export async function saveDraft(draft: DraftPayload) {
  await apiFetch('/draft', { method: 'PUT', body: JSON.stringify(draft) })
}

export async function loadDraft(): Promise<DraftPayload | null> {
  const res = await apiFetch('/draft', { method: 'GET' })
  const json = (await res.json()) as { draft: DraftPayload | null }
  return json.draft
}

export async function submitRegistration(draft: DraftPayload) {
  await apiFetch('/submit', { method: 'POST', body: JSON.stringify(draft) })
}

