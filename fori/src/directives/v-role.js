// src/directives/v-role.js
//
// Directiva personalizada Vue: v-role
// Oculta o elimina elementos del DOM según el rol del usuario.
//
// Uso en template:
//   <button v-role="'admin'">Solo Admin</button>
//   <button v-role="['admin', 'superadmin']">Admin o Superadmin</button>
//   <button v-role.min="'editor'">Editor y superiores</button>
//
// Registrar en main.js:
//   import vRole from '@/directives/v-role'
//   app.directive('role', vRole)

const ROLES_JERARQUIA = ['user', 'editor', 'admin', 'superadmin']

function decodeJWT(token) {
  try {
    const payload = token.split('.')[1]
    const padded = payload.replace(/-/g, '+').replace(/_/g, '/').padEnd(
      payload.length + (4 - (payload.length % 4)) % 4, '='
    )
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

function getUserRole() {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')
  if (!token) return null
  const payload = decodeJWT(token)
  return payload?.role || 'user'
}

function hasAccess(binding) {
  const userRole = getUserRole()
  if (!userRole) return false  // No autenticado → ocultar siempre

  const value = binding.value  // 'admin' | ['admin', 'superadmin']
  const isMin = binding.modifiers?.min  // v-role.min="'editor'"

  if (isMin) {
    // Modo jerárquico: permitir si el rol del usuario >= rol mínimo
    const minRole = Array.isArray(value) ? value[0] : value
    const userLevel = ROLES_JERARQUIA.indexOf(userRole)
    const minLevel  = ROLES_JERARQUIA.indexOf(minRole)
    return userLevel >= minLevel && userLevel !== -1
  }

  // Modo lista: el rol debe estar en la lista
  const allowed = Array.isArray(value) ? value : [value]
  return allowed.includes(userRole)
}

const vRole = {
  /**
   * mounted: Se ejecuta cuando el elemento se inserta en el DOM.
   * Si el usuario no tiene el rol requerido, esconde el elemento.
   */
  mounted(el, binding) {
    if (!hasAccess(binding)) {
      // Guardar display original para posible restauración
      el._originalDisplay = el.style.display
      el.style.display = 'none'
      el.setAttribute('aria-hidden', 'true')
    }
  },

  /**
   * updated: Re-evalúa cuando cambia el binding (ej. cambio de ruta).
   */
  updated(el, binding) {
    if (!hasAccess(binding)) {
      el._originalDisplay = el.style.display || ''
      el.style.display = 'none'
      el.setAttribute('aria-hidden', 'true')
    } else {
      el.style.display = el._originalDisplay || ''
      el.removeAttribute('aria-hidden')
    }
  }
}

export default vRole
