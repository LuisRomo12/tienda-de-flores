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

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router