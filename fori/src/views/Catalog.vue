<template>
  <div class="pos-dashboard">
    <div class="header">
      <div class="greeting">
        <h1>Nuestro Catálogo de Flores 🌸</h1>
        <p>Encuentra el arreglo perfecto para cualquier ocasión.</p>
      </div>
    </div>

    <div class="catalog-layout">
      <!-- Barra lateral de Filtros Adicionales -->
      <aside class="filters-sidebar">
        <div class="filter-group">
          <h3>Categorías</h3>
          <div class="category-list">
            <button 
              class="sidebar-cat-btn" 
              :class="{ active: selectedCategory === null }"
              @click="selectCategory(null, null)"
            >
              <span class="cat-name">Todos</span>
              <span class="cat-badge">{{ totalStock }}</span>
            </button>
            <button 
              v-for="cat in categorias" 
              :key="cat.id"
              class="sidebar-cat-btn"
              :class="{ active: selectedCategory === cat.id }"
              @click="selectCategory(cat.id, cat.nombre)"
            >
              <span class="cat-name">{{ cat.nombre }}</span>
              <span class="cat-badge">{{ getCategoryStock(cat.id) }}</span>
            </button>
          </div>
        </div>

        <div class="filter-group">
          <h3>Disponibilidad</h3>
          <label class="custom-checkbox">
            <input type="checkbox" v-model="onlyInStock" />
            <span class="checkmark"></span>
            En stock
          </label>
        </div>

        <div class="filter-group">
          <h3>Precio</h3>
          <div class="radio-options">
            <label class="custom-radio">
              <input type="radio" value="under500" v-model="priceRange" />
              <span class="radio-mark"></span>
              Hasta $ 500
            </label>
            <label class="custom-radio">
              <input type="radio" value="500to1000" v-model="priceRange" />
              <span class="radio-mark"></span>
              $ 500 a $ 1000
            </label>
            <label class="custom-radio">
              <input type="radio" value="1000to1500" v-model="priceRange" />
              <span class="radio-mark"></span>
              $ 1000 a $ 1500
            </label>
            <label class="custom-radio">
              <input type="radio" value="1500to2000" v-model="priceRange" />
              <span class="radio-mark"></span>
              $ 1500 a $ 2000
            </label>
            <label class="custom-radio">
              <input type="radio" value="over2000" v-model="priceRange" />
              <span class="radio-mark"></span>
              Más de $ 2000
            </label>
            <label class="custom-radio">
              <input type="radio" value="custom" v-model="priceRange" />
              <span class="radio-mark"></span>
              Personalizado
            </label>
          </div>
          
          <div class="custom-price-inputs" v-if="priceRange === 'custom'">
            <input type="number" placeholder="Mínimo" v-model="minPrice" />
            <span>—</span>
            <input type="number" placeholder="Máximo" v-model="maxPrice" />
          </div>
        </div>
        
        <button class="clear-filters" @click="clearFilters" v-if="hasActiveFilters">
          Limpiar filtros
        </button>
      </aside>

      <div class="products-section">
        <div class="section-header">
          <h2>Explorar Productos</h2>
        </div>

        <!-- Cuadrícula de flores -->
        <div class="products-grid">
          <router-link
            class="product-card" 
            v-for="flor in filteredFlores" 
            :key="flor.id"
            :to="'/producto/' + flor.id"
          >
            <div class="img-container">
              <!-- Renderizamos imagen base64 o placeholder -->
              <img 
                v-if="flor.imagen_url && flor.imagen_url.startsWith('data:image')" 
                :src="flor.imagen_url" 
                :alt="flor.nombre" 
              />
              <div 
                v-else-if="flor.imagen_url"
                class="placeholder-img"
                :style="{ backgroundImage: 'url(' + flor.imagen_url + ')', backgroundSize: 'cover', backgroundPosition: 'center' }"
              ></div>
              <div v-else class="placeholder-img fallback-icon">
                🌸
              </div>
            </div>
            <div class="card-info">
              <h3 class="prod-title">{{ flor.nombre }}</h3>
              <p class="prod-code">Código: 12546{{ flor.id }}</p>
              <p class="prod-stock">Disponible: {{ flor.stock }}</p>
              
              <div class="price-row">
                <span class="price">${{ Number(flor.precio).toFixed(2) }}</span>
                <button class="add-btn" :disabled="flor.stock <= 0">
                  <span class="plus-icon">+</span>
                </button>
              </div>
            </div>
          </router-link>
          
          <div v-if="filteredFlores.length === 0" class="empty-state">
            <p>No hay flores que coincidan con tus filtros.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const flores = ref([]);
const categorias = ref([]);
const selectedCategory = ref(null);
const priceRange = ref(null);
const minPrice = ref('');
const maxPrice = ref('');
const onlyInStock = ref(false);

const hasActiveFilters = computed(() => {
    return priceRange.value !== null || onlyInStock.value || minPrice.value !== '' || maxPrice.value !== '';
});

const clearFilters = () => {
    priceRange.value = null;
    minPrice.value = '';
    maxPrice.value = '';
    onlyInStock.value = false;
};

// ... Apply category from query is fine

// ... ApplyCategoryFromQuery and selectCategory logic is untouched

const applyCategoryFromQuery = () => {
    const catQuery = route.query.cat;
    if (catQuery && categorias.value.length > 0) {
        // Find category ID by name
        const cat = categorias.value.find(c => c.nombre.toLowerCase() === catQuery.toLowerCase());
        if (cat) {
            selectedCategory.value = cat.id;
        } else {
            selectedCategory.value = null;
        }
    } else if (!catQuery) {
        selectedCategory.value = null;
    }
}

const selectCategory = (catId, catNombre) => {
    selectedCategory.value = catId;
    // Update the URL to reflect the local state
    if (catId === null) {
         router.push({ path: '/catalogo' });
    } else {
         router.push({ path: '/catalogo', query: { cat: catNombre } });
    }
}

const cargarDatos = async () => {
    try {
        // Obtenemos los datos directos del backend de FastAPI
        const resCategorias = await fetch('http://localhost:8000/api/categorias');
        categorias.value = await resCategorias.json();

        const resFlores = await fetch('http://localhost:8000/api/flores');
        flores.value = await resFlores.json();

        // Apply initially mapped category
        applyCategoryFromQuery();

    } catch (e) {
        console.error("Error al cargar datos desde el backend:", e);
    }
}

watch(() => route.query.cat, () => {
    applyCategoryFromQuery();
});

const totalStock = computed(() => {
    return flores.value.reduce((acc, flor) => acc + flor.stock, 0);
});

const getCategoryStock = (catId) => {
    return flores.value
      .filter(f => f.categoria_id === catId)
      .reduce((acc, flor) => acc + flor.stock, 0);
}

const filteredFlores = computed(() => {
    let result = flores.value;

    // Filter by Category
    if (selectedCategory.value !== null) {
        result = result.filter(f => f.categoria_id === selectedCategory.value);
    }

    // Filter by Stock
    if (onlyInStock.value) {
        result = result.filter(f => f.stock > 0);
    }

    // Filter by Price Range
    if (priceRange.value === 'under500') {
        result = result.filter(f => f.precio <= 500);
    } else if (priceRange.value === '500to1000') {
        result = result.filter(f => f.precio > 500 && f.precio <= 1000);
    } else if (priceRange.value === '1000to1500') {
        result = result.filter(f => f.precio > 1000 && f.precio <= 1500);
    } else if (priceRange.value === '1500to2000') {
        result = result.filter(f => f.precio > 1500 && f.precio <= 2000);
    } else if (priceRange.value === 'over2000') {
        result = result.filter(f => f.precio > 2000);
    } else if (priceRange.value === 'custom') {
        if (minPrice.value !== '' && minPrice.value !== null) {
            result = result.filter(f => f.precio >= Number(minPrice.value));
        }
        if (maxPrice.value !== '' && maxPrice.value !== null) {
            result = result.filter(f => f.precio <= Number(maxPrice.value));
        }
    }

    return result;
});

onMounted(() => {
    cargarDatos();
});

</script>

<style scoped>
.pos-dashboard {
  background-color: #E2E2E2; /* Fondo grisáceo claro de Figma */
  min-height: 100vh;
  padding: 40px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1A202C;
}

.header {
  margin-bottom: 30px;
}

.greeting h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.greeting p {
  color: #64748B;
  margin: 0;
  font-size: 14px;
}


.category-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-cat-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.sidebar-cat-btn:hover {
  background: #F1F5F9;
}

.sidebar-cat-btn.active {
  background: #0F172A;
}

.sidebar-cat-btn .cat-name {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
  margin-bottom: 0;
}

.sidebar-cat-btn.active .cat-name {
  color: white;
}

.sidebar-cat-btn .cat-badge {
  background: #E2E8F0;
  color: #475569;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.sidebar-cat-btn.active .cat-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.products-section {
  margin-top: 10px;
}

.section-header h2 {
  font-size: 18px;
  color: #1E293B;
  font-weight: 700;
  margin-bottom: 20px;
}

.products-grid {
  display: grid;
  /* Enforce exactly 5 cards per row on large screens */
  grid-template-columns: repeat(5, 1fr);
  gap: 25px;
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

.img-container {
  height: 260px;
  width: 100%;
  overflow: hidden;
  background-color: #F8FAFC;
  position: relative;
}

.img-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-img {
  width: 100%;
  height: 100%;
}

.fallback-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 5rem;
}

.card-info {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.prod-title {
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 600;
  color: #0F172A;
}

.prod-code, .prod-stock {
  margin: 0 0 4px 0;
  font-size: 12px;
  color: #64748B;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 15px;
}

.price {
  font-size: 18px;
  font-weight: 700;
  color: #0F172A;
}

.add-btn {
  background: #F1F5F9;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #0F172A;
  transition: background 0.2s;
}

.add-btn:hover:not(:disabled) {
  background: #E2E8F0;
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.plus-icon {
  font-size: 18px;
  font-weight: 500;
  line-height: 1;
  margin-top: -2px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: #64748B;
  background: white;
  border-radius: 16px;
}

/* Catalog Sidebar Layout */
.catalog-layout {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.filters-sidebar {
  width: 250px;
  flex-shrink: 0;
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.filter-group {
  margin-bottom: 24px;
}

.filter-group h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 15px;
}

/* Custom Checkbox and Radio styling */
.custom-checkbox, .custom-radio {
  display: block;
  position: relative;
  padding-left: 28px;
  margin-bottom: 12px;
  cursor: pointer;
  font-size: 14px;
  color: #475569;
  user-select: none;
}

.custom-checkbox input, .custom-radio input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark, .radio-mark {
  position: absolute;
  top: 0;
  left: 0;
  height: 18px;
  width: 18px;
  background-color: #F1F5F9;
  border: 1px solid #CBD5E1;
  border-radius: 4px;
  transition: all 0.2s;
}

.radio-mark {
  border-radius: 50%;
}

.custom-checkbox:hover input ~ .checkmark,
.custom-radio:hover input ~ .radio-mark {
  background-color: #E2E8F0;
}

.custom-checkbox input:checked ~ .checkmark,
.custom-radio input:checked ~ .radio-mark {
  background-color: #0F172A;
  border-color: #0F172A;
}

.checkmark:after, .radio-mark:after {
  content: "";
  position: absolute;
  display: none;
}

.custom-checkbox input:checked ~ .checkmark:after,
.custom-radio input:checked ~ .radio-mark:after {
  display: block;
}

.custom-checkbox .checkmark:after {
  left: 6px;
  top: 2px;
  width: 4px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-radio .radio-mark:after {
  top: 5px;
  left: 5px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
}

.custom-price-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 15px;
}

.custom-price-inputs input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.custom-price-inputs input:focus {
  border-color: #0F172A;
}

.custom-price-inputs span {
  color: #94A3B8;
}

.clear-filters {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid #E2E8F0;
  color: #64748B;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.clear-filters:hover {
  background: #F1F5F9;
  color: #0F172A;
}

.products-section {
  flex-grow: 1;
  margin-top: 0;
  min-width: 0; /* Prevents flex items from blowing out width */
}

/* Responsividad para la cuadrícula */
@media (max-width: 1400px) {
  .products-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1100px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 800px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
/* --- DARK MODE OVERRIDES (UNSCOPED FOR HIGHER SPECIFICITY & CSS SCOPE BYPASS) --- */
body.dark-theme .pos-dashboard { background-color: #121212 !important; color: #f1f5f9 !important; }
body.dark-theme .greeting h1 { color: #f8fafc !important; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }
body.dark-theme .greeting p { color: #94a3b8 !important; }
body.dark-theme .filters-sidebar { background: #1e1e1e !important; box-shadow: 0 4px 15px rgba(255,255,255,0.02) !important; border: 1px solid #333 !important; }
body.dark-theme .filter-group h3,
body.dark-theme .section-header h2 { color: #f8fafc !important; }
body.dark-theme .sidebar-cat-btn { color: #e2e8f0 !important; }
body.dark-theme .sidebar-cat-btn .cat-name { color: #cbd5e1 !important; }
body.dark-theme .sidebar-cat-btn:hover { background: #1e293b !important; }
body.dark-theme .sidebar-cat-btn.active { background: #38bdf8 !important; }
body.dark-theme .sidebar-cat-btn.active .cat-name { color: #0f172a !important; }
body.dark-theme .sidebar-cat-btn .cat-badge { background: #334155 !important; color: #f1f5f9 !important; }
body.dark-theme .sidebar-cat-btn.active .cat-badge { background: rgba(0,0,0,0.2) !important; color: #0f172a !important; }
body.dark-theme .custom-checkbox, body.dark-theme .custom-radio { color: #cbd5e1 !important; }
body.dark-theme .checkmark, body.dark-theme .radio-mark { background-color: #334155 !important; border-color: #475569 !important; }
body.dark-theme .custom-checkbox:hover input ~ .checkmark,
body.dark-theme .custom-radio:hover input ~ .radio-mark { background-color: #475569 !important; }
body.dark-theme .custom-checkbox input:checked ~ .checkmark,
body.dark-theme .custom-radio input:checked ~ .radio-mark { background-color: #38bdf8 !important; border-color: #38bdf8 !important; }
body.dark-theme .custom-price-inputs input { background: #1e1e1e !important; border-color: #475569 !important; color: #f1f5f9 !important; }
body.dark-theme .custom-price-inputs input:focus { border-color: #38bdf8 !important; }
body.dark-theme .clear-filters { border-color: #475569 !important; color: #94a3b8 !important; }
body.dark-theme .clear-filters:hover { background: #334155 !important; color: #f1f5f9 !important; border-color: #475569 !important; }
body.dark-theme .product-card { background: #1e1e1e !important; box-shadow: 0 4px 15px rgba(255,255,255,0.02) !important; border: 1px solid #333 !important; }
body.dark-theme .img-container { background-color: #111 !important; border-bottom: 1px solid #333 !important; }
body.dark-theme .prod-title { color: #f8fafc !important; }
body.dark-theme .prod-code, body.dark-theme .prod-stock { color: #94a3b8 !important; }
body.dark-theme .price { color: #f8fafc !important; }
body.dark-theme .add-btn { background: #334155 !important; color: #f8fafc !important; }
body.dark-theme .add-btn:hover:not(:disabled) { background: #475569 !important; }
body.dark-theme .empty-state { background: #1e1e1e !important; color: #94a3b8 !important; border: 1px solid #333 !important; }
</style>