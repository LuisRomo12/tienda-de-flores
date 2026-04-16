import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CartView from './CartView.vue';
import { createRouter, createMemoryHistory } from 'vue-router';

// 1. Mockear dependencias estructurales (Vue Router)
const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/login', component: {} }, { path: '/catalogo', component: {} }]
});

// 2. Interceptar y mockear la función global fetch para no tocar el backend real
global.fetch = vi.fn();

describe('Pruebas del Carrito de Compras (CartView.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    // Pre-simulamos una sesión activa
    localStorage.setItem('token', 'fake-jwt-token');
  });

  it('Debe aumentar la cantidad y actualizar el estado al hacer clic en el botón de agregar (+)', async () => {
    // ---- FASE DE PREPARACIÓN (Mocks) ----
    
    // Mock 1: Simular la respuesta inicial de la API al cargar el carrito
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        carrito_id: 1,
        items: [
          { id: 101, nombre: 'Ramo de Prueba', tipo: 'flor', precio: 50, cantidad: 1 }
        ]
      })
    });

    // Mock 2: Simular un "200 OK" cuando el botón "+" envíe su PATCH a la API
    fetch.mockResolvedValueOnce({
      ok: true
    });

    // Montar el componente con sus dependencias (router)
    const wrapper = mount(CartView, {
      global: {
        plugins: [router]
      }
    });

    // Esperar a que el hook 'onMounted' descargue el carrito simulado (vaciar stack de promesas)
    await new Promise(resolve => setTimeout(resolve, 50)); 

    // Verificamos que el estado inicial se configuró correctamente
    expect(wrapper.vm.cartItems.length).toBe(1);
    expect(wrapper.vm.cartItems[0].cantidad).toBe(1);

    // ---- FASE DE ACCIÓN ----

    // Buscar todos los botones de cantidad y filtrar por el de "+"
    const buttons = wrapper.findAll('.qty-btn');
    const btnIncrement = buttons.find(b => b.text() === '+');
    
    // Hacer clic en él
    await btnIncrement.trigger('click');

    // Esperar a que la lógica del componente y la petición de fetch terminen
    await new Promise(resolve => setTimeout(resolve, 50));

    // ---- FASE DE VERIFICACIÓN (Asserciones) ----

    // 1. Verificar el DOM / Estado: Que la cantidad se haya sumado al estado local del Frontend
    expect(wrapper.vm.cartItems[0].cantidad).toBe(2);

    // 2. Verificar Evento de Red: Que el componente sí disparó el evento correcto hacia la API
    expect(fetch).toHaveBeenCalledTimes(2); // Llamada de inicialización + Llamada de Actualización
    
    // Validar el body de la petición PATCH de actualización
    const updateCallOptions = fetch.mock.calls[1][1]; 
    expect(updateCallOptions.method).toBe('PATCH');
    const payloadDeseado = JSON.parse(updateCallOptions.body);
    expect(payloadDeseado.cantidad).toBe(2); // Se emitió correctamente enviar la nueva cant. 2
  });
});
