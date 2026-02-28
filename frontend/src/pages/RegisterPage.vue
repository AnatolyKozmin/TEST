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
  'Факультет ИТ и анализа больших данных',
  'Факультет международных экономических отношений',
  'Факультет экономики и бизнеса',
  'Факультет финансов',
  'Факультет налогов, аудита и бизнес-анализа',
  'Юридический факультет',
  'Другое',
]

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
  if (isTeamAllowed.value && !draft.mode) draft.mode = 'team'
}

function setDiscipline(v: Discipline) {
  draft.discipline = v
  ensureDefaults()
}

function setMode(v: RegistrationMode) {
  draft.mode = v
}

const facultyIsOther = computed(() => (draft.data['faculty'] as string | undefined) === 'Другое')

const statusText = computed(() => {
  if (savingState.value === 'saving') return 'Сохраняем черновик…'
  if (savingState.value === 'saved') return 'Черновик сохранён'
  if (savingState.value === 'error') return lastError.value ?? 'Ошибка сохранения'
  return ''
})

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
    ensureDefaults()
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
        <select
          :value="draft.discipline ?? ''"
          @change="setDiscipline(($event.target as HTMLSelectElement).value as Discipline)"
        >
          <option value="" disabled>Выберите дисциплину</option>
          <option value="CS2">CS2</option>
          <option value="DOTA2">Dota 2</option>
          <option value="FC26">FC26</option>
        </select>
      </div>

      <div class="field" v-if="draft.discipline">
        <div class="label">Тип регистрации</div>
        <select :value="resolvedMode ?? ''" @change="setMode(($event.target as HTMLSelectElement).value as RegistrationMode)">
          <option value="team" :disabled="!isTeamAllowed">Командная</option>
          <option value="individual">Индивидуальная</option>
        </select>
        <div class="hint" v-if="draft.discipline === 'FC26'">Для FC26 по умолчанию индивидуальная регистрация.</div>
      </div>
    </div>

    <div class="card" v-if="resolvedMode === 'team'">
      <div class="field">
        <div class="label">Участники команды</div>
        <textarea
          :value="(draft.data['team_members'] as string | undefined) ?? ''"
          placeholder="ФИО и ники всех участников (по строке на человека)"
          @input="draft.data['team_members'] = ($event.target as HTMLTextAreaElement).value"
        />
      </div>

      <div class="row">
        <div class="field">
          <div class="label">ФИО капитана</div>
          <input
            :value="(draft.data['captain_full_name'] as string | undefined) ?? ''"
            @input="draft.data['captain_full_name'] = ($event.target as HTMLInputElement).value"
          />
        </div>
        <div class="field">
          <div class="label">Телефон капитана</div>
          <input
            :value="(draft.data['captain_phone'] as string | undefined) ?? ''"
            inputmode="tel"
            placeholder="+7…"
            @input="draft.data['captain_phone'] = ($event.target as HTMLInputElement).value"
          />
        </div>
      </div>

      <div class="row">
        <div class="field">
          <div class="label">Ник в Telegram</div>
          <input
            :value="(draft.data['captain_tg_nick'] as string | undefined) ?? ''"
            placeholder="@username"
            @input="draft.data['captain_tg_nick'] = ($event.target as HTMLInputElement).value"
          />
        </div>
        <div class="field">
          <div class="label">Ник в VK</div>
          <input
            :value="(draft.data['captain_vk_nick'] as string | undefined) ?? ''"
            placeholder="vk.com/… или ник"
            @input="draft.data['captain_vk_nick'] = ($event.target as HTMLInputElement).value"
          />
        </div>
      </div>

      <div class="field">
        <div class="label">Факультет</div>
        <select
          :value="(draft.data['faculty'] as string | undefined) ?? ''"
          @change="draft.data['faculty'] = ($event.target as HTMLSelectElement).value"
        >
          <option value="" disabled>Выберите факультет</option>
          <option v-for="f in faculties" :key="f" :value="f">{{ f }}</option>
        </select>
      </div>

      <div class="field" v-if="facultyIsOther">
        <div class="label">Ваш вариант факультета</div>
        <input
          :value="(draft.data['faculty_other'] as string | undefined) ?? ''"
          @input="draft.data['faculty_other'] = ($event.target as HTMLInputElement).value"
        />
      </div>

      <div class="card" style="margin: 12px 0 0" v-if="draft.discipline === 'CS2'">
        <div class="row">
          <div class="field">
            <div class="label">Steam (ссылка)</div>
            <input
              :value="(draft.data['steam_url'] as string | undefined) ?? ''"
              placeholder="https://steamcommunity.com/…"
              @input="draft.data['steam_url'] = ($event.target as HTMLInputElement).value"
            />
          </div>
          <div class="field">
            <div class="label">Faceit (ссылка)</div>
            <input
              :value="(draft.data['faceit_url'] as string | undefined) ?? ''"
              placeholder="https://www.faceit.com/…"
              @input="draft.data['faceit_url'] = ($event.target as HTMLInputElement).value"
            />
          </div>
        </div>
      </div>

      <div class="card" style="margin: 12px 0 0" v-if="draft.discipline === 'DOTA2'">
        <div class="field">
          <div class="label">Steam (ссылка)</div>
          <input
            :value="(draft.data['steam_url'] as string | undefined) ?? ''"
            placeholder="https://steamcommunity.com/…"
            @input="draft.data['steam_url'] = ($event.target as HTMLInputElement).value"
          />
        </div>
      </div>
    </div>

    <div class="card" v-if="resolvedMode === 'individual'">
      <div class="row">
        <div class="field">
          <div class="label">ФИО</div>
          <input
            :value="(draft.data['full_name'] as string | undefined) ?? ''"
            @input="draft.data['full_name'] = ($event.target as HTMLInputElement).value"
          />
        </div>
        <div class="field">
          <div class="label">Телефон</div>
          <input
            :value="(draft.data['phone'] as string | undefined) ?? ''"
            inputmode="tel"
            placeholder="+7…"
            @input="draft.data['phone'] = ($event.target as HTMLInputElement).value"
          />
        </div>
      </div>

      <div class="row">
        <div class="field">
          <div class="label">Ник в Telegram</div>
          <input
            :value="(draft.data['tg_nick'] as string | undefined) ?? ''"
            placeholder="@username"
            @input="draft.data['tg_nick'] = ($event.target as HTMLInputElement).value"
          />
        </div>
        <div class="field">
          <div class="label">Ник в VK</div>
          <input
            :value="(draft.data['vk_nick'] as string | undefined) ?? ''"
            placeholder="vk.com/… или ник"
            @input="draft.data['vk_nick'] = ($event.target as HTMLInputElement).value"
          />
        </div>
      </div>

      <div class="field">
        <div class="label">Учебное заведение</div>
        <input
          :value="(draft.data['institution'] as string | undefined) ?? ''"
          placeholder="Например: Финансовый университет"
          @input="draft.data['institution'] = ($event.target as HTMLInputElement).value"
        />
      </div>
    </div>

    <div class="bottom-cta" v-if="draft.discipline && resolvedMode">
      <div class="status" v-if="statusText">{{ statusText }}</div>
      <button class="primary-button" type="button" @click="submit">Отправить заявку</button>
    </div>
  </div>
</template>

