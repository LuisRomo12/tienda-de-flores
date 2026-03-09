<template>
  <div class="address-form-layout">
    <div class="address-container">
      
      <!-- Top header with pin icon -->
      <div class="header-section">
        <div class="header-icon-container">
           <svg xmlns="http://www.w3.org/2000/svg" class="header-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
        </div>
        <h1 class="page-title">Agregar domicilio</h1>
        <p class="page-subtitle">Completa la información de tu dirección de entrega</p>
      </div>

      <div class="form-card">
        <!-- Gradient Top Bar -->
        <div class="gradient-bar"></div>
        
        <form @submit.prevent="submitAddress" class="address-form">
          
          <!-- Location Info -->
          <div class="form-section">
            <div class="section-title-wrap">
               <div class="section-icon-wrap location-icon-bg">
                  <svg xmlns="http://www.w3.org/2000/svg" class="section-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
               </div>
               <h2 class="section-title">Ubicación</h2>
            </div>
            
            <!-- Google Maps Autocomplete Search bar -->
            <div class="input-group">
              <label class="input-label">Buscar ubicación rápida <span class="text-xs text-gray-400 font-normal ml-2">(Rellenará el formulario mágicamente ✨)</span></label>
              <div class="input-with-icon">
                <div class="input-icon-left">
                  <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                  </svg>
                </div>
                <input ref="autocompleteInput" type="text" placeholder="Escribe tu dirección, lugar o código postal..." class="form-input has-icon search-input">
              </div>
            </div>

            <!-- Google Map View -->
            <div class="map-container">
              <div ref="mapContainer" class="google-map"></div>
              <p class="map-helper">Puedes arrastrar el pin <span class="text-xl">📍</span> para ajustar la ubicación exacta.</p>
            </div>

            <div class="input-group mt-15">
              <label class="input-label">Calle <span class="required">*</span></label>
              <input v-model="form.calle" type="text" required placeholder="Ej: Avenida las Leones" class="form-input">
            </div>

            <div class="checkbox-group">
              <input type="checkbox" id="sinNumero" v-model="form.sin_numero" class="form-checkbox">
              <label for="sinNumero" class="checkbox-label">Mi calle no tiene número</label>
            </div>

            <div class="grid-2-cols">
              <div class="input-group">
                <label class="input-label">Código Postal <span class="required">*</span></label>
                <input v-model="form.codigo_postal" type="text" required placeholder="Ej: 09440" class="form-input">
              </div>
              <div class="input-group">
                <label class="input-label">Estado <span class="required">*</span></label>
                <input v-model="form.estado" type="text" required placeholder="Ej: Jalisco" class="form-input">
              </div>
            </div>

            <div class="grid-2-cols">
              <div class="input-group">
                <label class="input-label">Municipio o alcaldía <span class="required">*</span></label>
                <input v-model="form.municipio" type="text" required class="form-input">
              </div>
              <div class="input-group">
                <label class="input-label">Localidad/Colonia <span class="required">*</span></label>
                <input v-model="form.colonia" type="text" required class="form-input">
              </div>
            </div>

            <div class="input-group mt-15">
               <label class="input-label">Número interior / Departamento (opcional)</label>
               <input v-model="form.num_interior" type="text" placeholder="Ej: 201" class="form-input">
            </div>

            <div class="input-group">
               <label class="input-label">Indicaciones para la entrega (opcional)</label>
               <textarea v-model="form.indicaciones" rows="3" placeholder="Ej: Entre calles, color del edificio..." class="form-textarea"></textarea>
            </div>
          </div>

          <!-- Tipo domicilio -->
          <div class="form-section">
            <div class="section-title-wrap">
               <div class="section-icon-wrap type-icon-bg">
                  <svg xmlns="http://www.w3.org/2000/svg" class="section-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                  </svg>
               </div>
               <h2 class="section-title">Tipo de domicilio</h2>
            </div>
            
            <div class="grid-2-cols-gap">
              <!-- Residencial Card -->
              <label 
                class="type-card"
                :class="{'active': form.tipo_domicilio === 'residencial'}"
              >
                <input type="radio" v-model="form.tipo_domicilio" value="residencial" class="hidden-radio">
                <div class="type-card-icon-wrap" :class="{'active-icon': form.tipo_domicilio === 'residencial'}">
                  <svg xmlns="http://www.w3.org/2000/svg" class="type-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                  </svg>
                </div>
                <span class="type-card-title" :class="{'active-text': form.tipo_domicilio === 'residencial'}">Residencial</span>
                <span class="type-card-subtitle">Casa o departamento</span>
              </label>

              <!-- Laboral Card -->
              <label 
                class="type-card"
                :class="{'active': form.tipo_domicilio === 'laboral'}"
              >
                <input type="radio" v-model="form.tipo_domicilio" value="laboral" class="hidden-radio">
                <div class="type-card-icon-wrap" :class="{'active-icon': form.tipo_domicilio === 'laboral'}">
                  <svg xmlns="http://www.w3.org/2000/svg" class="type-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd" />
                    <path d="M2 13.692V16a2 2 0 002 2h12a2 2 0 002-2v-2.308A24.974 24.974 0 0110 15c-2.796 0-5.487-.46-8-1.308z" />
                  </svg>
                </div>
                <span class="type-card-title" :class="{'active-text': form.tipo_domicilio === 'laboral'}">Laboral</span>
                <span class="type-card-subtitle">Oficina o negocio</span>
              </label>
            </div>
          </div>

          <!-- Contact Data -->
          <div class="form-section">
             <div class="section-title-wrap">
               <div class="section-icon-wrap contact-icon-bg">
                  <svg xmlns="http://www.w3.org/2000/svg" class="section-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
               </div>
               <h2 class="section-title">Datos de contacto</h2>
            </div>
             <p class="section-subtitle">Te llamaremos si hay un problema con la entrega.</p>

             <div class="input-group">
                <label class="input-label">Nombre y apellido <span class="required">*</span></label>
                <input v-model="form.nombre_contacto" type="text" required placeholder="Ej: Juan Pérez" class="form-input">
             </div>

             <div class="input-group">
                <label class="input-label">Teléfono <span class="required">*</span></label>
                <div class="input-with-icon">
                  <div class="input-icon-left">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon-small" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                    </svg>
                  </div>
                  <input v-model="form.telefono_contacto" type="tel" required placeholder="Ej: 5512345678" class="form-input has-icon">
                </div>
             </div>
          </div>

          <!-- Actions -->
          <div class="actions-group">
            <button 
              type="submit" 
              :disabled="isSubmitting"
              class="btn-submit"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
              </svg>
              <span>{{ isSubmitting ? 'Guardando...' : 'Guardar dirección' }}</span>
            </button>
            <button type="button" @click="goBack" class="btn-cancel">
              Cancelar
            </button>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isSubmitting = ref(false)

const autocompleteInput = ref(null)
const mapContainer = ref(null)
let map = null
let marker = null
let autocomplete = null
let geocoder = null

const form = ref({
  calle: '',
  sin_numero: false,
  codigo_postal: '',
  estado: '',
  municipio: '',
  localidad: '',
  colonia: '',
  num_interior: '',
  indicaciones: '',
  tipo_domicilio: 'residencial',
  nombre_contacto: '',
  telefono_contacto: '',
  es_principal: false
})

/**
 * Parses Google Place component array into our form's schema
 */
const fillFormFromPlace = (place) => {
  // Reset fields to avoid mixing old data
  form.value.calle = ''
  form.value.codigo_postal = ''
  form.value.estado = ''
  form.value.municipio = ''
  form.value.colonia = ''
  let route = ''
  let street_number = ''

  if (!place.address_components) return

  for (const component of place.address_components) {
    const componentType = component.types[0]

    switch (componentType) {
      case 'street_number':
        street_number = component.long_name
        break
      case 'route':
        route = component.long_name
        break
      case 'postal_code':
        form.value.codigo_postal = component.long_name
        break
      case 'administrative_area_level_1':
        form.value.estado = component.long_name
        break
      case 'locality': // City / Municipio
        form.value.municipio = component.long_name
        break
      case 'sublocality_level_1': // Colonia / Neighborhood
      case 'neighborhood':
        form.value.colonia = component.long_name
        break
    }
  }

  // Combine route and street number into "Calle" field
  form.value.calle = `${route} ${street_number}`.trim()
  
  // If we couldn't get a strict colonia, fallback to municipality
  if (!form.value.colonia && form.value.municipio) {
    form.value.colonia = form.value.municipio
  }
}

/**
 * Reverse geocoding when the user drops the marker
 */
const geocodePosition = (pos) => {
  geocoder.geocode({ location: pos }, (results, status) => {
    if (status === 'OK' && results[0]) {
      fillFormFromPlace(results[0])
      // Force change in the input manually mapped
      if(autocompleteInput.value) {
        autocompleteInput.value.value = results[0].formatted_address
      }
    }
  })
}

onMounted(() => {
  // Initialize Google Maps if the API is loaded
  if (typeof google === 'undefined') {
    console.error('Google Maps API is not loaded. Make sure the script is in index.html with a valid API key.')
    return
  }

  geocoder = new google.maps.Geocoder()

  // 1. Setup the Map
  const defaultPos = { lat: 19.432608, lng: -99.133209 } // CDMX default
  
  map = new google.maps.Map(mapContainer.value, {
    center: defaultPos,
    zoom: 13,
    styles: [
      {
        featureType: "poi",
        elementType: "labels",
        stylers: [{ visibility: "off" }] // Declutter map
      }
    ],
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false
  })

  // 2. Setup draggable Marker
  marker = new google.maps.Marker({
    map,
    draggable: true,
    animation: google.maps.Animation.DROP,
    position: defaultPos
  })

  // Listen to marker drag to reverse-geocode
  marker.addListener('dragend', () => {
    const position = marker.getPosition()
    geocodePosition(position)
    map.panTo(position)
  })

  // 3. Setup Places Autocomplete
  autocomplete = new google.maps.places.Autocomplete(autocompleteInput.value, {
    fields: ['address_components', 'geometry', 'formatted_address'],
    types: ['address']
  })

  // Bind autocomplete predictions to the map bounds broadly
  autocomplete.bindTo('bounds', map)

  autocomplete.addListener('place_changed', () => {
    const place = autocomplete.getPlace()

    if (!place.geometry || !place.geometry.location) {
      alert("No se encontraron detalles para este lugar.")
      return
    }

    // Move map and marker to the searched place
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport)
    } else {
      map.setCenter(place.geometry.location)
      map.setZoom(17)
    }
    
    marker.setPosition(place.geometry.location)

    // Populate the Vue form state
    fillFormFromPlace(place)
  })
})

const goBack = () => {
  router.push('/user/addresses')
}

const submitAddress = async () => {
  isSubmitting.value = true
  try {
    const token = localStorage.getItem('token')
    if(!token) {
      router.push('/login')
      return;
    }

    const payload = { ...form.value }
    
    // Determine locality mapping
    payload.localidad = payload.colonia // Fori uses locality/colonia interchangeably in form

    const response = await fetch('http://localhost:8000/api/user/direcciones', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      router.push('/user/addresses')
    } else {
      const errorData = await response.json()
      alert(errorData.detail || 'Error al guardar la dirección')
    }

  } catch (error) {
    console.error('Error enviando direccion:', error)
    alert('Ocurrió un error de red.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.address-form-layout {
  min-height: 100vh;
  background-color: var(--bg-creme);
  padding: 40px 20px;
}

.address-container {
  max-width: 650px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}

.header-icon {
  width: 32px;
  height: 32px;
  color: var(--accent-pink);
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.page-subtitle {
  font-size: 0.9rem;
  color: var(--text-soft);
}

.form-card {
  background-color: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 4px 15px var(--card-shadow);
  border: 1px solid var(--border-color);
  overflow: hidden;
  position: relative;
}

.gradient-bar {
  height: 6px;
  width: 100%;
  background: linear-gradient(to right, var(--accent-pink), #f9a068);
}

.address-form {
  padding: 30px 40px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.map-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
  margin-bottom: 5px;
}

.google-map {
  width: 100%;
  height: 250px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background-color: #f1f5f9; /* Fallback skeleton color */
  overflow: hidden;
}

.map-helper {
  font-size: 0.85rem;
  color: var(--text-soft);
  text-align: center;
  font-style: italic;
}

.search-input {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.search-input:focus {
  border-color: var(--accent-pink);
  box-shadow: 0 0 0 3px rgba(214, 109, 129, 0.25);
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 5px;
}

.section-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.location-icon-bg { background-color: rgba(244, 184, 193, 0.3); color: var(--accent-pink); }
.type-icon-bg { background-color: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.contact-icon-bg { background-color: rgba(168, 85, 247, 0.1); color: #a855f7; }

.section-icon {
  width: 16px;
  height: 16px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

.section-subtitle {
  font-size: 0.8rem;
  color: var(--text-soft);
  margin-left: 44px; /* Icon width + gap */
  margin-top: -15px;
  margin-bottom: 10px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mt-15 { margin-top: 15px; }

.input-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.required {
  color: #ef4444;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px 16px;
  background-color: var(--bg-creme);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-primary);
  outline: none;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-input:focus, .form-textarea:focus {
  border-color: var(--accent-pink);
  box-shadow: 0 0 0 2px rgba(214, 109, 129, 0.2);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--accent-pink);
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-soft);
  cursor: pointer;
}

.grid-2-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.grid-2-cols-gap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.type-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: var(--card-bg);
}

.type-card:hover {
  border-color: rgba(214, 109, 129, 0.4);
}

.type-card.active {
  border-color: var(--accent-pink);
  background-color: rgba(214, 109, 129, 0.05); /* very light pink */
}

.hidden-radio {
  display: none;
}

.type-card-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-creme);
  color: var(--text-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  transition: all 0.3s;
  border: 1px solid var(--border-color);
}

.type-card-icon-wrap.active-icon {
  background-color: rgba(214, 109, 129, 0.1);
  color: var(--accent-pink);
  border-color: transparent;
}

.type-icon {
  width: 20px;
  height: 20px;
}

.type-card-title {
  font-size: 0.9rem;
  font-weight: bold;
  color: var(--text-primary);
}

.type-card-title.active-text {
  color: var(--accent-pink);
}

.type-card-subtitle {
  font-size: 0.75rem;
  color: var(--text-soft);
  margin-top: 4px;
}

.input-with-icon {
  position: relative;
}

.input-icon-left {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  padding-left: 12px;
  display: flex;
  align-items: center;
  pointer-events: none;
}

.icon-small {
  width: 16px;
  height: 16px;
  color: var(--text-soft);
}

.has-icon {
  padding-left: 36px;
}

.actions-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
}

.btn-submit {
  width: 100%;
  padding: 16px;
  background: linear-gradient(to right, #f5658e, #fb8592);
  color: white;
  font-weight: bold;
  font-size: 1rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(245, 101, 142, 0.3);
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(to right, #e3527a, #eb6c7d);
  box-shadow: 0 6px 15px rgba(245, 101, 142, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  width: 20px;
  height: 20px;
  opacity: 0.9;
}

.btn-cancel {
  background: none;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-soft);
  cursor: pointer;
  transition: color 0.3s;
}

.btn-cancel:hover {
  color: var(--text-primary);
}

@media (max-width: 600px) {
  .grid-2-cols {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  .address-form {
    padding: 20px;
  }
}
</style>
