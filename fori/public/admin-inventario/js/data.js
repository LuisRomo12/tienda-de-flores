// data.js: Manejo de Datos via API (PostgREST)
import { api } from './api.js';

export default class InventoryModel {
    constructor() {
        this.products = [];
        this.categorias = [];
        this.catMapNameId = {};
        this.catMapIdName = {};

        this.accessories = [];
        this.accCategorias = [];
        this.accCatMapNameId = {};
        this.accCatMapIdName = {};
    }

    // Método para inicializar y cargar la primera vez
    async loadData() {
        try {
            // Cargar categorías (Flores)
            this.categorias = await api.get('/categorias');
            this.categorias.forEach(c => {
                this.catMapNameId[c.nombre] = c.id;
                this.catMapIdName[c.id] = c.nombre;
            });
            // Cargar flores
            await this.fetchProducts();

            // Cargar categorías (Accesorios)
            this.accCategorias = await api.get('/accesorios_categorias');
            this.accCategorias.forEach(c => {
                this.accCatMapNameId[c.nombre] = c.id;
                this.accCatMapIdName[c.id] = c.nombre;
            });
            // Cargar accesorios
            await this.fetchAccessories();

        } catch (error) {
            console.error("Error cargando datos del inventario:", error);
        }
    }

    async fetchProducts() {
        const flores = await api.get('/flores');
        this.products = flores.map(f => ({
            id: f.id,
            nombre: f.nombre,
            categoria: this.catMapIdName[f.categoria_id] || 'Desconocida',
            categoria_id: f.categoria_id,
            precio: parseFloat(f.precio),
            stock: parseInt(f.stock),
            imagen: f.imagen_url, // Mapeamos de DB a UI para compatibilidad backwards
            sku: f.sku || '',
            tags: f.tags || '',
            descripcion_detallada: f.descripcion_detallada || '',
            recomendaciones: f.recomendaciones || '',
            imagenes_extra: f.imagenes_extra || []
        }));
    }

    getProducts() {
        return this.products;
    }

    async addProduct(product) {
        const catId = this.catMapNameId[product.categoria] || null; // Manejo básico si no existe, ideal ID
        const payload = {
            nombre: product.nombre,
            precio: parseFloat(product.precio),
            stock: parseInt(product.stock),
            categoria_id: catId,
            imagen_url: product.imagen_url || null,
            imagenes_extra: product.imagenes_extra || [],
            sku: product.sku || null,
            tags: product.tags || null,
            descripcion_detallada: product.descripcion_detallada || null,
            recomendaciones: product.recomendaciones || null
        };

        await api.post('/flores', payload);
        await this.fetchProducts(); // Refrescar lista final
        return true;
    }

    async editProduct(id, updatedData) {
        const payload = {};
        if (updatedData.nombre) payload.nombre = updatedData.nombre;
        if (updatedData.precio) payload.precio = parseFloat(updatedData.precio);
        if (updatedData.stock !== undefined) payload.stock = parseInt(updatedData.stock);
        if (updatedData.categoria) {
            payload.categoria_id = this.catMapNameId[updatedData.categoria] || null;
        }
        if (updatedData.imagen_url) {
            payload.imagen_url = updatedData.imagen_url;
        }
        if (updatedData.imagenes_extra) {
            payload.imagenes_extra = updatedData.imagenes_extra;
        }
        if (updatedData.sku !== undefined) payload.sku = updatedData.sku;
        if (updatedData.tags !== undefined) payload.tags = updatedData.tags;
        if (updatedData.descripcion_detallada !== undefined) payload.descripcion_detallada = updatedData.descripcion_detallada;
        if (updatedData.recomendaciones !== undefined) payload.recomendaciones = updatedData.recomendaciones;

        await api.patch(`/flores/${id}`, payload);
        await this.fetchProducts();
        return true;
    }

    async deleteProduct(id) {
        await api.delete(`/flores/${id}`);
        await this.fetchProducts(); // Refrescar lista final
        return true;
    }

    // ==========================================
    // MÉTODOS PARA ACCESORIOS
    // ==========================================

    async fetchAccessories() {
        const accesorios = await api.get('/accesorios');
        this.accessories = accesorios.map(a => ({
            id: a.id,
            nombre: a.nombre,
            categoria: this.accCatMapIdName[a.categoria_id] || 'Desconocida',
            categoria_id: a.categoria_id,
            precio: parseFloat(a.precio),
            stock: parseInt(a.stock),
            imagen: a.imagen_data || '',
            sku: a.sku || '',
            descripcion_detallada: a.descripcion || ''
        }));
    }

    getAccessories() {
        return this.accessories;
    }

    async addAccessory(accessory) {
        const catId = this.accCatMapNameId[accessory.categoria] || null;
        const payload = {
            nombre: accessory.nombre,
            precio: parseFloat(accessory.precio),
            stock: parseInt(accessory.stock),
            categoria_id: catId,
            imagen_data: accessory.imagen || null,
            sku: accessory.sku || null,
            descripcion: accessory.descripcion_detallada || null
        };

        await api.post('/accesorios', payload);
        await this.fetchAccessories();
        return true;
    }

    async editAccessory(id, updatedData) {
        const payload = {};
        if (updatedData.nombre) payload.nombre = updatedData.nombre;
        if (updatedData.precio) payload.precio = parseFloat(updatedData.precio);
        if (updatedData.stock !== undefined) payload.stock = parseInt(updatedData.stock);
        if (updatedData.categoria) {
            payload.categoria_id = this.accCatMapNameId[updatedData.categoria] || null;
        }
        if (updatedData.imagen) {
            payload.imagen_data = updatedData.imagen;
        }
        if (updatedData.sku !== undefined) payload.sku = updatedData.sku;
        if (updatedData.descripcion_detallada !== undefined) payload.descripcion = updatedData.descripcion_detallada;

        await api.patch(`/accesorios/${id}`, payload);
        await this.fetchAccessories();
        return true;
    }

    async deleteAccessory(id) {
        await api.delete(`/accesorios/${id}`);
        await this.fetchAccessories();
        return true;
    }

    // Filtros y Búsqueda sobre los datos ya cacheados en memoria
    filterProducts(searchTerm, category) {
        return this.products.filter(prod => {
            const matchesSearch = prod.nombre.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesCategory = category === 'all' || prod.categoria === category || !category;
            return matchesSearch && matchesCategory;
        });
    }

    filterAccessories(term, category) {
        if (!term && category === 'all') return this.accessories;

        const t = term.toLowerCase();
        return this.accessories.filter(a => {
            const matchesTerm = a.nombre.toLowerCase().includes(t);
            const matchesCat = category === 'all' || a.categoria === category;
            return matchesTerm && matchesCat;
        });
    }
}