// src/services/api.js
// Usa apiClient (axios con interceptor JWT + auto-refresh) en lugar de fetch() nativo
import apiClient from '../api/axios.js'

const cache = new Map()
// Mapa de AbortControllers activos por endpoint
const controllers = new Map()

/**
 * Realiza un GET autenticado al endpoint indicado.
 * - Cancela peticiones duplicadas en vuelo (AbortController)
 * - Cachea la respuesta en memoria para evitar llamadas repetidas
 * - El token JWT se inyecta automáticamente via el interceptor de apiClient
 *
 * @param {string} endpoint  Ruta relativa, ej: '/flores' → GET /api/flores
 * @param {boolean} [useCache=true]  Pasar false para forzar recarga
 */
export const fetchData = async (endpoint, useCache = true) => {
  // 1. Caché manual en memoria
  if (useCache && cache.has(endpoint)) {
    console.log('[API] Cargando desde caché:', endpoint)
    return cache.get(endpoint)
  }

  // 2. Cancelar petición anterior al mismo endpoint si sigue activa
  if (controllers.has(endpoint)) {
    controllers.get(endpoint).abort()
  }
  const controller = new AbortController()
  controllers.set(endpoint, controller)

  try {
    // 3. Petición autenticada — el interceptor de axios.js inyecta
    //    el Authorization: Bearer <token> y gestiona el refresh automático
    const { data } = await apiClient.get(`/api${endpoint}`, {
      signal: controller.signal
    })

    cache.set(endpoint, data)
    return data
  } catch (error) {
    if (error.name === 'CanceledError' || error.name === 'AbortError') {
      console.log('[API] Petición cancelada:', endpoint)
    } else {
      // Re-lanzar para que el componente pueda manejar el error
      throw error
    }
  } finally {
    controllers.delete(endpoint)
  }
}

/**
 * Invalida una entrada del caché (útil al crear/editar recursos).
 * @param {string} endpoint
 */
export const invalidateCache = (endpoint) => {
  cache.delete(endpoint)
}