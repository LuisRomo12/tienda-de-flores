<template>
  <div class="addresses-layout">
    <div class="container-md">
      
      <!-- Breadcrumbs -->
      <div class="breadcrumbs">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
        </svg>
        <span class="divider">/</span>
        <span>Inicio</span>
        <span class="divider">/</span>
        <span>User</span>
        <span class="divider">/</span>
        <span class="current">Addresses</span>
      </div>

      <!-- Header Center -->
      <div class="page-header">
        <div class="header-decoration">
           <div class="line"></div>
           <svg xmlns="http://www.w3.org/2000/svg" class="header-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
           <div class="line"></div>
        </div>
        <h1 class="title">Direcciones</h1>
        <p class="subtitle">Gestiona tus direcciones de entrega</p>
      </div>

      <div class="content-body">
        
        <!-- Empty State (Fallback for no addresses) -->
        <div v-if="direcciones.length === 0 && !loading" class="card empty-state">
          <div class="gradient-bar"></div>
          
          <div class="empty-content">
             <div class="empty-icon-wrap">
                <svg xmlns="http://www.w3.org/2000/svg" class="map-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                </svg>
                <div class="flower-dec top-left">🌸</div>
                <div class="flower-dec bottom-right">🌸</div>
                <div class="flower-dec top-right">🏵️</div>
             </div>
             
             <h2>No tienes direcciones guardadas</h2>
             <p>Agrega una dirección de entrega para que podamos llevar flores frescas hasta tu puerta</p>

             <button @click="goToAddAddress" class="btn-primary">
                <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                <span>Agregar nueva dirección</span>
              </button>
          </div>
        </div>

        <!-- Address Cards (When there are addresses) -->
        <div v-if="direcciones.length > 0">
           <div 
            v-for="direccion in direcciones" 
            :key="direccion.id"
            class="card address-card"
          >
            <div class="gradient-line"></div>
            
            <div class="card-body">
              <div class="card-header">
                <div class="address-details">
                  <h2 class="address-title">
                    <span class="icon-pin">📍</span>
                    {{ direccion.calle }} {{ direccion.sin_numero ? 'S/N' : '' }} {{ direccion.num_interior ? `Int. ${direccion.num_interior}` : '' }}
                  </h2>
                  <p class="address-text">
                    C.P. {{ direccion.codigo_postal }} - {{ direccion.estado }}, {{ direccion.municipio }}
                  </p>
                  <p class="address-text-small">
                    <span class="icon-type" v-if="direccion.tipo_domicilio === 'residencial'">🏠</span>
                    <span class="icon-type" v-else>💼</span>
                    Domicilio {{ direccion.tipo_domicilio }}
                  </p>
                  <p class="address-text-small">
                    <span class="icon-type">👤</span> {{ direccion.nombre_contacto }} - {{ direccion.telefono_contacto }}
                  </p>
                </div>
                
                <button @click="deleteAddress(direccion.id)" title="Eliminar dirección" class="btn-delete">
                  <svg xmlns="http://www.w3.org/2000/svg" class="trash-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
              
              <div v-if="direccion.es_principal" class="badge-container">
                <span class="badge-principal">Principal</span>
              </div>
            </div>
            
            <!-- Set Principal Option -->
            <div class="set-principal-bar" @click="setPrincipal(direccion.id)" v-if="!direccion.es_principal">
               <span class="set-principal-text">Fijar como principal</span>
               <svg xmlns="http://www.w3.org/2000/svg" class="check-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          
          <!-- Add Address Button (When not empty) -->
          <button 
            v-if="direcciones.length < 4"
            @click="goToAddAddress"
            class="btn-dashed"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon-dashed" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
            <span>Agregar nueva dirección</span>
          </button>
          <p v-else class="limit-msg">
            Límite de 4 direcciones alcanzado.
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const direcciones = ref([])
const loading = ref(true)

const fetchDirecciones = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/direcciones`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      direcciones.value = await response.json()
    } else {
      console.error('Error al obtener direcciones')
    }
  } catch (error) {
    console.error('Network error:', error)
  } finally {
    loading.value = false
  }
}

const deleteAddress = async (id) => {
  if (!confirm('¿Seguro que deseas eliminar esta dirección?')) return

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/direcciones/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      // Refresh list
      await fetchDirecciones()
    } else {
      alert('Hubo un error al eliminar.')
    }
  } catch (error) {
    console.error(error)
  }
}

const setPrincipal = async (id) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/direcciones/${id}/principal`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      await fetchDirecciones()
    } else {
      alert('Hubo un error al procesar tu solicitud.')
    }
  } catch (error) {
    console.error(error)
  }
}

const goToAddAddress = () => {
  router.push('/user/addresses/new')
}

onMounted(() => {
  fetchDirecciones()
})
</script>

<style scoped>
.addresses-layout {
  min-height: 100vh;
  background-color: var(--bg-creme);
  padding: 40px 20px;
}

.container-md {
  max-width: 800px;
  margin: 0 auto;
}

/* Breadcrumbs */
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-soft);
  margin-bottom: 24px;
}

.icon-small {
  width: 16px;
  height: 16px;
  color: var(--accent-pink);
}

.divider {
  color: var(--accent-pink);
}

.current {
  font-weight: 600;
  color: var(--text-primary);
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.header-decoration {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

.line {
  width: 40px;
  height: 1px;
  background-color: var(--border-color);
  margin: 0 10px;
}

.header-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-pink);
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 5px 0;
}

.subtitle {
  font-size: 0.9rem;
  color: var(--text-soft);
  margin: 0;
}

/* Content */
.content-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background-color: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 4px 15px var(--card-shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
  position: relative;
  margin-bottom: 16px;
}

.gradient-bar {
  height: 6px;
  width: 100%;
  background: linear-gradient(to right, var(--accent-pink), #f9a068);
}

/* Empty State */
.empty-state {
  text-align: center;
}

.empty-content {
  padding: 50px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon-wrap {
  width: 120px;
  height: 120px;
  background-color: rgba(244, 184, 193, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 24px;
}

.map-icon {
  width: 60px;
  height: 60px;
  color: var(--accent-pink);
}

.flower-dec {
  position: absolute;
  font-size: 20px;
}

.top-left { top: 15px; left: 15px; color: var(--accent-pink); }
.bottom-right { bottom: 20px; right: 20px; color: var(--accent-pink); }
.top-right { top: 30px; right: 15px; color: #f9a068; font-size: 16px; }

.empty-content h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px 0;
}

.empty-content p {
  font-size: 0.9rem;
  color: var(--text-soft);
  max-width: 350px;
  margin: 0 0 30px 0;
}

/* Buttons */
.btn-primary {
  padding: 12px 28px;
  background: linear-gradient(to right, #f5658e, #fb8592);
  color: white;
  font-weight: bold;
  font-size: 0.9rem;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(245, 101, 142, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(to right, #e3527a, #eb6c7d);
  box-shadow: 0 6px 15px rgba(245, 101, 142, 0.4);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.btn-dashed {
  width: 100%;
  padding: 16px;
  margin-top: 10px;
  background: transparent;
  border: 2px dashed rgba(214, 109, 129, 0.5);
  border-radius: 12px;
  color: var(--accent-pink);
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-dashed:hover {
  background-color: rgba(244, 184, 193, 0.2);
  border-color: var(--accent-pink);
}

.btn-icon-dashed {
  width: 20px;
  height: 20px;
}

/* Address Cards */
.address-card {
  display: flex;
  flex-direction: column;
}

.gradient-line {
  height: 4px;
  width: 100%;
  background: linear-gradient(to right, var(--accent-pink), #f9a068);
  opacity: 0.6;
}

.card-body {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.address-details {
  flex: 1;
}

.address-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-pin {
  color: var(--accent-pink);
  font-size: 1.1rem;
}

.address-text {
  font-size: 0.9rem;
  color: var(--text-soft);
  margin: 0 0 12px 28px;
}

.address-text-small {
  font-size: 0.8rem;
  color: var(--text-soft);
  margin: 0 0 6px 28px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-type {
  font-size: 1rem;
}

.btn-delete {
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-delete:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}

.trash-icon {
  width: 20px;
  height: 20px;
}

.badge-container {
  margin-top: 16px;
  margin-left: 28px;
}

.badge-principal {
  background-color: rgba(244, 184, 193, 0.3);
  color: var(--accent-pink);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
}

.set-principal-bar {
  border-top: 1px solid var(--border-color);
  background-color: rgba(0, 0, 0, 0.02);
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.3s;
}

.set-principal-bar:hover {
  background-color: rgba(244, 184, 193, 0.1);
}

.set-principal-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-pink);
}

.check-icon {
  width: 16px;
  height: 16px;
  color: var(--accent-pink);
}

.limit-msg {
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-soft);
  margin-top: 20px;
}
</style>
