import { createRouter, createWebHistory } from 'vue-router'
import Error404 from '@/views/errors/Error404.vue'
import Error500 from '@/views/errors/Error500.vue'
const Home = () => import('@/views/Home.vue')
const Catalog = () => import('@/views/Catalog.vue')
const About = () => import('@/views/About.vue')
const SearchView = () => import('@/views/SearchView.vue')
const Register = () => import('@/views/Register.vue')

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/catalogo', name: 'Catalogo', component: Catalog },
  {
    path: '/producto/:id',
    name: 'ProductDetails',
    component: () => import('@/views/ProductDetails.vue')
  },
  { path: '/500', name: 'Error500', component: Error500 },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: Error404
  },
  {
    path: '/nosotros',
    name: 'Nosotros',
    component: About
  },
  {
    path: '/busqueda',
    name: 'Busqueda',
    component: SearchView,
  },
  {
    path: '/registro',
    name: 'Register',
    component: Register,
  },
  {
    path: '/constructor',
    name: 'Constructor',
    component: () => import('@/views/Constructor.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/perfil',
    name: 'Perfil',
    component: () => import('@/views/Profile.vue')
  },
  {
    path: '/user/addresses',
    name: 'UserAddresses',
    component: () => import('@/views/UserAddresses.vue')
  },
  {
    path: '/user/addresses/new',
    name: 'AddressForm',
    component: () => import('@/views/AddressForm.vue')
  },
  {
    path: '/settings',
    name: 'UserSettings',
    component: () => import('@/views/UserSettings.vue')
  },
  {
    path: '/carrito',
    name: 'Carrito',
    component: () => import('@/views/CartView.vue')
  },
  {
    path: '/mfa',
    name: 'MFAVerify',
    component: () => import('@/views/MFAVerify.vue')
  },
  {
    path: '/recovery',
    name: 'Recovery',
    component: () => import('@/views/Recovery.vue')
  }
]

// Jerarquía de roles (debe coincidir con backend y useRole.js)
const ROLES_JERARQUIA = ['user', 'editor', 'admin', 'superadmin']

function decodeJWTRole(token) {
  try {
    const payload = token.split('.')[1]
    const padded = payload.replace(/-/g, '+').replace(/_/g, '/').padEnd(
      payload.length + (4 - (payload.length % 4)) % 4, '='
    )
    return JSON.parse(atob(padded))?.role || 'user'
  } catch { return null }
}

// ── Rutas que requieren sesión activa ──────────────────────────────────────
const RUTAS_PRIVADAS = ['/perfil', '/settings', '/carrito', '/user', '/mfa', '/dashboard']
// Rutas que NO deben ser accesibles si ya hay sesión
const RUTAS_SOLO_PUBLICAS = ['/login', '/registro']

const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * Navigation Guard — autenticación + RBAC.
 *
 * En cada ruta se pueden declarar:
 *   meta.requiresAuth  → true  (ruta privada; también cubre las de RUTAS_PRIVADAS)
 *   meta.roles         → ['admin', 'superadmin']  (lista exacta de roles permitidos)
 *   meta.minRole       → 'editor'  (rol mínimo jerárquico)
 *
 * Ejemplos en routes[]:
 *   { path: '/dashboard', meta: { requiresAuth: true, minRole: 'admin' }, ... }
 *   { path: '/admin',     meta: { requiresAuth: true, roles: ['admin','superadmin'] }, ... }
 */
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')

  // ── 1. Ruta solo para usuarios NO autenticados (login, registro) ──────────
  const esSoloPublica = RUTAS_SOLO_PUBLICAS.some(r => to.path.startsWith(r))
  if (esSoloPublica && token) {
    return next({ path: '/perfil' })
  }

  // ── 2. ¿Requiere autenticación? ───────────────────────────────────────────
  const esPrivadaLista  = RUTAS_PRIVADAS.some(r => to.path.startsWith(r))
  const esPrivadaMeta   = to.meta?.requiresAuth === true
  const necesitaAuth    = esPrivadaLista || esPrivadaMeta

  if (necesitaAuth && !token) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // ── 3. RBAC: verificar rol si la ruta lo requiere ─────────────────────────
  if (token && (to.meta?.roles || to.meta?.minRole)) {
    const userRole  = decodeJWTRole(token)
    const userLevel = ROLES_JERARQUIA.indexOf(userRole)

    // 3a. Lista exacta de roles
    if (to.meta.roles) {
      if (!to.meta.roles.includes(userRole)) {
        return next({ path: '/no-autorizado', query: { from: to.fullPath } })
      }
    }

    // 3b. Rol mínimo jerárquico
    if (to.meta.minRole) {
      const minLevel = ROLES_JERARQUIA.indexOf(to.meta.minRole)
      if (userLevel < minLevel) {
        return next({ path: '/no-autorizado', query: { from: to.fullPath } })
      }
    }
  }

  next()
})

export default router