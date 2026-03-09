// src/services/api.js
const cache = new Map();
let controller = null;

export const fetchData = async (endpoint) => {
  // 1. Implementar Cancelación (AbortController) [cite: 47]
  if (controller) {
    controller.abort(); 
  }
  controller = new AbortController();
  const { signal } = controller;

  // 2. Implementar Caché manual en memoria [cite: 48]
  if (cache.has(endpoint)) {
    console.log("Cargando desde caché:", endpoint);
    return cache.get(endpoint);
  }

  try {
    const response = await fetch(`http://localhost:8000/api${endpoint}`, { signal });
    if (!response.ok) throw new Error("Error en la carga de datos");
    
    const data = await response.ok ? await response.json() : null;
    
    // Guardar en caché para evitar llamadas repetidas [cite: 49]
    cache.set(endpoint, data);
    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Petición cancelada');
    } else {
      throw error;
    }
  }
};