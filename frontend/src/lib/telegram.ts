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

export function getTelegramInitData(): string | null {
  const fromTg = window.Telegram?.WebApp?.initData
  if (fromTg && fromTg.length > 0) return fromTg

  const url = new URL(window.location.href)
  const fromQuery = url.searchParams.get('initData')
  if (fromQuery && fromQuery.length > 0) return fromQuery

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

