<script setup lang="ts">
import { useRouter } from 'vue-router'
import { telegramReady } from '../lib/telegram'
import bgImageUrl from '../assets/tg-app-bg.png'
import eventLogoUrl from '../assets/logo.svg'

const router = useRouter()

telegramReady()

function goRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="page landing-page">
    <img class="landing-bg-image" :src="bgImageUrl" alt="" aria-hidden="true" />
    <div class="landing-top-logo-wrap">
      <img class="landing-top-logo" :src="eventLogoUrl" alt="FCL 26" />
    </div>
    <div class="hero" />

    <div class="bottom-cta">
      <button class="primary-button landing-register-button" type="button" @click="goRegister">
        Зарегистрироваться
      </button>
    </div>
  </div>
</template>

