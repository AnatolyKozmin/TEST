<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppTopbar from '../components/AppTopbar.vue'
import { telegramReady } from '../lib/telegram'
import eventLogoUrl from '../assets/logo.svg'

const router = useRouter()

telegramReady()

function goRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="page">
    <AppTopbar />

    <div class="hero">
      <div class="fcl-mark" aria-label="FCL Financial Cybersport League">
        <div class="fcl-mark-word">
          <div class="fcl-layer fcl-stroke">FCL</div>
          <div class="fcl-layer fcl-fill">FCL</div>
        </div>
        <div class="fcl-caption">FINANCIAL CYBERSPORT LEAGUE</div>
      </div>
    </div>

    <div class="bottom-cta">
      <div class="event-logo">
        <img class="event-logo-img" :src="eventLogoUrl" alt="FCL logo" />
      </div>

      <button class="primary-button" type="button" @click="goRegister">Регистрация</button>
    </div>
  </div>
</template>

