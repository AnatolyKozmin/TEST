import { getTelegramInitData } from './telegram'

export type Discipline = 'CS2' | 'DOTA2' | 'FC26'
export type RegistrationMode = 'team' | 'individual'

export type DraftPayload = {
  discipline: Discipline | null
  mode: RegistrationMode | null
  data: Record<string, unknown>
}

export type AdminRegistration = {
  id: number
  tg_user_id: number
  tg_username: string | null
  tg_first_name: string | null
  tg_last_name: string | null
  discipline: string
  mode: string
  payload: Record<string, unknown>
  submitted_at: string | null
}

export type AdminRegistrationsResponse = {
  total: number
  limit: number
  offset: number
  items: AdminRegistration[]
}

export class MissingTelegramInitDataError extends Error {
  constructor() {
    super('Missing Telegram initData')
    this.name = 'MissingTelegramInitDataError'
  }
}

async function apiFetch(path: string, init: RequestInit) {
  const initData = getTelegramInitData()
  if (!initData) throw new MissingTelegramInitDataError()

  const headers = new Headers(init.headers || {})
  headers.set('Content-Type', 'application/json')
  headers.set('X-Telegram-Init-Data', initData)

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

export async function loadAdminRegistrations(params: {
  discipline?: string
  mode?: string
  q?: string
  limit?: number
  offset?: number
}): Promise<AdminRegistrationsResponse> {
  const query = new URLSearchParams()
  if (params.discipline) query.set('discipline', params.discipline)
  if (params.mode) query.set('mode', params.mode)
  if (params.q) query.set('q', params.q)
  query.set('limit', String(params.limit ?? 30))
  query.set('offset', String(params.offset ?? 0))

  const res = await fetch(`/api/admin/registrations?${query.toString()}`)
  if (!res.ok) {
    const txt = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${txt}`)
  }
  return (await res.json()) as AdminRegistrationsResponse
}

