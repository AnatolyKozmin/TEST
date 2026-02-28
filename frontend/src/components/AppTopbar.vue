<script setup lang="ts">
defineProps<{
  title?: string
  showBack?: boolean
}>()

const emit = defineEmits<{
  (e: 'back'): void
  (e: 'menu'): void
}>()
</script>

<template>
  <div class="topbar">
    <button v-if="showBack" class="icon-button" type="button" @click="emit('back')">←</button>
    <div v-else class="brand">
      <span class="brand-badge" aria-hidden="true" />
      <span>FCL</span>
    </div>

    <div v-if="title" style="font-weight: 700; letter-spacing: 0.04em">{{ title }}</div>
    <div v-else />

    <button class="icon-button" type="button" @click="emit('menu')" aria-label="menu">
      ☰
    </button>
  </div>
</template>

