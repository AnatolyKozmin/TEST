<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppTopbar from '../components/AppTopbar.vue'
import bgImageUrl from '../assets/tg-app-bg.png'
import {
  type Discipline,
  type DraftPayload,
  type RegistrationMode,
  loadDraft,
  saveDraft,
  submitRegistration,
} from '../lib/api'
import { telegramReady } from '../lib/telegram'

const router = useRouter()
const savingState = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const lastError = ref<string | null>(null)

const faculties = [
  'НАБ',
  'ВШУ',
  'ФЭБ',
  'МЭО',
  'СНиМК',
  'ИТиАБД',
  'Юрфак',
  'Финфак',
]

type TeamRole = 'main' | 'reserve'
type TeamPlayer = {
  role: TeamRole
  full_name: string
  game_nick: string
  steam_url: string
  faceit_url: string
  faculty: string
  telegram: string
}

const draft = reactive<DraftPayload>({
  discipline: null,
  mode: null,
  data: {},
})

const isTeamAllowed = computed(() => draft.discipline === 'CS2' || draft.discipline === 'DOTA2')
const resolvedMode = computed<RegistrationMode | null>(() => {
  if (draft.discipline === 'FC26') return 'individual'
  if (isTeamAllowed.value) return draft.mode ?? 'team'
  return draft.mode
})

function ensureDefaults() {
  if (draft.discipline === 'FC26') draft.mode = 'individual'
  if (isTeamAllowed.value && !draft.mode) {
    draft.mode = 'team'
  }
  if (isTeamAllowed.value && draft.mode === 'team') {
    ensureTeamPlayers()
  }
}

function setDiscipline(v: Discipline) {
  draft.discipline = v
  ensureDefaults()
}

function setMode(v: RegistrationMode) {
  draft.mode = v
  if (v === 'team') ensureTeamPlayers()
}

const teamPlayers = computed<TeamPlayer[]>(() => {
  ensureTeamPlayers()
  return (draft.data['team_players'] as TeamPlayer[]) ?? []
})

function ensureTeamPlayers() {
  const existingRaw = draft.data['team_players']
  if (Array.isArray(existingRaw) && existingRaw.length === 8) {
    return
  }

  const existing = Array.isArray(existingRaw) ? (existingRaw as Partial<TeamPlayer>[]) : []
  const normalized: TeamPlayer[] = []
  for (let i = 0; i < 8; i++) {
    const role: TeamRole = i < 5 ? 'main' : 'reserve'
    const old = existing[i] ?? {}
    normalized.push({
      role,
      full_name: String(old.full_name ?? ''),
      game_nick: String(old.game_nick ?? ''),
      steam_url: String(old.steam_url ?? ''),
      faceit_url: String(old.faceit_url ?? ''),
      faculty: String(old.faculty ?? ''),
      telegram: String(old.telegram ?? ''),
    })
  }
  draft.data['team_players'] = normalized
}

const statusText = computed(() => {
  if (savingState.value === 'saving') return 'Сохраняем черновик…'
  if (savingState.value === 'saved') return 'Черновик сохранён'
  if (savingState.value === 'error') return lastError.value ?? 'Ошибка сохранения'
  return ''
})

function isFilled(v: unknown): boolean {
  return typeof v === 'string' ? v.trim().length > 0 : false
}

function validateBeforeSubmit(): string | null {
  if (!draft.discipline || !resolvedMode.value) return 'Выберите дисциплину и тип регистрации'

  if (resolvedMode.value === 'team') {
    const players = teamPlayers.value
    for (let i = 0; i < players.length; i++) {
      const p = players[i]
      if (!p) continue
      const isMain = i < 5
      if (!isMain) continue

      if (!isFilled(p.full_name)) return `Игрок ${i + 1}: заполните ФИО`
      if (!isFilled(p.game_nick)) return `Игрок ${i + 1}: заполните никнейм в игре`
      if ((draft.discipline === 'CS2' || draft.discipline === 'DOTA2') && !isFilled(p.steam_url)) {
        return `Игрок ${i + 1}: заполните ссылку Steam`
      }
      if (draft.discipline === 'CS2' && !isFilled(p.faceit_url)) {
        return `Игрок ${i + 1}: заполните ссылку Faceit`
      }
      if (!isFilled(p.faculty)) return `Игрок ${i + 1}: выберите факультет`
      if (!isFilled(p.telegram)) return `Игрок ${i + 1}: заполните Telegram`
    }
  } else {
    if (!isFilled(draft.data['full_name'])) return 'Заполните ФИО'
    if (!isFilled(draft.data['game_nick'])) return 'Заполните никнейм в игре'
    if ((draft.discipline === 'CS2' || draft.discipline === 'DOTA2') && !isFilled(draft.data['steam_url'])) {
      return 'Заполните ссылку Steam'
    }
    if (draft.discipline === 'CS2' && !isFilled(draft.data['faceit_url'])) return 'Заполните ссылку Faceit'
    if (!isFilled(draft.data['faculty'])) return 'Выберите факультет'
    if (!isFilled(draft.data['telegram'])) return 'Заполните Telegram'
  }

  return null
}

telegramReady()

onMounted(async () => {
  try {
    const loaded = await loadDraft()
    if (loaded) {
      draft.discipline = loaded.discipline
      draft.mode = loaded.mode
      draft.data = loaded.data || {}
      ensureDefaults()
      savingState.value = 'saved'
    }
  } catch {
    // ignore
  }
})

let saveTimer: number | null = null
watch(
  () => ({ discipline: draft.discipline, mode: draft.mode, data: draft.data }),
  () => {
    if (saveTimer) window.clearTimeout(saveTimer)
    saveTimer = window.setTimeout(async () => {
      savingState.value = 'saving'
      lastError.value = null
      try {
        await saveDraft({ discipline: draft.discipline, mode: resolvedMode.value, data: draft.data })
        savingState.value = 'saved'
      } catch (e) {
        savingState.value = 'error'
        lastError.value = e instanceof Error ? e.message : 'Ошибка сохранения'
      }
    }, 600)
  },
  { deep: true },
)

async function submit() {
  const validationError = validateBeforeSubmit()
  if (validationError) {
    savingState.value = 'error'
    lastError.value = validationError
    return
  }

  savingState.value = 'saving'
  lastError.value = null
  try {
    await submitRegistration({ discipline: draft.discipline, mode: resolvedMode.value, data: draft.data })
    savingState.value = 'saved'
    router.push('/')
  } catch (e) {
    savingState.value = 'error'
    lastError.value = e instanceof Error ? e.message : 'Ошибка отправки'
  }
}
</script>

<template>
  <div class="page register-page">
    <img class="landing-bg-image" :src="bgImageUrl" alt="" aria-hidden="true" />
    <AppTopbar title="Регистрация" showBack @back="router.back()" />

    <div class="card">
      <div class="field">
        <div class="label">Дисциплина</div>
        <select v-model="draft.discipline" @change="setDiscipline(draft.discipline as Discipline)">
          <option value="" disabled>Выберите дисциплину</option>
          <option value="CS2">CS2</option>
          <option value="DOTA2">Dota 2</option>
          <option value="FC26">FC26</option>
        </select>
      </div>

      <div class="field" v-if="draft.discipline">
        <div class="label">Тип регистрации</div>
        <select v-model="draft.mode" @change="setMode((draft.mode ?? 'individual') as RegistrationMode)">
          <option value="team" :disabled="!isTeamAllowed">Командная</option>
          <option value="individual">Индивидуальная</option>
        </select>
        <div class="hint" v-if="draft.discipline === 'FC26'">Для FC26 по умолчанию индивидуальная регистрация.</div>
      </div>
    </div>

    <div class="card" v-if="resolvedMode === 'team'">
      <div class="hint" style="margin-bottom: 14px">
        Состав команды: 5 основных игроков + 3 запасных. Для запасных поля необязательные.
      </div>

      <div class="player-block" v-for="(player, idx) in teamPlayers" :key="idx">
        <div class="player-title">
          Игрок {{ idx + 1 }}
          <span class="player-role">{{ player.role === 'main' ? 'Основной' : 'Запасной' }}</span>
        </div>

        <div class="field">
          <div class="label">ФИО</div>
          <input v-model="player.full_name" :required="idx < 5" />
        </div>

        <div class="field">
          <div class="label">Никнейм в игре</div>
          <input v-model="player.game_nick" :required="idx < 5" />
        </div>

        <div class="field" v-if="draft.discipline === 'CS2' || draft.discipline === 'DOTA2'">
          <div class="label">Ссылка Steam</div>
          <input v-model="player.steam_url" placeholder="https://steamcommunity.com/profiles/..." :required="idx < 5" />
        </div>

        <div class="field" v-if="draft.discipline === 'CS2'">
          <div class="label">Ссылка Faceit</div>
          <input v-model="player.faceit_url" placeholder="https://www.faceit.com/ru/players/..." :required="idx < 5" />
        </div>

        <div class="field">
          <div class="label">Факультет</div>
          <select v-model="player.faculty" :required="idx < 5">
            <option value="" disabled>Выберите факультет</option>
            <option v-for="f in faculties" :key="f" :value="f">{{ f }}</option>
          </select>
        </div>

        <div class="field">
          <div class="label">Telegram</div>
          <input v-model="player.telegram" placeholder="@username" :required="idx < 5" />
        </div>
      </div>
    </div>

    <div class="card" v-if="resolvedMode === 'individual'">
      <div class="field">
        <div class="label">ФИО</div>
        <input
          :value="(draft.data['full_name'] as string | undefined) ?? ''"
          required
          @input="draft.data['full_name'] = ($event.target as HTMLInputElement).value"
        />
      </div>

      <div class="field">
        <div class="label">Никнейм в игре</div>
        <input
          :value="(draft.data['game_nick'] as string | undefined) ?? ''"
          required
          @input="draft.data['game_nick'] = ($event.target as HTMLInputElement).value"
        />
      </div>

      <div class="field" v-if="draft.discipline === 'CS2' || draft.discipline === 'DOTA2'">
        <div class="label">Ссылка Steam</div>
        <input
          :value="(draft.data['steam_url'] as string | undefined) ?? ''"
          placeholder="https://steamcommunity.com/profiles/..."
          required
          @input="draft.data['steam_url'] = ($event.target as HTMLInputElement).value"
        />
      </div>

      <div class="field" v-if="draft.discipline === 'CS2'">
        <div class="label">Ссылка Faceit</div>
        <input
          :value="(draft.data['faceit_url'] as string | undefined) ?? ''"
          placeholder="https://www.faceit.com/ru/players/..."
          required
          @input="draft.data['faceit_url'] = ($event.target as HTMLInputElement).value"
        />
      </div>

      <div class="field">
        <div class="label">Факультет</div>
        <select
          :value="(draft.data['faculty'] as string | undefined) ?? ''"
          required
          @change="draft.data['faculty'] = ($event.target as HTMLSelectElement).value"
        >
          <option value="" disabled>Выберите факультет</option>
          <option v-for="f in faculties" :key="f" :value="f">{{ f }}</option>
        </select>
      </div>

      <div class="field">
        <div class="label">Telegram</div>
        <input
          :value="(draft.data['telegram'] as string | undefined) ?? ''"
          placeholder="@username"
          required
          @input="draft.data['telegram'] = ($event.target as HTMLInputElement).value"
        />
      </div>
    </div>

    <div class="bottom-cta" v-if="draft.discipline && resolvedMode">
      <div class="status" v-if="statusText">{{ statusText }}</div>
      <button class="primary-button" type="button" @click="submit">Отправить заявку</button>
    </div>
  </div>
</template>

