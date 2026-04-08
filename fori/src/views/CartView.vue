<template>
  <div class="cart-page-container">
    <div v-if="loading" class="loading-state">
      Cargando carrito...
    </div>
    
    <div v-else-if="cartItems.length === 0" class="empty-state">
      <h2>Tu carrito está vacío 🥀</h2>
      <p>Añade algunas flores o accesorios para comenzar.</p>
      <router-link to="/catalogo" class="btn-primary">Ir al catálogo</router-link>
    </div>

    <div v-else class="cart-layout">
      <!-- Lado Izquierdo: Resumen de Artículos (Order Summary) -->
      <div class="order-summary-col">
        <h2 class="section-title">Order Summary</h2>
        <div class="items-list">
          <div v-for="item in cartItems" :key="item.id" class="cart-item">
            <div class="item-img-wrapper">
              <img :src="item.imagen || '/placeholder.jpg'" :alt="item.nombre">
            </div>
            
            <div class="item-details">
              <h3 class="item-name">{{ item.nombre }}</h3>
              <p class="item-type">Tipo: <span>{{ item.tipo === 'flor' ? '🌸 Flor' : '🎀 Accesorio' }}</span></p>
            </div>

            <div class="item-actions">
              <p class="item-price">${{ item.precio.toFixed(2) }}</p>
              <div class="qty-selector">
                <button @click="updateQuantity(item, -1)" class="qty-btn" :disabled="item.updating">-</button>
                <span class="qty-display">{{ item.cantidad }}</span>
                <button @click="updateQuantity(item, 1)" class="qty-btn" :disabled="item.updating">+</button>
              </div>
              <button @click="removeItem(item.id)" class="remove-btn" :disabled="item.updating" title="Eliminar">🗑️</button>
            </div>
          </div>
        </div>

        <div class="coupon-section">
          <button class="btn-coupon">Add Coupon Code →</button>
        </div>
      </div>

      <!-- Lado Derecho: Checkout (Shopping Cart) -->
      <div class="checkout-col">
        <div class="checkout-header">
          <h2 class="section-title">Shopping Cart</h2>
          <span class="item-count-badge">{{ totalItems }} Items</span>
        </div>

        <div class="price-summary">
          <div class="price-row">
            <span>Subtotal:</span>
            <strong>${{ subtotal.toFixed(2) }}</strong>
          </div>
          <div class="price-row">
            <span>Delivery:</span>
            <strong>$0.00</strong>
          </div>
          <div class="price-row total-row">
            <span>Total:</span>
            <strong>${{ subtotal.toFixed(2) }}</strong>
          </div>
        </div>

        <div class="checkout-forms">
          <!-- Shipping / Promo (Mockup) -->
          <div class="form-row-2">
            <div class="input-group">
              <label>Shipping</label>
              <select class="form-input">
                <option>Standard Delivery - $0.00</option>
                <option>Express Delivery - $5.00</option>
              </select>
            </div>
            <div class="input-group">
              <label>Promo Code</label>
              <input type="text" placeholder="xxxx - xxxx" class="form-input">
            </div>
          </div>

          <!-- Address (Mockup) -->
          <div class="input-group">
            <label>Address</label>
            <input type="text" placeholder="Alpha Plus, Near Ralya Telephone exchange." class="form-input">
          </div>

          <!-- Payment (Mockup) -->
          <div class="payment-section">
            <label>Payment</label>
            <div class="payment-options">
              <label class="payment-radio">
                <input type="radio" name="payment_method" value="delivery">
                <span>Payment Delivery</span>
              </label>
              <label class="payment-radio selected">
                <input type="radio" name="payment_method" value="card" checked>
                <span>Card Payment</span>
              </label>
              <label class="payment-radio">
                <input type="radio" name="payment_method" value="paypal">
                <span>PayPal Payment</span>
              </label>
            </div>
          </div>

          <!-- Card Details (Mockup) -->
          <div class="card-details">
            <div class="input-group">
              <label>Card Number</label>
              <input type="text" placeholder="xxxx xxxx xxxx 4569" class="form-input">
            </div>
            <div class="form-row-2">
              <div class="input-group">
                <label>Expiry Date</label>
                <input type="text" placeholder="Dec 2026" class="form-input">
              </div>
              <div class="input-group">
                <label>CVV</label>
                <input type="text" placeholder="000" class="form-input">
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="checkout-actions">
            <button class="btn-cancel" @click="$router.push('/catalogo')">Cancel</button>
            <button class="btn-order" @click="placeOrder">Order</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Estado
const loading = ref(true);
const cartItems = ref([]);
const cartId = ref(null);

// Computados
const totalItems = computed(() => {
  return cartItems.value.reduce((total, item) => total + item.cantidad, 0);
});

const subtotal = computed(() => {
  return cartItems.value.reduce((total, item) => total + (item.precio * item.cantidad), 0);
});

// Obtener el carrito
const fetchCart = async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    // Si no está logueado, redirigir a login
    router.push('/login');
    return;
  }

  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/carrito`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!res.ok) {
      let errTxt = "";
      try {
        const errorData = await res.json();
        errTxt = errorData.detail || JSON.stringify(errorData);
      } catch(e) {
        errTxt = `HTTP ${res.status}`;
      }
      alert(`Error crítico en Carrito: ${errTxt}`);
      throw new Error('Error al cargar el carrito');
    }
    const data = await res.json();
    cartId.value = data.carrito_id;
    // Agregamos un flag 'updating' local para manejar estados de carga por botón
    cartItems.value = data.items.map(i => ({ ...i, updating: false }));
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// Actualizar Cantidad (+ o -)
const updateQuantity = async (item, change) => {
  const newQuantity = item.cantidad + change;
  if (newQuantity < 1) return; // No puede bajar de 1. Para eliminar usar tacho de basura.

  const token = localStorage.getItem('token');
  item.updating = true;

  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/carrito/items/${item.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ cantidad: newQuantity })
    });

    if (res.ok) {
      item.cantidad = newQuantity;
    } else {
      console.error("No se pudo actualizar la cantidad");
    }
  } catch (error) {
    console.error("Error validando el cambio de cantidad:", error);
  } finally {
    item.updating = false;
  }
};

// Remover del carrito
const removeItem = async (itemId) => {
  const token = localStorage.getItem('token');
  const targetItem = cartItems.value.find(i => i.id === itemId);
  if (targetItem) targetItem.updating = true;

  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/carrito/items/${itemId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (res.ok) {
      cartItems.value = cartItems.value.filter(i => i.id !== itemId);
    }
  } catch (error) {
    console.error("Error al eliminar item del carrito:", error);
    if (targetItem) targetItem.updating = false;
  }
};

// Procesar Orden (Mockup)
const placeOrder = () => {
  alert("Procesando tu orden...");
  // Aquí se enviaría el pago y los datos a la DB.
};

onMounted(() => {
  fetchCart();
});
</script>

<style scoped>
/* Contenedor Principal */
.cart-page-container {
  max-width: 1300px;
  margin: 60px auto;
  padding: 0 20px;
  font-family: 'Inter', sans-serif;
  color: #1a1a1a;
}

/* Manejo de Estados * Vacío o Cargando */
.loading-state, .empty-state {
  text-align: center;
  padding: 100px 20px;
}

.empty-state h2 {
  font-size: 2rem;
  color: #3d1520;
  margin-bottom: 10px;
}
.empty-state p {
  color: #666;
  margin-bottom: 24px;
}

/* Layout General: Dos Columnas */
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 450px;
  gap: 50px;
  align-items: flex-start;
}

/* TITULOS COMUNES */
.section-title {
  font-size: 1.4rem;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 30px;
}

/* =======================================================
   COLUMNA IZQUIERDA: ORDER SUMMARY
======================================================== */
.items-list {
  display: flex;
  flex-direction: column;
}

.cart-item {
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 20px;
  padding: 24px 0;
  border-bottom: 1px solid #eee;
  align-items: center;
}
.cart-item:first-child {
  border-top: 1px solid #eee;
}

.item-img-wrapper {
  width: 100px;
  height: 100px;
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.item-img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.item-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.item-type {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0;
}
.item-type span {
  font-weight: 500;
  color: #dc2626;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 30px;
}

.item-price {
  font-weight: 600;
  font-size: 1.1rem;
  min-width: 80px;
  text-align: right;
  margin: 0;
}

.qty-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.qty-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.qty-btn:hover {
  background: #f3f4f6;
  color: #1a1a1a;
}
.qty-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-display {
  font-weight: 600;
  font-size: 1rem;
  min-width: 20px;
  text-align: center;
}

.remove-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.remove-btn:hover {
  opacity: 1;
}

/* Agregar Cupon (Estilo Mockup) */
.coupon-section {
  margin-top: 30px;
}

.btn-coupon {
  width: 100%;
  padding: 18px;
  background: #111827;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-coupon:hover {
  background: #1f2937;
}

/* =======================================================
   COLUMNA DERECHA: SHOPPING CART (CHECKOUT)
======================================================== */
.checkout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.item-count-badge {
  font-size: 0.9rem;
  color: #6b7280;
}

.price-summary {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 30px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  color: #6b7280;
}
.price-row strong {
  color: #1a1a1a;
  font-weight: 600;
}

.total-row {
  font-size: 1.2rem;
  color: #1a1a1a;
  margin-top: 8px;
}

/* Checkout Forms */
.checkout-forms {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
}

.form-input {
  padding: 14px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #1a1a1a;
  background: #f9fafb;
  outline: none;
  transition: all 0.2s;
}
.form-input:focus {
  border-color: #4f46e5;
  background: white;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Payments Radio */
.payment-section {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.payment-section > label {
  font-size: 0.8rem;
  color: #1a1a1a;
  font-weight: 600;
}

.payment-options {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.payment-radio {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
  background: white;
  transition: background 0.2s;
}
.payment-radio:last-child {
  border-bottom: none;
}
.payment-radio.selected {
  background: #f8faff;
}
.payment-radio input[type="radio"] {
  accent-color: #4f46e5;
  width: 16px;
  height: 16px;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

/* Acciones Finales */
.checkout-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 30px;
}

.btn-cancel, .btn-order {
  padding: 16px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  border: none;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f3f4f6;
  color: #4b5563;
}
.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-order {
  background: #4f46e5;
  color: white;
  box-shadow: 0 4px 6px rgba(79, 70, 229, 0.2);
}
.btn-order:hover {
  background: #4338ca;
  box-shadow: 0 6px 12px rgba(79, 70, 229, 0.3);
  transform: translateY(-1px);
}

/* Boton Primario Generico */
.btn-primary {
  display: inline-block;
  padding: 12px 24px;
  background: #9e6070;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: opacity 0.2s;
}
.btn-primary:hover {
  opacity: 0.9;
}

/* =======================================================
   RESPONSIVO
======================================================== */
@media (max-width: 1024px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .cart-item {
    grid-template-columns: 80px 1fr;
  }
  .item-actions {
    grid-column: 1 / -1;
    justify-content: space-between;
    margin-top: 10px;
  }
}
</style>
