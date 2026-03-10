<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import partnersStrip from '@/assets/partners-strip.svg'
import contactOleg from '@/assets/contact-oleg.png'
import contactPlaton from '@/assets/contact-platon.png'
import contactAlina from '@/assets/contact-alina.png'

const faqItems = [
  {
    short: 'Участие',
    question: 'Кто может участвовать в турнире?',
    answer:
      'Участвовать в турнире могут студенты Финансового университета и других ВУЗов Москвы.',
  },
  {
    short: 'Условия',
    question: 'Что нужно для участия?',
    answer:
      'Основное — это готовность проявить себя, капитанам заполнить заявку на участие команды.',
  },
  {
    short: 'Подтверждение',
    question: 'Нужно ли куда-то писать, чтобы подтвердить участие?',
    answer:
      'Нет, после обработки всех заявок представители турнира сами свяжутся с участниками и напишут, что делать дальше.',
  },
  {
    short: 'Финал',
    question: 'Как проходит Гранд-финал?',
    answer:
      'Гранд-финал турнира пройдет очно на киберарене с трансляцией и активностями для зрителей.',
  },
  {
    short: 'Награды',
    question: 'Какой призовой фонд турнира?',
    answer:
      'Все победители и призеры получат ценные награды от партнеров турнира.',
  },
  {
    short: 'Матчи',
    question: 'Где и когда будут проходить матчи?',
    answer:
      'Матчи по CS2 будут проходить на платформе FACEIT, по Dota 2 и FC26 — в последних клиентах игр. На онлайн-этапе командам ежедневно будут предлагаться временные слоты, которые они должны выбрать.',
  },
];

const contacts = [
  {
    name: 'Олег Никитин',
    role: 'Главный менеджер',
    email: 'olezheq@gmail.com',
    telegram: '@o1ezheq',
    photo: contactOleg,
  },
  {
    name: 'платон бандик',
    role: 'Руководитель организации',
    email: 'bandikplaton@gmail.com',
    telegram: '@platon_bpm',
    photo: contactPlaton,
  },
  {
    name: 'Алина дородова',
    role: 'Главный менеджер',
    email: 'alinadorodova14@gmail.com',
    telegram: '@alinalinaalinalinaa',
    photo: contactAlina,
  },
]

const openedFaqIndex = ref(null)
const mobileMenuOpen = ref(false)
const statsLayoutScaleEl = ref(null)
const statsMobileScale = ref(1)
const heroGalleryScaleEl = ref(null)
const heroGalleryScale = ref(1)
const scheduleScaleEl = ref(null)
const scheduleMobileScale = ref(1)
let revealObserver = null
let statsResizeObserver = null
let heroResizeObserver = null
let scheduleResizeObserver = null

const toggleFaq = (index) => {
  openedFaqIndex.value = openedFaqIndex.value === index ? null : index
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

watch(mobileMenuOpen, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
})

const updateStatsScale = () => {
  const el = statsLayoutScaleEl.value
  if (!el) return
  const width = el.clientWidth || 0
  const nextScale = width > 0 ? Math.min(1, width / 1128) : 1
  statsMobileScale.value = Number(nextScale.toFixed(4))
}

const updateHeroGalleryScale = () => {
  const el = heroGalleryScaleEl.value
  if (!el) return
  const width = el.clientWidth || 0
  const nextScale = width > 0 ? Math.min(1, (width / 1680) * 1.0) : 1
  heroGalleryScale.value = Number(nextScale.toFixed(4))
}

const updateScheduleScale = () => {
  const el = scheduleScaleEl.value
  if (!el) return
  const width = el.clientWidth || 0
  const nextScale = width > 0 ? Math.min(1, width / 980) : 1
  scheduleMobileScale.value = Number(nextScale.toFixed(4))
}

onMounted(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const targets = document.querySelectorAll(
    '.hero__text, .hero__gallery, .section'
  )

  if (reduceMotion) {
    targets.forEach((el) => el.classList.add('is-visible'))
    return
  }

  targets.forEach((el, index) => {
    el.classList.add('reveal-on-scroll')
    el.style.setProperty('--reveal-delay', `${Math.min(index * 45, 220)}ms`)
  })

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          revealObserver?.unobserve(entry.target)
        }
      })
    },
    {
      root: null,
      threshold: 0.14,
      rootMargin: '0px 0px -8% 0px',
    }
  )

  targets.forEach((el) => revealObserver?.observe(el))

  updateStatsScale()
  updateHeroGalleryScale()
  updateScheduleScale()
  window.addEventListener('resize', updateStatsScale)
  window.addEventListener('resize', updateHeroGalleryScale)
  window.addEventListener('resize', updateScheduleScale)
  if ('ResizeObserver' in window) {
    statsResizeObserver = new ResizeObserver(() => updateStatsScale())
    if (statsLayoutScaleEl.value) {
      statsResizeObserver.observe(statsLayoutScaleEl.value)
    }
    heroResizeObserver = new ResizeObserver(() => updateHeroGalleryScale())
    if (heroGalleryScaleEl.value) {
      heroResizeObserver.observe(heroGalleryScaleEl.value)
    }
    scheduleResizeObserver = new ResizeObserver(() => updateScheduleScale())
    if (scheduleScaleEl.value) {
      scheduleResizeObserver.observe(scheduleScaleEl.value)
    }
  }
})

onBeforeUnmount(() => {
  revealObserver?.disconnect()
  statsResizeObserver?.disconnect?.()
  heroResizeObserver?.disconnect?.()
  scheduleResizeObserver?.disconnect?.()
  window.removeEventListener('resize', updateStatsScale)
  window.removeEventListener('resize', updateHeroGalleryScale)
  window.removeEventListener('resize', updateScheduleScale)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="fcl-page">
    <!-- HEADER -->
    <header class="fcl-header">
      <img src="@/assets/fcl-logo-header.png" alt="FCL Logo" class="fcl-header__logo" />
      <button
        class="fcl-header__menu-toggle"
        :class="{ 'fcl-header__menu-toggle--open': mobileMenuOpen }"
        type="button"
        aria-label="Открыть меню"
        @click="toggleMobileMenu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
      <nav class="fcl-nav" :class="{ 'fcl-nav--open': mobileMenuOpen }">
        <a href="#about" @click="closeMobileMenu">О проекте</a>
        <a href="#partners" @click="closeMobileMenu">партнёры</a>
        <a href="#contacts" @click="closeMobileMenu">контакты</a>
      </nav>
      <div class="fcl-header__social">
        <a href="https://t.me/fcl_26" target="_blank" rel="noreferrer">
          <img src="@/assets/icon-tg.png" alt="Telegram" class="fcl-header__icon" />
        </a>
        <a href="https://vk.com/fin_cyber_league" target="_blank" rel="noreferrer">
          <img src="@/assets/icon-vk.png" alt="VK" class="fcl-header__icon" />
        </a>
    </div>
  </header>

  <main>
      <!-- HERO SECTION -->
      <section class="hero" id="about">
        <!-- Фоновые элементы -->
        <div class="hero__bg">
          <img src="@/assets/hero-bg.png" alt="" class="hero__bg-image" />
        </div>
        <div class="hero__character">
          <img src="@/assets/hero-character.png" alt="" class="hero__character-image" />
        </div>

        <div class="hero__container">
          <!-- Большой логотип FCL и подпись под ним (одинаковая ширина) -->
          <div class="hero__fcl-logo-wrap">
            <div class="hero__fcl-logo">
              <img src="@/assets/fcl-logo-hero.png" alt="FCL" class="hero__fcl-logo-image" />
            </div>
            <p class="hero__logo-caption">FINANCIAL CYBERSPORT LEAGUE</p>
          </div>

          <!-- Текстовый блок -->
          <div class="hero__text">
            <h1 class="hero__title">FINANCIAL CYBERSPORT LEAGUE</h1>
            <p class="hero__subtitle">— больше, чем просто турнир</p>
            <p class="hero__description">
              Ежегодно мы собираем всех фанатов киберспорта и проводим масштабный турнир по 3 игровым дисциплинам на онлайн-этапе и гранд-финале.<br />
              Параллельно с турниром в финале работают множество интерактивных зон, фотозоны<br />
              и проходит яркая трансляция.
            </p>
          </div>

          <!-- Галерея фотографий -->
          <div class="hero__gallery-scale" ref="heroGalleryScaleEl" :style="{ '--hero-gallery-scale': String(heroGalleryScale) }">
            <div class="hero__gallery">
              <div class="hero__photo hero__photo--left">
                <img src="@/assets/hero-left.png" alt="Турнир FCL" />
              </div>
              <div class="hero__photo hero__photo--center">
                <img src="@/assets/hero-center.png" alt="Турнир FCL" />
              </div>
              <div class="hero__photo hero__photo--right">
                <img src="@/assets/hero-right.png" alt="Турнир FCL" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ИНФОРМАЦИОННЫЕ БЛОКИ -->
      <section class="section section--info">
        <div class="info-grid">
          <article class="info-card">
            <div class="info-card__head">
              <img class="info-card__icon" src="@/assets/info-icon-disciplines.svg" alt="" aria-hidden="true" />
              <h3 class="info-card__title">ДИСЦИПЛИНЫ</h3>
            </div>
            <p class="info-card__text">CS2, FC26 И DOTA 2.</p>
          </article>

          <article class="info-card">
            <div class="info-card__head">
              <img class="info-card__icon" src="@/assets/info-icon-participants.svg" alt="" aria-hidden="true" />
              <h3 class="info-card__title">УЧАСТНИКИ</h3>
            </div>
            <p class="info-card__text info-card__text--azoft">Студенты москвы, которые хотят улучшить навыки и попробовать свои силы в чём-то новом.</p>
          </article>

          <article class="info-card">
            <div class="info-card__head">
              <img class="info-card__icon" src="@/assets/info-icon-format.svg" alt="" aria-hidden="true" />
              <h3 class="info-card__title">ФОРМАТ</h3>
            </div>
            <p class="info-card__text">Турнир проводится в два этапа: Онлайн-этап и Очный гранд финал.</p>
          </article>
        </div>
      </section>

      <!-- РАСПИСАНИЕ -->
      <section class="section section--schedule">
        <h2 class="section__title section__title--outline">РАСПИСАНИЕ</h2>

        <div class="schedule-visual-scale" ref="scheduleScaleEl" :style="{ '--schedule-mobile-scale': String(scheduleMobileScale) }">
          <!-- В макете: 3 картинки фоном + горизонтальная линия и точки поверх -->
          <div class="schedule-visual" aria-label="Примерное расписание">
            <div class="schedule-visual__inner">
              <div class="schedule-visual__bg" aria-hidden="true">
                <img src="@/assets/schedule-1.png" alt="" class="schedule-visual__bg-img" />
                <img src="@/assets/schedule-2.png" alt="" class="schedule-visual__bg-img" />
                <img src="@/assets/schedule-3.png" alt="" class="schedule-visual__bg-img" />
              </div>

              <!-- Оверлей центрируем по Figma-артборду 1440px -->
              <div class="schedule-visual__overlay">
                <div class="schedule-visual__segment schedule-visual__segment--1" aria-hidden="true"></div>
                <div class="schedule-visual__segment schedule-visual__segment--2" aria-hidden="true"></div>
                <div class="schedule-visual__segment schedule-visual__segment--3" aria-hidden="true"></div>

              <div class="schedule-step" style="--x: 11.1806%; --label-w: 215px;">
                <div class="schedule-step__circle schedule-step__circle--sm">
                  <span class="schedule-step__dot" aria-hidden="true"></span>
                </div>
                <div class="schedule-step__vline" aria-hidden="true"></div>
                <div class="schedule-step__date">01.03</div>
                <div class="schedule-step__label">Начало регистрации участников</div>
              </div>

              <div class="schedule-step" style="--x: 35.5986%; --label-w: 220px;">
                <div class="schedule-step__circle schedule-step__circle--sm">
                  <span class="schedule-step__dot" aria-hidden="true"></span>
                </div>
                <div class="schedule-step__vline" aria-hidden="true"></div>
                <div class="schedule-step__date">22.03</div>
                <div class="schedule-step__label">Начало онлайн-этапа</div>
              </div>

              <div class="schedule-step" style="--x: 60.016%; --label-w: 216px;">
                <div class="schedule-step__circle schedule-step__circle--sm">
                  <span class="schedule-step__dot" aria-hidden="true"></span>
                </div>
                <div class="schedule-step__vline" aria-hidden="true"></div>
                <div class="schedule-step__date">15.03</div>
                <div class="schedule-step__label">Начало регистрации зрителей</div>
              </div>

                <div class="schedule-step schedule-step--final" style="--x: 80.625%; --label-w: 134px;">
                  <div class="schedule-step__circle schedule-step__circle--lg">
                    <img src="@/assets/schedule-trophy.svg" alt="" aria-hidden="true" class="schedule-step__trophy" />
                  </div>
                  <div class="schedule-step__vline schedule-step__vline--final" aria-hidden="true"></div>
                  <div class="schedule-step__date">28.03</div>
                  <div class="schedule-step__label schedule-step__label--center">Гранд-финал</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ИТОГИ -->
      <section class="section section--stats">
        <h2 class="section__title">ИТОГИ 25 ГОДА</h2>

        <!-- Макет: 3 колонки (310/368/420) с зазором 15px, справа один большой блок -->
        <div class="stats-layout-scale" ref="statsLayoutScaleEl" :style="{ '--stats-mobile-scale': String(statsMobileScale) }">
          <div class="stats-layout">
            <div class="stats-col stats-col--left">
              <article class="stats-tile stats-tile--outline stats-tile--sq">
                <div class="stats-tile__value stats-tile__value--dark">1030</div>
                <div class="stats-tile__label">зрителей в пике на трансляции</div>
              </article>

              <article class="stats-tile stats-tile--light stats-tile--short">
                <div class="stats-tile__value stats-tile__value--light">150+</div>
                <div class="stats-tile__label stats-tile__label--dark">посетителей проекта</div>
              </article>
            </div>

            <div class="stats-col stats-col--mid">
              <article class="stats-tile stats-tile--outline stats-tile--mid">
                <div class="stats-tile__value stats-tile__value--dark">Winstrike</div>
                <div class="stats-tile__label">площадка проекта</div>
              </article>

              <article class="stats-tile stats-tile--outline stats-tile--mid stats-tile--with-icon">
                <div class="stats-tile__icon-wrap" aria-hidden="true">
                  <img src="@/assets/stats-trophy.svg" alt="" class="stats-tile__icon" />
                </div>
                <div class="stats-tile__value stats-tile__value--dark">450+</div>
                <div class="stats-tile__label">участников проекта</div>
              </article>
            </div>

            <article class="stats-panel stats-panel--light">
              <div class="stats-panel__title">VK и TG</div>
              <div class="stats-panel__metric">
                <div class="stats-panel__value">7800</div>
                <div class="stats-panel__label">охваты</div>
              </div>
              <div class="stats-panel__metric">
                <div class="stats-panel__value">150272</div>
                <div class="stats-panel__label">просмотров</div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- CTA: ТЕЛЕГРАМ -->
      <section class="section section--cta">
        <div class="cta-layout">
          <div class="cta-layout__images">
            <div class="cta-image cta-image--back">
              <img src="@/assets/hero-left.png" alt="FCL турнир" />
            </div>
            <div class="cta-image cta-image--front">
              <img src="@/assets/hero-center.png" alt="FCL турнир" />
            </div>
          </div>
          <div class="cta-layout__content">
            <h2 class="section__title section__title--outline">ХОЧЕШЬ ЗНАТЬ БОЛЬШЕ?</h2>
            <p class="cta__text">
              Вся информация о турнире и киберспортивной жизни в нашем телеграм-канале
            </p>
            <div class="cta__actions">
              <a href="https://t.me/fcl_26" target="_blank" rel="noreferrer" class="cta__button">Подписаться</a>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section class="section section--faq">
        <h2 class="section__title">FAQ</h2>
        <div class="faq-list">
          <article
            v-for="(item, index) in faqItems"
            :key="index"
            class="faq-item"
            :class="{ 'faq-item--open': openedFaqIndex === index }"
            @click="toggleFaq(index)"
          >
            <div class="faq-item__inner">
              <!-- Лицевая сторона карточки -->
              <div class="faq-item__face faq-item__face--front">
                <h3 class="faq-item__question">{{ item.question }}</h3>
                <span class="faq-item__arrow" aria-hidden="true"></span>
              </div>
              <!-- Обратная сторона карточки -->
              <div class="faq-item__face faq-item__face--back">
                <p class="faq-item__answer">
                  {{ item.answer }}
                </p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- ПАРТНЁРЫ -->
      <section class="section section--partners" id="partners">
        <h2 class="section__title">НАМ ДОВЕРЯЮТ</h2>
          <div class="partners-marquee">
          <div class="partners-marquee__track">
            <div class="partners-strip-wrap"><img :src="partnersStrip" alt="Партнёры" class="partners-strip" /></div>
            <div class="partners-strip-wrap partners-strip-wrap--tach"><img src="/tach-logo-white.svg" alt="Tach" class="partners-strip partners-strip--tach" /></div>
            <div class="partners-strip-wrap"><img :src="partnersStrip" alt="" aria-hidden="true" class="partners-strip" /></div>
            <div class="partners-strip-wrap partners-strip-wrap--tach"><img src="/tach-logo-white.svg" alt="" aria-hidden="true" class="partners-strip partners-strip--tach" /></div>
            <div class="partners-strip-wrap"><img :src="partnersStrip" alt="" aria-hidden="true" class="partners-strip" /></div>
            <div class="partners-strip-wrap partners-strip-wrap--tach"><img src="/tach-logo-white.svg" alt="" aria-hidden="true" class="partners-strip partners-strip--tach" /></div>
          </div>
        </div>
      </section>

      <!-- КОНТАКТЫ -->
      <section class="section section--contacts" id="contacts">
        <h2 class="section__title">КОНТАКТЫ</h2>
        <div class="contacts-grid">
          <article v-for="contact in contacts" :key="contact.email" class="contact-card">
            <h3 class="contact-card__name">{{ contact.name }}</h3>
            <p class="contact-card__role">{{ contact.role }}</p>
            <div class="contact-card__photo">
              <img :src="contact.photo" :alt="contact.name" loading="lazy" />
            </div>
            <p class="contact-card__meta">
              <a class="contact-card__link" :href="`mailto:${contact.email}`">{{ contact.email }}</a>
              <br />
              <a
                class="contact-card__link"
                :href="`https://t.me/${contact.telegram.replace('@', '')}`"
                target="_blank"
                rel="noreferrer"
              >
                Telegram: {{ contact.telegram }}
              </a>
            </p>
          </article>
        </div>
      </section>
  </main>

    <!-- FOOTER -->
    <footer class="fcl-footer">
      <img src="@/assets/fcl-logo-footer.png" alt="FCL Logo" class="fcl-footer__logo" />
      <a href="https://t.me/fcl_26/44" target="_blank" rel="noreferrer" class="contacts__rules-btn footer__rules-btn">Положение</a>
    </footer>
  </div>
</template>

<style scoped>
/* Импорт шрифтов */
@import './assets/fonts.css';

.fcl-page {
  min-height: 100vh;
  background: #0F0121;
  color: #FFFFFF;
  position: relative;
  overflow-x: hidden;
  font-family: 'Cygre', system-ui, -apple-system, sans-serif;
}

/* Фоновые градиенты */
.fcl-page::before,
.fcl-page::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.4;
  pointer-events: none;
}

.fcl-page::before {
  width: 820px;
  height: 820px;
  left: 1030px;
  top: -52px;
  background: radial-gradient(
    50% 50% at 50% 50%,
    rgba(151, 125, 255, 0.7) 0%,
    rgba(151, 125, 255, 0) 99.04%
  );
}

/* Ellipse 9372 — левое свечение под верхним логоблоком */
.fcl-page::after {
  width: 695px;
  height: 729px;
  left: -346px;
  top: 592px;
  background: radial-gradient(
    50% 50% at 50% 50%,
    rgba(151, 125, 255, 0.7) 0%,
    rgba(151, 125, 255, 0) 99.04%
  );
}

/* HEADER — на всю ширину экрана */
.fcl-header {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 48px 80px 0 80px;
  position: relative;
  z-index: 10;
}

.fcl-header__menu-toggle {
  display: none;
  width: 38px;
  height: 30px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  position: relative;
  z-index: 16;
}

.fcl-header__menu-toggle span {
  display: block;
  width: 100%;
  height: 2px;
  background: #FFFFFF;
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.fcl-header__menu-toggle span + span {
  margin-top: 8px;
}

.fcl-header__menu-toggle--open span:nth-child(1) {
  transform: translateY(10px) rotate(45deg);
}

.fcl-header__menu-toggle--open span:nth-child(2) {
  opacity: 0;
}

.fcl-header__menu-toggle--open span:nth-child(3) {
  transform: translateY(-10px) rotate(-45deg);
}

.fcl-header__logo {
  width: 104px;
  height: 58px;
  object-fit: contain;
  flex-shrink: 0;
}

.fcl-nav {
  display: flex;
  gap: 64px;
  text-transform: uppercase;
  font-size: 18.18px;
  letter-spacing: 0.05em;
  font-family: 'Cygre', sans-serif;
}

.fcl-nav a {
  color: #FFFFFF;
  text-decoration: none;
  position: relative;
  display: inline-block;
}

.fcl-nav a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 100%;
  height: 1.5px;
  background: #FFFFFF;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.2s ease;
}

.fcl-nav a:hover::after,
.fcl-nav a:focus-visible::after {
  transform: scaleX(1);
}

.fcl-header__social {
  display: flex;
  gap: 12px;
}

.fcl-header__icon {
  width: 45px;
  height: 45px;
  object-fit: contain;
  /* Иконки в ассетах сейчас чёрные — приводим к белым как в макете */
  filter: brightness(0) invert(1);
}

/* HERO SECTION — подстраивается под экран (Figma: лого 1140×566, top 213px, left 143px) */
.hero {
  position: relative;
  padding: 0 clamp(24px, 10vw, 156px);
  margin-top: clamp(48px, 14.8vw, 213px);
  overflow: hidden;
}

.hero__container {
  position: relative;
  z-index: 3;
  max-width: min(1440px, 100%);
  margin: 0 auto;
}

.hero__bg {
  position: absolute;
  top: 40px;
  right: -420px;
  width: 754px;
  height: 733px;
  z-index: 1;
  pointer-events: none;
}

.hero__bg-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.hero__character {
  position: absolute;
  top: 29px;
  left: -440px;
  width: 521px;
  height: 554px;
  z-index: 1;
  pointer-events: none;
}

.hero__character-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Обёртка: логотип и подпись одинаковой ширины */
.hero__fcl-logo-wrap {
  width: 100%;
  max-width: min(1300px, 90vw);
  margin: 0 auto;
}

/* Пропорции из Figma: 1140.14 × 565.64 */
.hero__fcl-logo {
  width: 100%;
  aspect-ratio: 1140.14 / 565.64;
}

.hero__fcl-logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center top;
  display: block;
}

.hero__logo-caption {
  font-family: 'Cygre ExtraBold', 'Cygre', sans-serif;
  font-weight: 800;
  width: 100%;
  font-size: clamp(28px, 4.5vw, 72px);
  line-height: 1.05;
  letter-spacing: 0.055em;
  text-shadow: 0 0 0.74px #FFFFFF;
  margin: clamp(-220px, -15vw, -60px) 0 clamp(120px, 16vw, 240px);
  text-align: center;
  white-space: nowrap;
}

.hero__text {
  max-width: min(1127px, 78.3vw);
  margin: clamp(140px, 18vw, 260px) auto 72px;
  padding: 0 clamp(16px, 4vw, 48px);
}

.hero__title {
  font-family: 'Cygre ExtraBold', 'Cygre', sans-serif;
  font-weight: 800;
  font-size: clamp(36px, 5.8vw, 80px);
  line-height: 1.05;
  letter-spacing: 0.03em;
  margin-bottom: 4px;
  text-shadow: 0 0 0.68px #FFFFFF;
  white-space: nowrap;
}

.hero__subtitle {
  font-family: 'Cygre', sans-serif;
  font-size: 60px;
  line-height: 1.05;
  letter-spacing: 0.03em;
  margin-bottom: 28px;
  margin-left: 56px;
}

.hero__description {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 30.57px;
  line-height: 1.28;
  letter-spacing: 0.05em;
  max-width: 100%;
}

/* Три картинки: под наклоном и с наложением друг на друга, как в Figma */
.hero__gallery {
  position: relative;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto clamp(84px, 8vw, 130px);
  min-height: 500px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: clamp(-120px, -8vw, -60px);
  padding: 0 clamp(24px, 5vw, 80px);
  z-index: 5;
  overflow: visible;
}

.hero__gallery-scale {
  width: 100%;
  --hero-gallery-scale: 1;
}

.hero__photo {
  flex: 0 1 auto;
  min-width: 0;
  border: 2.36px solid #F2F2F2;
  border-radius: 0;
  overflow: hidden;
  transition: transform 0.2s ease;
  transform-origin: 50% 100%;
}

.hero__photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Левая — Figma: 110.84×73.89, angle -9.86°, left 12px, top 453.73 */
.hero__photo--left {
  align-self: flex-end;
  aspect-ratio: 110.84 / 73.89;
  width: clamp(380px, 40vw, 540px);
  border-width: 2.36px;
  transform: translateY(-10px) rotate(9.86deg);
  z-index: 2;
}

/* Центр — под первой и третьей */
.hero__photo--center {
  align-self: flex-end;
  aspect-ratio: 119.08 / 79.39;
  width: clamp(400px, 42vw, 540px);
  border-width: 2.6px;
  transform: translateY(16px) rotate(-2.38deg);
  z-index: 1;
}

/* Правая — Figma: 124.56×83.02, angle 14.21°, left 219.88px, top 430.23 */
.hero__photo--right {
  align-self: flex-end;
  aspect-ratio: 124.56 / 83.02;
  width: clamp(450px, 46vw, 630px);
  border-width: 2.6px;
  transform: translateY(-10px) rotate(-14.21deg);
  z-index: 2;
}

/* SECTIONS */
.section {
  padding: 0 156px;
  margin-bottom: 200px;
  position: relative;
  z-index: 6;
  max-width: 1440px;
  margin-left: auto;
  margin-right: auto;
}

.reveal-on-scroll {
  opacity: 0;
  transform: translate3d(0, 36px, 0);
  transition:
    opacity 820ms cubic-bezier(0.22, 1, 0.36, 1) var(--reveal-delay, 0ms),
    transform 820ms cubic-bezier(0.22, 1, 0.36, 1) var(--reveal-delay, 0ms);
  will-change: opacity, transform;
}

.reveal-on-scroll.is-visible {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

/* Keep hero gallery scale on mobile while reveal animation runs */
.hero__gallery.reveal-on-scroll {
  transform: translate3d(0, 36px, 0) scale(var(--hero-gallery-scale, 1));
}

.hero__gallery.reveal-on-scroll.is-visible {
  transform: translate3d(0, 0, 0) scale(var(--hero-gallery-scale, 1));
}

@media (prefers-reduced-motion: reduce) {
  .reveal-on-scroll {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

.section__title {
  font-family: 'Cygre ExtraBold', 'Cygre', sans-serif;
  font-weight: 800;
  font-size: 60px;
  line-height: 1.05;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 64px;
}

.section__title--outline {
  text-shadow:
    -1.34px -1.34px 0 #977DFF,
    1.34px -1.34px 0 #977DFF,
    -1.34px 1.34px 0 #977DFF,
    1.34px 1.34px 0 #977DFF,
    -0.67px -0.67px 0 #FFFFFF,
    0.67px -0.67px 0 #FFFFFF,
    -0.67px 0.67px 0 #FFFFFF,
    0.67px 0.67px 0 #FFFFFF;
}

/* INFO CARDS */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 48px;
}

.info-card {
  position: relative;
  padding: 0;
  border: none;
  border-radius: 0;
  background: transparent;
}

.info-card__head {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  position: relative;
}

.info-card__icon {
  width: 63.62px;
  height: 63.52px;
  flex: 0 0 auto;
  opacity: 0.5;
}

.info-card__title {
  font-family: 'Cygre', sans-serif;
  font-weight: 700;
  font-size: 31.81px;
  line-height: 1.58;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin: 0;
  /* Figma: заголовок начинается внутри области иконки (x~28.6 при icon ~63.6) */
  margin-left: -36px;
  padding-top: 2px;
}

.info-card__text {
  font-family: 'Cygre', sans-serif;
  font-size: 21.84px;
  line-height: 1.16;
}

.info-card__text--azoft {
  font-family: 'Cygre', sans-serif;
}

/* SCHEDULE */
.section--schedule .section__title {
  text-align: center;
  max-width: 855.64px;
  margin-left: auto;
  margin-right: auto;
  white-space: nowrap;
  /* чтобы на меньших экранах не переносилось */
  font-size: clamp(34px, 4.2vw, 60px);
}

.schedule-visual {
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  overflow-x: auto;
  padding: 0;
}

.schedule-visual-scale {
  width: 100%;
  --schedule-mobile-scale: 1;
}

.schedule-visual__inner {
  position: relative;
  /* Картинки в макете идут во всю ширину экрана */
  width: 100vw;
  min-width: 980px;
  margin: 0;
  height: clamp(420px, 34vw, 493px);
}

.schedule-visual__bg {
  position: absolute;
  inset: 0;
  display: flex;
  z-index: 1;
}

.schedule-visual__bg-img {
  flex: 1 1 0;
  min-width: 0;
  height: 100%;
  object-fit: cover;
  opacity: 0.3;
}

.schedule-visual__overlay {
  position: absolute;
  inset: 0;
  left: 50%;
  right: auto;
  width: 1440px;
  max-width: 100%;
  transform: translateX(-50%);
  z-index: 3;
  /* Чуть приподнимаем весь таймлайн относительно картинок */
  --schedule-shift-y: -10px;
  /* Центры точек из макета */
  --x1: 11.1806%;
  --x2: 35.5986%;
  --x3: 60.016%;
  --x4: 80.625%;
  /* Отступ линии от центра точки */
  --track-gap: clamp(56px, 4vw, 66px);
}

.schedule-visual__segment {
  position: absolute;
  z-index: 2;
  height: 2px;
  background: #F2F2F2;
  top: calc(clamp(84px, 9vw, 111px) + 39px + var(--schedule-shift-y));
}

/* Сегменты линии с зазорами — не соединяются в одну сплошную */
.schedule-visual__segment--1 {
  left: calc(var(--x1) + var(--track-gap));
  right: calc(100% - (var(--x2) - var(--track-gap)));
}

.schedule-visual__segment--2 {
  left: calc(var(--x2) + var(--track-gap));
  right: calc(100% - (var(--x3) - var(--track-gap)));
}

.schedule-visual__segment--3 {
  left: calc(var(--x3) + var(--track-gap));
  right: calc(100% - (var(--x4) - var(--track-gap)));
}

.schedule-step {
  position: absolute;
  z-index: 3;
  left: var(--x);
  top: 0;
  width: 0;
  height: 0;
}

.schedule-step__circle,
.schedule-step__vline,
.schedule-step__date,
.schedule-step__label {
  position: absolute;
  left: 0;
  transform: none;
}

.schedule-step__circle--sm {
  width: 78px;
  height: 78px;
  margin-left: -39px;
  top: calc(clamp(84px, 9vw, 111px) + var(--schedule-shift-y));
  border: 10.5px solid #F2F2F2;
  box-sizing: border-box;
  border-radius: 50%;
}

.schedule-step__dot {
  position: absolute;
  width: 13px;
  height: 13px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  background: #F2F2F2;
  border-radius: 50%;
}

.schedule-step__circle--lg {
  width: 92px;
  height: 92px;
  margin-left: -46px;
  top: calc(clamp(80px, 8.6vw, 106px) + var(--schedule-shift-y));
  border: none;
  display: grid;
  place-items: center;
}

.schedule-step__trophy {
  width: 92px;
  height: 92px;
  display: block;
}

.schedule-step__vline {
  width: 0;
  height: 130px;
  margin-left: 0;
  border-left: 2px solid #F2F2F2;
  /* Линия начинается под кругом, а не из его центра */
  top: calc(clamp(84px, 9vw, 111px) + 78px + 12px + var(--schedule-shift-y));
  transform: none;
}

.schedule-step__vline--final {
  height: 102px;
  top: calc(clamp(80px, 8.6vw, 106px) + 92px + 12px + var(--schedule-shift-y));
}

.schedule-step__date {
  /* Чуть ниже, чтобы вертикальная линия не упиралась в текст */
  top: calc(clamp(282px, 24vw, 341px) + var(--schedule-shift-y));
  width: 69px;
  margin-left: -34.5px;
  height: 42px;
  font-family: 'Cygre ExtraBold', 'Cygre', sans-serif;
  font-weight: 800;
  font-size: 40.19px;
  line-height: 1.05;
  letter-spacing: 0.03em;
  font-variant-numeric: tabular-nums;
  color: #FFFFFF;
  -webkit-text-stroke: 0.44px #FFFFFF;
  text-align: center;
  display: grid;
  place-items: center;
  transform: translateX(var(--date-shift-x, -22px));
}

.schedule-step__label {
  top: calc(clamp(344px, 28vw, 408px) + var(--schedule-shift-y));
  width: var(--label-w);
  margin-left: calc(var(--label-w) / -2);
  min-height: 25px;
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 21.84px;
  line-height: 1.159;
  color: #FFFFFF;
  opacity: 0.8;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.schedule-step__label--center {
  top: calc(clamp(356px, 29vw, 420px) + var(--schedule-shift-y));
}

.section--faq .section__title {
  text-align: left;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.faq-item {
  position: relative;
  border-radius: 0;
  border: 1px solid rgba(242, 242, 242, 0.6);
  background: transparent;
  cursor: pointer;
  perspective: 1200px;
  min-height: 120px;
}

.faq-item:last-child {
  min-height: 160px;
}

.faq-item__inner {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 0;
  background: radial-gradient(circle at 0 0, rgba(151, 125, 255, 0.25), transparent 70%);
  transform-style: preserve-3d;
  transition: transform 0.6s ease;
}

.faq-item__face {
  position: absolute;
  inset: 0;
  padding: 24px 28px;
  backface-visibility: hidden;
}

.faq-item__face--back {
  transform: rotateY(180deg);
}

.faq-item--open .faq-item__inner {
  transform: rotateY(180deg);
}

.faq-item__question {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 21.84px;
  line-height: 1.16;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-right: 40px;
}

.faq-item__answer {
  font-family: 'Cygre', sans-serif;
  font-size: 21.84px;
  line-height: 1.16;
  opacity: 0.9;
}

.faq-item__arrow {
  position: absolute;
  right: 24px;
  top: 50%;
  width: 12px;
  height: 12px;
  border-right: 2px solid #ffffff;
  border-bottom: 2px solid #ffffff;
  transform: translateY(-50%) rotate(45deg);
}

.schedule-images,
.schedule-images__item {
  display: none;
}

/* STATS (ИТОГИ) — раскладка как в Figma (310/368/420 + 15px gaps) */
.section--stats {
  position: relative;
  overflow: visible;
}

.section--stats::after {
  content: '';
  position: absolute;
  width: min(1422.9px, 98vw);
  height: 765.56px;
  left: 50%;
  top: 42%;
  transform: translate(-50%, -50%);
  background: radial-gradient(
    50% 50% at 50% 50%,
    rgba(151, 125, 255, 0.7) 0%,
    rgba(151, 125, 255, 0) 99.04%
  );
  opacity: 0.4;
  pointer-events: none;
  z-index: 0;
}

.section--stats .section__title {
  position: relative;
  z-index: 1;
  text-align: center;
}

.stats-layout {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1128px; /* 310 + 368 + 420 + 15 + 15 */
  margin: 0 auto;
  display: grid;
  grid-template-columns: 310px 368px 420px;
  gap: 15px;
}

.stats-layout-scale {
  width: 100%;
  --stats-mobile-scale: 1;
}

.stats-col {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stats-col--left {
  min-width: 0;
}

.stats-col--mid {
  min-width: 0;
}

.stats-tile {
  position: relative;
  min-width: 0;
  border-radius: 0;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  text-align: left;
}

.stats-tile--outline {
  background: transparent;
  border: 3px solid #F2F2F2;
}

.stats-tile--light,
.stats-panel--light {
  background: #F2F2F2;
  color: #0F0121;
}

.stats-tile--sq {
  height: 310px;
}

.stats-tile--short {
  height: 138px;
}

.stats-tile--mid {
  height: 224px;
}

.stats-tile__value {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  letter-spacing: 0.1em;
}

.stats-tile__value--dark {
  font-size: 58.65px;
  line-height: 1.58;
  color: #FFFFFF;
  -webkit-text-stroke: 2.35px #FFFFFF;
  text-shadow: 0 0 0.7px rgba(255, 255, 255, 0.6);
}

.stats-tile__value--light {
  font-size: 54.62px;
  line-height: 1.58;
  color: #0F0121;
  -webkit-text-stroke: 2.18px #0F0121;
  text-shadow: 0 0 2.18px rgba(15, 1, 33, 0.35);
}

.stats-tile__label {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 21.84px;
  line-height: 1.159;
  color: #FFFFFF;
  opacity: 0.95;
  text-align: left;
}

.stats-tile__label--dark {
  color: #0F0121;
  opacity: 1;
}

.stats-tile--with-icon {
  padding-right: 92px;
}

.stats-tile__icon-wrap {
  position: absolute;
  right: 24px;
  top: 50%;
  width: 69px;
  height: 69px;
  background: transparent;
  display: grid;
  place-items: center;
  transform: translateY(-50%);
}

.stats-tile__icon {
  width: 69px;
  height: 69px;
  display: block;
}

.stats-panel {
  height: 463px;
  padding: 24px 28px;
  border-radius: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 28px;
  overflow: hidden;
  text-align: center;
}

.stats-panel__title {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 78.78px;
  line-height: 1.08;
  letter-spacing: 0.03em;
  text-align: center;
  -webkit-text-stroke: 3.15px #0F0121;
  text-shadow: 0 0 2px rgba(15, 1, 33, 0.15);
  margin-top: 6px;
}

.stats-panel__metric {
  width: 100%;
  padding-left: 0;
  text-align: center;
}

.stats-panel__value {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 54.62px;
  line-height: 1.58;
  letter-spacing: 0.06em;
  -webkit-text-stroke: 2.18px #0F0121;
}

.stats-panel__label {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 28.85px;
  line-height: 1.159;
  margin-top: 4px;
}

/* CTA */
.section--cta {
  text-align: left;
  max-width: 1353px;
  margin-left: auto;
  margin-right: auto;
  position: relative;
}

.cta-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1.1fr);
  gap: 40px;
  align-items: center;
}

.cta-layout__images {
  position: relative;
  max-width: 420px;
  height: 320px;
}

.cta-image {
  position: absolute;
  inset: 0;
  border: 2.6px solid #F2F2F2;
  overflow: hidden;
}

.cta-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cta-image--back {
  top: 32px;
  left: 0;
  transform: rotate(-6deg);
  opacity: 0.85;
}

.cta-image--front {
  top: 0;
  left: 48px;
  transform: rotate(4deg);
  z-index: 1;
}

.cta-layout__content {
  position: relative;
}

.cta__text {
  font-family: 'Cygre', sans-serif;
  font-size: 21.84px;
  line-height: 1.16;
  margin-bottom: 24px;
  max-width: 508px;
}

.cta__actions {
  display: flex;
  align-items: center;
  justify-content: center;
}

.cta__button {
  display: inline-block;
  padding: 17px 31px;
  background: #FFFFFF;
  color: #0F0121;
  text-decoration: none;
  font-family: 'Cygre', sans-serif;
  font-size: 15.04px;
  line-height: 1.16;
  text-transform: uppercase;
  border-radius: 0;
}

/* PARTNERS */
.section--partners {
  max-width: none;
  padding-left: 0;
  padding-right: 0;
  margin-bottom: 80px;
}

.section--partners .section__title {
  max-width: 1440px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 156px;
  text-align: center;
}

.partners-marquee {
  position: relative;
  overflow: hidden;
  margin-top: 12px;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
  padding: 4px 0;
}

.partners-marquee__track {
  --partners-gap: 80px;
  display: flex;
  align-items: center;
  gap: var(--partners-gap);
  padding: 0 var(--partners-gap);
  animation: partners-scroll 22s linear infinite;
  width: max-content;
  will-change: transform;
}

/* wrap — 100vw, без scale чтобы не наезжали */
.partners-strip-wrap {
  flex: 0 0 100vw;
  position: relative;
  width: 100vw;
  height: clamp(140px, 14vw, 280px);
  overflow: hidden;
}

.partners-strip {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 100vw;
  height: auto;
  min-height: 100%;
  object-fit: contain;
  object-position: center;
  box-sizing: border-box;
  padding: 0 clamp(10px, 2vw, 24px);
}

@keyframes partners-scroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(calc(-100vw - var(--partners-gap)));
  }
}

.partners-strip-wrap--tach {
  display: flex;
  justify-content: center;
  align-items: center;
}

.partners-strip--tach {
  position: static;
  transform: none;
  width: auto;
  height: clamp(48px, 6vw, 80px);
  min-height: 0;
  padding: 0;
}

/* CONTACTS */
.section--contacts {
  position: relative;
  overflow: visible;
}

.section--contacts::before {
  content: '';
  position: absolute;
  width: min(1719px, 120vw);
  height: 858px;
  left: 50%;
  top: 58%;
  transform: translate(-50%, -50%);
  background: radial-gradient(
    50% 50% at 50% 50%,
    rgba(151, 125, 255, 0.7) 0%,
    rgba(151, 125, 255, 0) 99.04%
  );
  opacity: 0.4;
  pointer-events: none;
  z-index: 0;
}

.section--contacts .section__title {
  text-align: center;
  position: relative;
  z-index: 1;
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 48px;
  margin-bottom: 48px;
  position: relative;
  z-index: 1;
}

.contact-card {
  min-width: 0;
  text-align: center;
}

.contact-card__photo {
  width: 100%;
  max-width: 280px;
  margin-left: auto;
  margin-right: auto;
  border: 2.02px solid #FFFFFF;
  overflow: hidden;
  box-shadow:
    0px 6.73px 13.47px 0px rgba(0, 0, 0, 0.25),
    6.73px 0px 13.47px 0px rgba(0, 0, 0, 0.25),
    0px -6.73px 13.47px 0px rgba(0, 0, 0, 0.25),
    -6.73px 0px 13.47px 0px rgba(0, 0, 0, 0.25);
  aspect-ratio: 280 / 334;
  margin-bottom: 18px;
}

.contact-card__photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.contact-card__name {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: clamp(26px, 2.25vw, 33.67px);
  line-height: 1.58;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin: 0 0 2px 0;
  text-shadow: 0 0 0.67px #FFFFFF;
  text-align: center;
  white-space: nowrap;
}

.contact-card__role {
  font-family: 'Cygre', sans-serif;
  font-weight: 400;
  font-size: 20.88px;
  line-height: 1.58;
  letter-spacing: 0.05em;
  margin: 0 0 18px 0;
  text-transform: capitalize;
  text-align: center;
}

.contact-card__meta {
  font-family: 'Cygre', sans-serif;
  font-size: 18.18px;
  line-height: 1.32;
  letter-spacing: 0.05em;
  margin: 14px auto 0;
  text-align: center;
  text-transform: uppercase;
}

.contact-card__link {
  color: #FFFFFF;
  text-decoration: none;
}

.contact-card__link:hover {
  text-decoration: underline;
}

.contacts__rules-btn {
  display: inline-block;
  padding: 10px 24px;
  border: none;
  text-decoration: none;
  color: #FFFFFF;
  text-transform: uppercase;
  font-family: 'Cygre', sans-serif;
  font-size: 18.18px;
  line-height: 1.3;
  letter-spacing: 0.05em;
  text-align: center;
  border-radius: 0;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.contacts__rules-btn::after {
  content: '';
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 6px;
  height: 1.5px;
  background: #FFFFFF;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.2s ease;
}

.contacts__rules-btn:hover::after,
.contacts__rules-btn:focus-visible::after {
  transform: scaleX(1);
}

/* FOOTER */
.fcl-footer {
  padding: 48px 156px;
  display: flex;
  align-items: flex-end;
  gap: 18px;
  max-width: 1440px;
  margin: 0 auto;
}

.fcl-footer__logo {
  width: 122px;
  height: 68px;
  object-fit: contain;
}

.footer__rules-btn {
  margin-bottom: 6px;
}

/* Адаптивность */
@media (max-width: 1440px) {
  .fcl-page {
    font-size: 14px;
  }
  
  .hero {
    padding: 0 80px;
  }
  
  .section {
    padding: 0 80px;
  }
}

@media (max-width: 1024px) {
  .fcl-header {
    padding: 24px 32px 0;
    flex-wrap: wrap;
    gap: 24px;
  }
  
  .hero {
    padding: 0 32px;
    min-height: auto;
  }
  
  .hero__fcl-logo {
    max-width: 100%;
  }
  
  .hero__logo-caption {
    white-space: nowrap;
  }

  .hero__text {
    max-width: min(1127px, 85vw);
    margin: clamp(120px, 18vw, 200px) auto 60px;
    padding: 0 24px;
  }

  .hero__gallery-scale {
    height: calc(500px * var(--hero-gallery-scale));
    display: flex;
    justify-content: center;
    overflow: visible;
    margin-bottom: 64px;
  }

  .hero__gallery {
    flex-direction: row;
    align-items: flex-end;
    justify-content: center;
    gap: 0;
    margin-bottom: 0;
    padding: 0;
    min-height: 500px;
    width: 1360px;
    max-width: none;
    transform: scale(var(--hero-gallery-scale));
    transform-origin: top center;
  }

  .cta-layout {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .cta-layout__images {
    margin: 0 auto;
    max-width: 320px;
    height: 260px;
  }
  
  .hero__photo {
    width: auto;
    max-width: none;
  }

  .hero__photo--left {
    width: 525px;
    transform: translateY(-10px) rotate(9.86deg);
    z-index: 2;
  }

  .hero__photo--center {
    width: 565px;
    transform: translateY(16px) rotate(-2.38deg);
    z-index: 1;
  }

  .hero__photo--right {
    width: 590px;
    transform: translateY(-10px) rotate(-14.21deg);
    z-index: 2;
  }

  .schedule-visual-scale {
    --schedule-mobile-scale: clamp(0.56, calc((100vw - 48px) / 1440), 0.66);
    height: calc(493px * var(--schedule-mobile-scale));
    overflow: visible;
    display: flex;
    justify-content: center;
    padding-bottom: 8px;
  }

  .schedule-visual {
    width: 1440px;
    margin: 0;
    overflow: visible;
    transform: scale(var(--schedule-mobile-scale));
    transform-origin: top center;
  }

  .schedule-visual__inner {
    width: 1440px;
    min-width: 0;
    height: 493px;
  }
  
  .info-grid,
  .contacts-grid {
    grid-template-columns: 1fr;
  }

  /* ИТОГИ: сохраняем десктоп-композицию и просто уменьшаем целиком */
  .stats-layout-scale {
    width: 100%;
    margin: 0;
    height: calc(463px * var(--stats-mobile-scale));
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-bottom: 8px;
  }

  .stats-layout {
    width: 1128px;
    max-width: none;
    grid-template-columns: 310px 368px 420px;
    gap: 15px;
    margin: 0;
    transform: scale(var(--stats-mobile-scale));
    transform-origin: top center;
  }

  .stats-col {
    gap: 15px;
  }

  .stats-tile--sq {
    height: 310px;
    min-height: 0;
  }

  .stats-tile--short {
    height: 138px;
    min-height: 0;
  }

  .stats-tile--mid {
    height: 224px;
    min-height: 0;
  }

  .stats-panel {
    height: 463px;
    min-height: 0;
  }
  
  .section {
    padding: 0 32px;
  }
}

@media (max-width: 768px) {
  .fcl-header {
    padding: 14px 16px 0;
    gap: 10px;
    justify-content: space-between;
    align-items: center;
  }

  .fcl-header__logo {
    width: 92px;
    height: 52px;
  }

  .fcl-header__menu-toggle {
    display: block;
    order: 3;
  }

  .fcl-header__social {
    order: 2;
    margin-left: auto;
    margin-right: 10px;
    gap: 8px;
  }

  .fcl-header__icon {
    width: 34px;
    height: 34px;
  }

  .fcl-nav {
    position: absolute;
    top: calc(100% + 8px);
    left: 16px;
    right: 16px;
    width: auto;
    display: none;
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
    font-size: 14px;
    background: rgba(15, 1, 33, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.22);
    padding: 14px 16px;
    z-index: 15;
  }

  .fcl-nav--open {
    display: flex;
  }

  .fcl-nav a::after {
    display: none;
  }

  .hero {
    padding: 0 16px;
    margin-top: 56px;
  }

  .hero__character {
    left: -180px;
    right: auto;
    top: 20px;
    width: 360px;
    height: auto;
    opacity: 0.95;
    transform: none;
  }

  .hero__bg {
    right: -340px;
    top: 20px;
    width: 520px;
    height: 520px;
  }

  .hero__logo-caption {
    font-size: clamp(18px, 4.5vw, 40px);
    letter-spacing: 0.02em;
    margin: clamp(-110px, -14vw, -50px) 0 clamp(52px, 8vw, 88px);
    white-space: nowrap;
  }

  .hero__text {
    max-width: min(100%, 520px);
    margin: clamp(96px, 20vw, 180px) auto 36px;
    padding: 0 8px;
    text-align: center;
  }

  .hero__title {
    font-size: clamp(18px, 5.2vw, 44px);
    margin-bottom: 8px;
    white-space: nowrap;
  }

  .hero__subtitle {
    font-size: clamp(24px, 7.4vw, 34px);
    margin-left: 0;
    margin-bottom: 16px;
  }

  .hero__description {
    font-size: clamp(16px, 4.3vw, 20px);
    line-height: 1.35;
    letter-spacing: 0.03em;
    max-width: 100%;
    margin-left: auto;
    margin-right: auto;
  }

  .hero__gallery-scale {
    height: calc(500px * var(--hero-gallery-scale));
    display: flex;
    justify-content: center;
    overflow: visible;
    margin-bottom: 42px;
    padding-bottom: calc(38px * var(--hero-gallery-scale));
  }

  .hero__gallery {
    width: 1680px;
    max-width: none;
    min-height: 500px;
    transform: scale(var(--hero-gallery-scale));
    transform-origin: top center;
    margin: 0;
    padding: 0;
    gap: 0;
    overflow: visible;
  }

  .hero__photo {
    flex: 0 0 auto;
  }

  /* Figma: left 12px, center 122.47px, right 219.88px; top: left 453.73, center 437.54, right 430.23; border 0.68/0.74/0.74 */
  .hero__photo--left {
    width: 525px;
    border-width: 2.2px;
    transform: translate(-35px, 0) rotate(9.86deg);
    z-index: 2;
  }

  .hero__photo--center {
    width: 565px;
    border-width: 2.6px;
    transform: translate(-2px, -11px) rotate(-2.38deg);
    z-index: 1;
  }

  .hero__photo--right {
    width: 590px;
    border-width: 2.6px;
    transform: translate(25px, -14px) rotate(-14.21deg);
    z-index: 2;
  }

  .info-card__head {
    justify-content: center;
    align-items: center;
    gap: 12px;
  }

  .info-card__title {
    margin-left: -56px;
    transform: translateY(-4px);
    text-align: center;
  }

  .info-card__icon {
    margin-left: 0;
  }

  .info-card__text {
    text-align: center;
  }

  .info-grid {
    gap: 72px;
  }

  .section {
    padding: 0 16px;
    margin-bottom: 112px;
  }

  .section--info {
    margin-top: -18px;
  }

  .section__title {
    font-size: clamp(30px, 8vw, 44px);
    margin-bottom: 28px;
  }

  .section--partners .section__title {
    padding: 0 16px;
  }

  .schedule-visual-scale {
    height: calc(410px * var(--schedule-mobile-scale));
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-bottom: 6px;
  }

  .schedule-visual {
    width: 980px;
    margin: 0;
    transform: scale(var(--schedule-mobile-scale));
    transform-origin: top center;
    overflow: visible;
  }

  .schedule-visual__inner {
    width: 980px;
    min-width: 0;
    height: 410px;
  }

  .schedule-visual__overlay {
    width: 980px;
    left: 0;
    transform: none;
    --schedule-shift-y: -22px;
    --track-gap: 42px;
  }

  .schedule-step__circle--sm {
    width: 64px;
    height: 64px;
    margin-left: -32px;
    border-width: 8px;
  }

  .schedule-step__circle--lg {
    width: 76px;
    height: 76px;
    margin-left: -38px;
  }

  .schedule-step__trophy {
    width: 76px;
    height: 76px;
  }

  .schedule-step__date {
    font-size: 30px;
    width: 58px;
    margin-left: -29px;
  }

  .schedule-step__label {
    font-size: 17px;
    line-height: 1.2;
  }

  .faq-item {
    min-height: 148px;
  }

  .faq-item:last-child {
    min-height: 200px;
  }

  .faq-item__face {
    padding: 18px 18px;
  }

  .faq-item__question,
  .faq-item__answer {
    font-size: 18px;
    line-height: 1.24;
    letter-spacing: 0.04em;
  }

  .contact-card__name {
    font-size: clamp(22px, 6.4vw, 30px);
    white-space: normal;
    line-height: 1.3;
  }

  .contact-card__role {
    font-size: clamp(16px, 4.8vw, 20px);
    line-height: 1.3;
  }

  .contact-card__meta {
    font-size: clamp(14px, 4vw, 18px);
  }

  .stats-layout-scale {
    padding-bottom: 10px;
  }

  .section--cta {
    text-align: center;
  }

  .cta-layout__content {
    text-align: center;
  }

  .cta-layout__images {
    width: min(320px, 100%);
    max-width: 290px;
    height: 228px;
    margin: 0 auto;
  }

  .cta__text {
    margin-left: auto;
    margin-right: auto;
  }

  .cta__actions {
    justify-content: center;
  }

  .partners-marquee__track {
    animation-duration: 28s;
  }

  .fcl-footer {
    padding: 24px 16px 34px;
    justify-content: center;
  }
}

@media (max-width: 560px) {
  .fcl-nav {
    font-size: 12px;
  }

  .info-card__title {
    margin-left: -50px;
    transform: translateY(-5px);
  }

  .hero__character {
    left: -200px;
    top: 16px;
  }

  .hero__bg {
    right: -372px;
    top: 0;
  }

  .hero__logo-caption {
    margin: -70px 0 48px;
  }

  .hero__gallery {
    margin-bottom: 0;
  }

  .hero__gallery-scale {
    margin-bottom: 34px;
  }

  .section--info {
    margin-top: -12px;
  }

  .section {
    margin-bottom: 88px;
  }

  .section--schedule .section__title {
    font-size: clamp(28px, 7.2vw, 34px);
  }

  .schedule-step__label {
    font-size: 15px;
  }

  .stats-layout-scale {
    padding-bottom: 12px;
  }
}
</style>
