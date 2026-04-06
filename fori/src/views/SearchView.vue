<template>
  <div class="search-page">
    <h2>Buscador de Flores</h2>
    
    <div class="search-box">
      <input 
        v-model="query" 
        @input="buscar" 
        type="text" 
        placeholder="Escribe el nombre de una flor..."
      />
      <button @click="buscar">🔍 Buscar</button>
    </div>

    <div v-if="loading">Cargando resultados...</div>

    <div v-else class="results-grid">
      <div v-for="flor in resultados" :key="flor.id" class="flower-card">
        <h3>{{ flor.nombre }}</h3>
        <p>Categoría: {{ flor.categoria }}</p>
        <p class="price">${{ flor.precio }}</p>
      </div>
      <p v-if="resultados.length === 0 && query !== ''">
        No se encontraron flores que coincidan con "{{ query }}".
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const query = ref('');
const resultados = ref([]);
const loading = ref(false);

const debounce = (fn, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const executeSearch = async () => {
  if (query.value.length < 2) {
    resultados.value = [];
    return;
  }
  
  loading.value = true;
  try {
    console.time('busqueda-api');
    // Conexión a la API del Backend (FastAPI)
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/search?q=${query.value}`);
    console.timeEnd('busqueda-api');
    resultados.value = response.data.results;
    console.log("Evidencia API JSON:", response.data); // Para tu captura de pantalla
  } catch (error) {
    console.error("Error conectando con la API:", error);
  } finally {
    loading.value = false;
  }
};

const buscar = debounce(executeSearch, 400);
</script>

<style scoped>
/* Estilos alineados a tu paleta Rosa/Crema */
.search-page { padding: 40px; background-color: #FDF9F1; min-height: 80vh; }
.search-box { display: flex; gap: 10px; margin-bottom: 30px; }
input { padding: 10px; border: 2px solid #F4B8C1; border-radius: 8px; flex-grow: 1; }
button { background: #D66D81; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.flower-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #F4B8C1; text-align: center; }
.price { color: #D66D81; font-weight: bold; font-size: 1.2rem; }
</style>