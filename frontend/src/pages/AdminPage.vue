<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { type AdminRegistration, loadAdminRegistrations } from '../lib/api'

const discipline = ref('')
const mode = ref('')
const search = ref('')
const page = ref(1)
const pageSize = 30

const loading = ref(false)
const error = ref<string | null>(null)
const total = ref(0)
const items = ref<AdminRegistration[]>([])
const selectedId = ref<number | null>(null)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const selectedItem = computed(() => items.value.find((i) => i.id === selectedId.value) ?? null)

function formatDate(value: string | null) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('ru-RU')
}

async function loadPage() {
  loading.value = true
  error.value = null
  try {
    const data = await loadAdminRegistrations({
      discipline: discipline.value || undefined,
      mode: mode.value || undefined,
      q: search.value.trim() || undefined,
      limit: pageSize,
      offset: (page.value - 1) * pageSize,
    })
    total.value = data.total
    items.value = data.items
    if (items.value.length === 0) {
      selectedId.value = null
    } else if (!items.value.some((i) => i.id === selectedId.value)) {
      selectedId.value = items.value[0]?.id ?? null
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось загрузить заявки'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  void loadPage()
}

function prevPage() {
  if (page.value <= 1) return
  page.value -= 1
  void loadPage()
}

function nextPage() {
  if (page.value >= totalPages.value) return
  page.value += 1
  void loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>

<template>
  <div class="admin-page">
    <div class="admin-header">
      <h1>Админка заявок</h1>
      <div class="admin-total">Всего: {{ total }}</div>
    </div>

    <div class="admin-filters">
      <select v-model="discipline">
        <option value="">Все дисциплины</option>
        <option value="CS2">CS2</option>
        <option value="DOTA2">Dota 2</option>
        <option value="FC26">FC26</option>
      </select>

      <select v-model="mode">
        <option value="">Все типы</option>
        <option value="team">Командная</option>
        <option value="individual">Индивидуальная</option>
      </select>

      <input
        v-model="search"
        type="text"
        placeholder="Поиск: username, id, данные заявки"
        @keyup.enter="applyFilters"
      />
      <button type="button" @click="applyFilters">Применить</button>
    </div>

    <div class="admin-state" v-if="loading">Загрузка...</div>
    <div class="admin-state admin-state--error" v-else-if="error">{{ error }}</div>

    <div class="admin-layout" v-else>
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Пользователь</th>
              <th>Дисциплина</th>
              <th>Тип</th>
              <th>Дата</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in items"
              :key="row.id"
              :class="{ active: selectedId === row.id }"
              @click="selectedId = row.id"
            >
              <td>{{ row.id }}</td>
              <td>@{{ row.tg_username || '-' }} ({{ row.tg_user_id }})</td>
              <td>{{ row.discipline }}</td>
              <td>{{ row.mode }}</td>
              <td>{{ formatDate(row.submitted_at) }}</td>
            </tr>
          </tbody>
        </table>

        <div class="admin-pagination">
          <button type="button" @click="prevPage" :disabled="page <= 1">Назад</button>
          <span>Страница {{ page }} / {{ totalPages }}</span>
          <button type="button" @click="nextPage" :disabled="page >= totalPages">Вперед</button>
        </div>
      </div>

      <div class="admin-details">
        <h2>Детали заявки</h2>
        <div v-if="!selectedItem">Выберите заявку из таблицы.</div>
        <template v-else>
          <div><b>ID:</b> {{ selectedItem.id }}</div>
          <div><b>TG:</b> @{{ selectedItem.tg_username || '-' }} ({{ selectedItem.tg_user_id }})</div>
          <div><b>Дисциплина:</b> {{ selectedItem.discipline }}</div>
          <div><b>Тип:</b> {{ selectedItem.mode }}</div>
          <pre>{{ JSON.stringify(selectedItem.payload, null, 2) }}</pre>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #0f0121;
  color: #fff;
  padding: 24px;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.admin-header h1 {
  margin: 0;
  font-size: 28px;
}

.admin-filters {
  display: grid;
  grid-template-columns: 180px 180px 1fr 140px;
  gap: 10px;
  margin-bottom: 16px;
}

.admin-filters input,
.admin-filters select,
.admin-filters button,
.admin-pagination button {
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  padding: 0 12px;
}

.admin-layout {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 14px;
}

.admin-table-wrap,
.admin-details {
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.04);
  padding: 12px;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  text-align: left;
  padding: 9px 7px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 13px;
}

.admin-table tbody tr {
  cursor: pointer;
}

.admin-table tbody tr.active {
  background: rgba(151, 125, 255, 0.28);
}

.admin-pagination {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.admin-details pre {
  margin-top: 10px;
  max-height: 60vh;
  overflow: auto;
  background: #090114;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 10px;
  font-size: 12px;
}

.admin-state {
  margin-top: 8px;
  opacity: 0.9;
}

.admin-state--error {
  color: #ff8f8f;
}

@media (max-width: 900px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .admin-filters {
    grid-template-columns: 1fr;
  }
}
</style>
