<template>
  <div class="product-details-page">
    <div class="breadcrumb">
      <router-link to="/">Inicio</router-link>
      <span class="separator">/</span>
      <router-link to="/catalogo">Catálogo</router-link>
      <span class="separator">/</span>
      <span class="current">{{ flor ? flor.nombre : 'Cargando...' }}</span>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner">🌸</div>
      <p>Buscando flor en el jardín...</p>
    </div>
    
    <div v-else-if="flor" class="product-container">
      <!-- Sección Top: Imágenes e Info -->
      <div class="product-top-section">
        
        <!-- Galería Izquierda -->
        <div class="product-gallery">
          <div class="main-image">
            <img 
              v-if="currentImage && currentImage.startsWith('http') || currentImage.startsWith('data:image')" 
              :src="currentImage" 
              :alt="flor.nombre" 
            />
            <div 
              v-else-if="currentImage"
              class="placeholder-img"
              :style="{ backgroundImage: 'url(' + currentImage + ')', backgroundSize: 'cover', backgroundPosition: 'center' }"
            ></div>
            <div v-else class="placeholder-img fallback-icon">🌸</div>
          </div>
          <div class="thumbnail-list">
            <div 
              v-for="(img, index) in productImages" 
              :key="index"
              class="thumbnail"
              :class="{ active: currentImageIndex === index }"
              @click="currentImageIndex = index"
            >
              <img v-if="img" :src="img" :alt="'thumb' + (index + 1)"/>
              <div v-else class="fallback-icon">🌸</div>
            </div>
          </div>
        </div>

        <!-- Información Derecha -->
        <div class="product-info">
          <span class="product-category">{{ categoryName }}</span>
          
          <div class="title-row">
            <h1>{{ flor.nombre }}</h1>
            <span class="stock-badge" v-if="flor.stock > 0">En Stock</span>
            <span class="out-stock-badge" v-else>Agotado</span>
          </div>

          <div class="reviews-snippet">
            <div class="stars">⭐⭐⭐⭐⭐</div>
            <span class="rating-text">4.9 (245 Reseñas)</span>
          </div>

          <div class="price-section">
            <span class="current-price">${{ Number(flor.precio).toFixed(2) }}</span>
            <span class="original-price">${{ (Number(flor.precio) * 1.25).toFixed(2) }}</span>
          </div>

          <p class="short-description">
            {{ flor.descripcion_detallada ? flor.descripcion_detallada.substring(0, 150) + '...' : 'Un hermoso arreglo cuidadosamente seleccionado. Perfecto para demostrar tu cariño, con flores frescas del día que llenarán cualquier espacio de color y alegría.' }}
          </p>

          <!-- Opciones de Tamaño -->
          <div class="options-group">
            <h3>Tamaño</h3>
            <div class="size-options">
              <button 
                class="size-card" 
                :class="{ active: selectedSize === 'standard' }"
                @click="selectedSize = 'standard'"
              >
                <div class="size-icon">💐</div>
                <div class="size-name">Estándar</div>
                <div class="size-price">+$0.00</div>
              </button>
              <button 
                class="size-card" 
                :class="{ active: selectedSize === 'deluxe' }"
                @click="selectedSize = 'deluxe'"
              >
                <div class="size-icon deluxe">💐</div>
                <div class="size-name">Deluxe</div>
                <div class="size-price">+$150.00</div>
              </button>
              <button 
                class="size-card" 
                :class="{ active: selectedSize === 'premium' }"
                @click="selectedSize = 'premium'"
              >
                <div class="size-icon premium">💐</div>
                <div class="size-name">Premium</div>
                <div class="size-price">+$250.00</div>
              </button>
            </div>
          </div>

          <!-- Selección de Color -->
          <div class="options-group">
            <h3>Color Principal: <span>{{ selectedColor }}</span></h3>
            <div class="color-options">
              <button 
                class="color-circle" 
                style="background-color: #c4536a;"
                :class="{ active: selectedColor === 'Rosa' }"
                @click="selectedColor = 'Rosa'"
              ></button>
              <button 
                class="color-circle" 
                style="background-color: #fdf6f7; border: 1px solid #ddd;"
                :class="{ active: selectedColor === 'Blanco' }"
                @click="selectedColor = 'Blanco'"
              ></button>
              <button 
                class="color-circle" 
                style="background-color: #d11234;"
                :class="{ active: selectedColor === 'Rojo Intenso' }"
                @click="selectedColor = 'Rojo Intenso'"
              ></button>
            </div>
          </div>

          <!-- Mensaje de Tarjeta -->
          <div class="options-group">
            <h3>Mensaje para Tarjeta</h3>
            <textarea 
              v-model="cardMessage" 
              placeholder="Escribe un mensaje especial..." 
              rows="3"
            ></textarea>
          </div>

          <!-- Acciones de Compra -->
          <div class="action-row">
            <div class="quantity-selector">
              <button @click="quantity > 1 ? quantity-- : null">-</button>
              <input type="number" v-model="quantity" min="1" :max="flor.stock" readonly>
              <button @click="quantity < flor.stock ? quantity++ : null">+</button>
            </div>
            
            <button class="add-to-cart-btn" :disabled="flor.stock === 0 || addingToCart" @click="addToCart">
              {{ addingToCart ? 'Agregando...' : 'Agregar al Carrito' }}
            </button>
            
            <button class="buy-now-btn" :disabled="flor.stock === 0">
              Comprar Ahora
            </button>

            <button class="wishlist-btn">
              ♡
            </button>
          </div>

          <!-- Meta (SKU, Tags, Share) -->
          <div class="product-meta">
            <div class="meta-item">
              <span class="meta-label">SKU:</span>
              <span class="meta-value">{{ flor.sku || 'N/A' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Tags:</span>
              <span class="meta-value">{{ flor.tags ? flor.tags : categoryName + ', Arreglos, Flores' }}</span>
            </div>
            <div class="meta-item share">
              <span class="meta-label">Compartir:</span>
              <div class="share-icons">
                <span class="icon">📘</span>
                <span class="icon">📸</span>
                <span class="icon">📌</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Sección Inferior: Tabs -->
      <div class="product-bottom-section">
        <div class="tabs-header">
          <button 
            :class="{ active: activeTab === 'description' }"
            @click="activeTab = 'description'"
          >Descripción</button>
          <button 
            :class="{ active: activeTab === 'additional' }"
            @click="activeTab = 'additional'"
          >Información Adicional</button>
          <button 
            :class="{ active: activeTab === 'reviews' }"
            @click="activeTab = 'reviews'"
          >Reseñas</button>
        </div>
        
        <div class="tab-content">
          <div v-if="activeTab === 'description'" class="tab-pane">
            <p v-if="flor.descripcion_detallada">{{ flor.descripcion_detallada }}</p>
            <div v-else>
                <p>No hay descripción detallada disponible para este producto.</p>
            </div>
          </div>
          
          <div v-if="activeTab === 'additional'" class="tab-pane">
            <div v-if="flor.recomendaciones">
              <p style="white-space: pre-line;">{{ flor.recomendaciones }}</p>
            </div>
            <ul v-else>
              <li><strong>Cuidados:</strong> Mantener en lugar fresco, cambiar agua cada 2 días.</li>
              <li><strong>Información:</strong> Contacte a soporte para medidas específicas.</li>
            </ul>
          </div>
          
          <div v-if="activeTab === 'reviews'" class="tab-pane reviews-pane">
            <div class="reviews-summary">
              <div class="score-box">
                <div class="big-score">4.9 <span class="out-of">de 5</span></div>
                <div class="stars">⭐⭐⭐⭐⭐</div>
                <div class="total-reviews">(245 Reseñas)</div>
              </div>
              <div class="progress-bars">
                <div class="bar-row"><span class="star-label">5 Estrellas</span><div class="bar-bg"><div class="bar-fill" style="width: 85%;"></div></div></div>
                <div class="bar-row"><span class="star-label">4 Estrellas</span><div class="bar-bg"><div class="bar-fill" style="width: 10%;"></div></div></div>
                <div class="bar-row"><span class="star-label">3 Estrellas</span><div class="bar-bg"><div class="bar-fill" style="width: 3%;"></div></div></div>
                <div class="bar-row"><span class="star-label">2 Estrellas</span><div class="bar-bg"><div class="bar-fill" style="width: 1%;"></div></div></div>
                <div class="bar-row"><span class="star-label">1 Estrella</span><div class="bar-bg"><div class="bar-fill" style="width: 1%;"></div></div></div>
              </div>
            </div>

            <div class="reviews-list">
              <div class="reviews-header">
                <h3>Lista de Reseñas <span class="count">Mostrando 1-2 de 245 resultados</span></h3>
                <div class="sort-dropdown">
                  Ordenar por: <select><option>Más Recientes</option><option>Mejores</option></select>
                </div>
              </div>

              <!-- Comentario Falso 1 -->
              <div class="review-item">
                <div class="review-user">
                  <div class="avatar">KW</div>
                  <div class="user-info">
                    <h4>Kristin Watson <span class="verified">(Comprador Verificado)</span></h4>
                    <span class="date">hace 1 mes</span>
                  </div>
                </div>
                <div class="review-content">
                  <h5>¡Perfecto para Cumpleaños y Aniversarios!</h5>
                  <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                  <div class="stars">⭐⭐⭐⭐⭐ 5.0</div>
                  <div class="review-images">
                    <div class="rev-img-box"><div class="fallback-icon">🌸</div></div>
                    <div class="rev-img-box"><div class="fallback-icon">🌸</div></div>
                    <div class="rev-img-box"><div class="fallback-icon">🌸</div></div>
                  </div>
                </div>
              </div>

              <!-- Comentario Falso 2 -->
              <div class="review-item">
                <div class="review-user">
                  <div class="avatar" style="background: #9e2a3e;">JW</div>
                  <div class="user-info">
                    <h4>Jenny Wilson <span class="verified">(Comprador Verificado)</span></h4>
                    <span class="date">hace 2 meses</span>
                  </div>
                </div>
                <div class="review-content">
                  <h5>¡El Ramo más hermoso de todos!</h5>
                  <p>Muy fresco y duró muchísimo tiempo en casa.</p>
                  <div class="stars">⭐⭐⭐⭐⭐ 5.0</div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="error-state">
      <h2>¡Ups!</h2>
      <p>No pudimos encontrar el detalle de esta flor.</p>
      <button @click="$router.push('/catalogo')" class="btn-return">Regresar al Catálogo</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const flor = ref(null);
const loading = ref(true);
const categorias = ref([]);

// UI State
const selectedSize = ref('standard');
const selectedColor = ref('Rosa');
const cardMessage = ref('');
const quantity = ref(1);
const activeTab = ref('reviews');
const currentImageIndex = ref(0);
const addingToCart = ref(false);

// Product logic
const productImages = computed(() => {
    if (!flor.value) return [];
    
    // Check if the backend gave us extra images
    if (flor.value.imagenes_extra) {
        let extras = [];
        try {
            // It might come as a stringified JSON array or directly as an array from FastAPI
            extras = typeof flor.value.imagenes_extra === 'string' 
                ? JSON.parse(flor.value.imagenes_extra) 
                : flor.value.imagenes_extra;
        } catch(e) {
            console.error("Error parsing imagenes_extra", e);
        }
        
        if (Array.isArray(extras) && extras.length > 0) {
            return extras;
        }
    }
    
    // Fallback exactly to the single main image if no extras were uploaded
    if (flor.value.imagen_url) {
        return [flor.value.imagen_url];
    }
    
    return [];
});

const currentImage = computed(() => {
    return productImages.value[currentImageIndex.value] || null;
});

const categoryName = computed(() => {
    if (!flor.value || categorias.value.length === 0) return 'Flores';
    const cat = categorias.value.find(c => c.id === flor.value.categoria_id);
    return cat ? cat.nombre : 'Flores';
});

const loadInitialData = async () => {
    try {
        const id = route.params.id;
        
        // Fetch Categories first to map the ID
        const resCat = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/categorias`);
        categorias.value = await resCat.json();

        // Fetch Product Details
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/flores/${id}`);
        if(res.ok) {
            flor.value = await res.json();
            // Default selected color can be based on category or name if smart enough, 
            // for now just 'Rosa'.
        } else {
            flor.value = null; // not found
        }
    } catch (e) {
        console.error("Error cargando flor:", e);
        flor.value = null;
    } finally {
        loading.value = false;
    }
}

const addToCart = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
        alert("¡Hola! Necesitas iniciar sesión para armar tu carrito 🌸");
        router.push('/login');
        return;
    }

    addingToCart.value = true;
    try {
        const payload = {
            flor_id: flor.value.id,
            cantidad: quantity.value
        };

        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')}/api/user/carrito/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert("¡Flor(es) agregada(s) a tu carrito exitosamente! 🛒");
        } else {
            const errData = await res.json();
            alert("Error: " + (errData.detail || "No pudimos agregar la flor al carrito"));
        }
    } catch (e) {
        console.error("Error al agregar al carrito:", e);
        alert("Error de conexión al agregar al carrito");
    } finally {
        addingToCart.value = false;
    }
};

onMounted(() => {
    loadInitialData();
});
</script>

<style scoped>
.product-details-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px 60px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text-dark, #333);
}

.breadcrumb {
  margin-bottom: 30px;
  font-size: 0.9rem;
  color: var(--text-soft, #666);
}
.breadcrumb a {
  color: var(--text-soft, #666);
  text-decoration: none;
  transition: color 0.2s;
}
.breadcrumb a:hover { color: var(--accent-pink, #c4536a); }
.breadcrumb .separator { margin: 0 8px; color: #ccc; }
.breadcrumb .current { color: var(--accent-pink, #c4536a); font-weight: 500; }

.loading-state, .error-state {
  text-align: center;
  padding: 100px 20px;
}
.spinner { font-size: 3rem; animation: spin 2s linear infinite; margin-bottom: 20px; display: inline-block; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.btn-return { margin-top: 20px; padding: 10px 20px; background: var(--accent-pink, #c4536a); color: white; border: none; border-radius: 8px; cursor: pointer; }

/* ─── TOP SECTION: GALLERY + INFO ─── */
.product-top-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
  margin-bottom: 60px;
}

@media (min-width: 900px) {
  .product-top-section { grid-template-columns: 1fr 1fr; gap: 60px; }
}

/* Galería */
.product-gallery { display: flex; flex-direction: column; gap: 15px; }
.main-image {
  background: var(--bg-creme-light, #fdf8f9);
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  display: flex; align-items: center; justify-content: center;
}
.main-image img, .placeholder-img { width: 100%; height: 100%; object-fit: cover; }
.fallback-icon { font-size: 4rem; color: var(--accent-pink, #c4536a); opacity: 0.5; }

.thumbnail-list { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.thumbnail {
  aspect-ratio: 1 / 1;
  background: var(--bg-creme-light, #fdf8f9);
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  border: 2px solid transparent;
  display: flex; align-items: center; justify-content: center;
}
.thumbnail.active { border-color: var(--accent-pink, #c4536a); }
.thumbnail img { width: 100%; height: 100%; object-fit: cover; }

/* Product Info */
.product-category { font-size: 0.85rem; color: var(--text-soft, #666); text-transform: uppercase; letter-spacing: 1px; }

.title-row { display: flex; align-items: center; gap: 15px; margin: 8px 0; }
.title-row h1 { font-size: 2rem; font-family: 'Playfair Display', serif; margin: 0; color: #1E293B; }
.stock-badge { background: #Edf7ed; color: #1e4620; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.out-stock-badge { background: #fdeded; color: #5f2120; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

.reviews-snippet { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; font-size: 0.9rem; }
.rating-text { color: var(--text-soft, #666); }

.price-section { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
.current-price { font-size: 1.8rem; font-weight: 700; color: #1E293B; }
.original-price { font-size: 1.2rem; color: #94A3B8; text-decoration: line-through; }

.short-description { color: #4b5563; line-height: 1.6; margin-bottom: 30px; }

.options-group { margin-bottom: 25px; }
.options-group h3 { font-size: 1rem; font-weight: 600; margin-bottom: 15px; color: #1E293B; }
.options-group h3 span { color: var(--accent-pink, #c4536a); font-weight: 500; }

.size-options { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.size-card {
  background: white; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 15px 10px;
  text-align: center; cursor: pointer; transition: all 0.2s; display: flex; flex-direction: column; align-items: center; gap: 5px;
}
.size-card:hover { border-color: #cbd5e1; background: #f8fafc; }
.size-card.active { border-color: var(--accent-pink, #c4536a); background: var(--bg-creme-light, #fdf8f9); }
.size-icon { font-size: 1.5rem; opacity: 0.7; }
.size-icon.deluxe { font-size: 1.8rem; opacity: 0.85; }
.size-icon.premium { font-size: 2.1rem; opacity: 1; }
.size-name { font-weight: 600; font-size: 0.9rem; color: #334155; }
.size-price { font-size: 0.8rem; color: var(--text-soft, #64748b); }
.size-card.active .size-name, .size-card.active .size-price { color: var(--accent-pink, #c4536a); }

.color-options { display: flex; gap: 12px; }
.color-circle {
  width: 30px; height: 30px; border-radius: 50%; border: none; cursor: pointer; padding: 0; outline: none; transition: transform 0.2s;
}
.color-circle:hover { transform: scale(1.1); }
.color-circle.active { box-shadow: 0 0 0 3px white, 0 0 0 5px var(--accent-pink, #c4536a); }

textarea {
  width: 100%; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 12px; font-family: inherit; font-size: 0.9rem; resize: vertical; outline: none; transition: border-color 0.2s; background: #f8fafc;
}
textarea:focus { border-color: var(--accent-pink, #c4536a); background: white; }

.action-row { display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
.quantity-selector {
  display: flex; align-items: center; border: 1.5px solid #e2e8f0; border-radius: 25px; overflow: hidden; height: 48px; background: white;
}
.quantity-selector button {
  background: transparent; border: none; padding: 0 15px; font-size: 1.2rem; cursor: pointer; color: #475569;
}
.quantity-selector input {
  width: 40px; border: none; text-align: center; font-weight: 600; font-size: 1rem; color: #1e293b; background: transparent; outline: none; pointer-events: none;
}

.add-to-cart-btn {
  background: var(--primary-pink, #821f35); color: white; border: none; border-radius: 25px; padding: 0 30px; height: 48px; font-weight: 600; cursor: pointer; font-size: 1rem; flex-grow: 1; transition: background 0.2s;
}
.add-to-cart-btn:hover { background: #6b1a2a; }
.buy-now-btn {
  background: var(--bg-creme, #f48fb1); color: white; border: none; border-radius: 25px; padding: 0 20px; height: 48px; font-weight: 600; cursor: pointer; transition: filter 0.2s;
}
.buy-now-btn:hover { filter: brightness(0.9); }
.wishlist-btn {
  width: 48px; height: 48px; border-radius: 50%; border: 1.5px solid #e2e8f0; background: white; color: #64748b; font-size: 1.4rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.wishlist-btn:hover { border-color: var(--accent-pink, #c4536a); color: var(--accent-pink, #c4536a); }
button:disabled { opacity: 0.5; cursor: not-allowed; }

.product-meta { border-top: 1px solid #e2e8f0; padding-top: 20px; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; }
.meta-item { display: flex; align-items: center; gap: 10px; }
.meta-label { color: #0F172A; font-weight: 600; width: 80px; }
.meta-value { color: #64748B; }
.share-icons { display: flex; gap: 10px; }
.share-icons .icon { width: 30px; height: 30px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.8rem; }
.share-icons .icon:hover { background: var(--bg-creme-light, #fdf8f9); }


/* ─── BOTTOM SECTION: TABS ─── */
.product-bottom-section { margin-top: 20px; border-top: 1px solid #e2e8f0; padding-top: 40px; }
.tabs-header { display: flex; justify-content: center; gap: 40px; border-bottom: 2px solid #e2e8f0; margin-bottom: 40px; }
.tabs-header button {
  background: transparent; border: none; padding: 0 0 15px 0; font-size: 1.1rem; font-weight: 600; color: #94A3B8; cursor: pointer; position: relative;
}
.tabs-header button.active { color: var(--accent-pink, #c4536a); }
.tabs-header button.active::after {
  content: ''; position: absolute; bottom: -2px; left: 0; width: 100%; height: 3px; background: var(--accent-pink, #c4536a); border-radius: 3px 3px 0 0;
}

.tab-content { max-width: 900px; margin: 0 auto; color: #475569; line-height: 1.7; }
.tab-pane p { margin-bottom: 20px; }
.tab-pane ul { margin-left: 20px; margin-bottom: 20px; }

/* Reseñas Tab */
.reviews-summary {
  display: flex; gap: 60px; align-items: center; margin-bottom: 50px; flex-wrap: wrap;
}
.score-box { display: flex; flex-direction: column; align-items: center; }
.big-score { font-size: 3.5rem; font-weight: 700; color: #1E293B; line-height: 1; margin-bottom: 5px; }
.out-of { font-size: 1rem; color: #64748B; font-weight: 400; }
.score-box .total-reviews { font-size: 0.85rem; color: #94A3B8; margin-top: 5px; }

.progress-bars { flex-grow: 1; min-width: 300px; display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 15px; }
.star-label { font-size: 0.85rem; color: #64748B; width: 70px; }
.bar-bg { flex-grow: 1; height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; background: #fbbf24; border-radius: 3px; }

.reviews-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid #f1f5f9; }
.reviews-header h3 { font-size: 1.2rem; margin: 0; color: #1E293B; }
.reviews-header .count { font-size: 0.85rem; color: #94A3B8; margin-left: 10px; font-weight: 400; }
.sort-dropdown select { border: none; background: transparent; color: #1E293B; font-weight: 600; outline: none; cursor: pointer; }

.review-item { margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px dashed #e2e8f0; }
.review-user { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
.avatar { width: 45px; height: 45px; border-radius: 50%; background: var(--bg-creme, #f48fb1); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem; }
.review-user h4 { margin: 0; font-size: 1rem; color: #1E293B; }
.verified { color: #64748B; font-weight: 400; font-size: 0.8rem; }
.review-user .date { font-size: 0.85rem; color: #94A3B8; }

.review-content h5 { margin: 0 0 10px 0; font-size: 1.05rem; color: #1E293B; }
.review-content p { margin: 0 0 15px 0; font-size: 0.95rem; }
.review-content .stars { font-size: 0.9rem; color: #fbbf24; margin-bottom: 15px; font-weight: 600; }
.review-images { display: flex; gap: 10px; }
.rev-img-box { width: 80px; height: 80px; border-radius: 8px; background: #fdf8f9; display: flex; align-items: center; justify-content: center; overflow: hidden; }

/* Responsive adjustments */
@media (max-width: 600px) {
  .tabs-header { gap: 15px; flex-wrap: wrap; justify-content: flex-start; }
  .tabs-header button { font-size: 0.95rem; }
  .reviews-summary { gap: 30px; }
}

/* DARK THEME SUPPORT */
body.dark-theme .product-details-page { color: #f1f5f9; }
body.dark-theme .breadcrumb a { color: #94a3b8; }
body.dark-theme .breadcrumb a:hover { color: var(--accent-pink, #f48fb1); }
body.dark-theme .breadcrumb .current { color: var(--accent-pink, #f48fb1); }
body.dark-theme .title-row h1, body.dark-theme .current-price, body.dark-theme .options-group h3 { color: #f8fafc; }
body.dark-theme .main-image, body.dark-theme .thumbnail, body.dark-theme .rev-img-box { background: #111; }
body.dark-theme .size-card { background: #1e1e1e; border-color: #333; }
body.dark-theme .size-card:hover { background: #2a2a2a; }
body.dark-theme .size-card.active { background: #3a2a2f; border-color: var(--accent-pink, #f48fb1); }
body.dark-theme .size-name { color: #e2e8f0; }
body.dark-theme .quantity-selector { background: #1e1e1e; border-color: #333; }
body.dark-theme .quantity-selector input, body.dark-theme .quantity-selector button { color: #f1f5f9; }
body.dark-theme .wishlist-btn { background: #1e1e1e; border-color: #333; color: #cbd5e1; }
body.dark-theme textarea { background: #1e1e1e; border-color: #333; color: #f1f5f9; }
body.dark-theme textarea:focus { border-color: var(--accent-pink, #f48fb1); background: #222; }
body.dark-theme .big-score, body.dark-theme .reviews-header h3, body.dark-theme .review-user h4, body.dark-theme .review-content h5 { color: #f8fafc; }
body.dark-theme .bar-bg { background: #333; }
body.dark-theme .meta-label { color: #e2e8f0; }
body.dark-theme .share-icons .icon { background: #333; }
body.dark-theme .tabs-header button { color: #64748b; }
body.dark-theme .tabs-header button.active { color: var(--accent-pink, #f48fb1); }
body.dark-theme .tabs-header button.active::after { background: var(--accent-pink, #f48fb1); }
body.dark-theme .tab-pane, body.dark-theme .short-description { color: #cbd5e1; }
body.dark-theme .review-item { border-color: #333; }
body.dark-theme .sort-dropdown select { color: #e2e8f0; }
body.dark-theme .sort-dropdown select option { background: #1e1e1e; }
body.dark-theme .add-to-cart-btn { background: var(--accent-pink, #f48fb1); color: #1e1e1e; }
</style>
