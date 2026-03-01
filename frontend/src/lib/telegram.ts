declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready?: () => void
        expand?: () => void
        initData?: string
        initDataUnsafe?: {
          user?: {
            id: number
            username?: string
            first_name?: string
            last_name?: string
          }
        }
      }
    }
  }
}

function getParamFromUrlOrHash(paramName: string): string | null {
  const url = new URL(window.location.href)

  const fromQuery = url.searchParams.get(paramName)
  if (fromQuery && fromQuery.length > 0) return fromQuery

  const hash = window.location.hash.startsWith('#') ? window.location.hash.slice(1) : window.location.hash
  if (hash) {
    const hashParams = new URLSearchParams(hash)
    const fromHash = hashParams.get(paramName)
    if (fromHash && fromHash.length > 0) return fromHash
  }

  return null
}

export function getTelegramInitData(): string | null {
  const fromTelegramSdk = window.Telegram?.WebApp?.initData
  if (fromTelegramSdk && fromTelegramSdk.length > 0) return fromTelegramSdk

  // Debug/manual fallback for local tests.
  const fromInitDataParam = getParamFromUrlOrHash('initData')
  if (fromInitDataParam && fromInitDataParam.length > 0) return fromInitDataParam

  // Telegram fallback: tgWebAppData may arrive in URL hash.
  const fromTgWebAppData = getParamFromUrlOrHash('tgWebAppData')
  if (fromTgWebAppData && fromTgWebAppData.length > 0) return fromTgWebAppData

  return null
}

export function getTelegramUserId(): number | null {
  const id = window.Telegram?.WebApp?.initDataUnsafe?.user?.id
  return typeof id === 'number' ? id : null
}

export function telegramReady() {
  window.Telegram?.WebApp?.ready?.()
  window.Telegram?.WebApp?.expand?.()
}

