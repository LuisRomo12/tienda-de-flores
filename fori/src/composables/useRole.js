// src/composables/useRole.js
//
// Composable RBAC para Vue.js
// Lee el rol del usuario desde el JWT almacenado en localStorage
// sin necesitar un endpoint extra.
//
// Uso en componente:
//   import { useRole } from '@/composables/useRole'
//   const { role, isAtLeast, hasRole, canDo } = useRole()

import { computed } from 'vue'

// Jerarquía de roles (debe coincidir con backend)
const ROLES_JERARQUIA = ['user', 'editor', 'admin', 'superadmin']

/**
 * Decodifica el payload de un JWT sin verificar la firma.
 * La verificación real la hace el servidor; aquí solo leemos claims para UI.
 */
function decodeJWT(token) {
  try {
    const payload = token.split('.')[1]
    // Añadir padding Base64 si es necesario
    const padded = payload.replace(/-/g, '+').replace(/_/g, '/').padEnd(
      payload.length + (4 - (payload.length % 4)) % 4, '='
    )
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

/**
 * Obtiene el rol actual del usuario desde el JWT en localStorage.
 * Retorna 'user' como fallback si no hay token o no tiene claim 'role'.
 */
function getCurrentRole() {
  const token = localStorage.getItem('access_token') || localStorage.getItem('token')
  if (!token) return null

  const payload = decodeJWT(token)
  if (!payload) return null

  // Tokens de admin tienen type='admin'; para UI de usuario nos interesa type='user'
  return payload.role || 'user'
}

export function useRole() {
  // Rol reactivo — se recalcula en cada llamada
  const role = computed(() => getCurrentRole())

  /**
   * Verifica si el usuario tiene exactamente uno de los roles indicados.
   * @param {string | string[]} roles
   */
  const hasRole = (roles) => {
    const allowed = Array.isArray(roles) ? roles : [roles]
    return allowed.includes(role.value)
  }

  /**
   * Verifica si el rol del usuario es igual o superior al mínimo requerido.
   * isAtLeast('editor') → true para editor, admin y superadmin.
   * @param {string} minRole
   */
  const isAtLeast = (minRole) => {
    const userLevel   = ROLES_JERARQUIA.indexOf(role.value)
    const requiredLevel = ROLES_JERARQUIA.indexOf(minRole)
    return userLevel >= requiredLevel && userLevel !== -1
  }

  /**
   * Mapa de permisos semánticos por acción.
   * Centraliza la lógica para no repetir listas de roles en los templates.
   */
  const canDo = computed(() => ({
    // Cualquier usuario autenticado
    verCatalogo:    isAtLeast('user'),
    verCarrito:     isAtLeast('user'),

    // Editores y superiores
    crearContenido: isAtLeast('editor'),
    editarContenido: isAtLeast('editor'),

    // Admins y superiores
    gestionarUsuarios: isAtLeast('admin'),
    verDashboard:      isAtLeast('admin'),
    eliminarRecursos:  isAtLeast('admin'),

    // Solo superadmin
    configurarSistema: hasRole('superadmin'),
    verLogs:           hasRole('superadmin'),
    asignarRoles:      hasRole('superadmin'),
  }))

  return {
    role,
    hasRole,
    isAtLeast,
    canDo,
  }
}
