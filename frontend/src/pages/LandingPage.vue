<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppTopbar from '../components/AppTopbar.vue'
import { telegramReady } from '../lib/telegram'
import bgImageUrl from '../assets/tg-app-bg.png'

const router = useRouter()

telegramReady()

function goRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="page landing-page">
    <img class="landing-bg-image" :src="bgImageUrl" alt="" aria-hidden="true" />
    <AppTopbar />

    <div class="hero" />

    <div class="bottom-cta">
      <button class="primary-button landing-register-button" type="button" @click="goRegister">
        Зарегистрироваться
      </button>
    </div>
  </div>
</template>

