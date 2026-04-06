import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import vScroll from './js/animations.js'
import vParallax from './js/dom.js'
import vMagnetic from './js/app.js'
import './css/animations.css'
import './css/base.css'

const app = createApp(App)

app.use(router)
app.use(i18n)
app.directive('scroll', vScroll)
app.directive('parallax', vParallax)
app.directive('magnetic', vMagnetic)
app.mount('#app')