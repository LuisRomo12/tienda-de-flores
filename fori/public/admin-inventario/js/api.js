// api.js: Cliente central para consumir la API de PostgREST

const BASE_HOST_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com';
const API_BASE_URL = `${BASE_HOST_URL}/api/admin`; // API en FastAPI
const TOKEN_KEY = 'admin_jwt_token';

class ApiClient {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    // Obtener token guardado
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    // Guardar token
    setToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    }

    // Eliminar token (Logout)
    clearToken() {
        localStorage.removeItem(TOKEN_KEY);
    }

    // Verificar si hay sesión activa
    isAuthenticated() {
        return !!this.getToken();
    }

    // Headers comunes, incluyendo autenticación si existe el token
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    // Manejo de errores común
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: response.statusText }));
            throw new Error(error.message || error.detail || 'Error en la petición a la API');
        }

        return response.json();
    }

    // --- MÉTODOS HTTP ---

    async get(endpoint) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // FastAPI devuelve la fila directamente
    async post(endpoint, body) {
        const headers = this.getHeaders();
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body)
        });
        return this.handleResponse(response);
    }

    async patch(endpoint, body) {
        const headers = this.getHeaders();
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify(body)
        });
        return this.handleResponse(response);
    }

    async delete(endpoint) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    // --- ENDPOINTS ESPECÍFICOS ---

    async loginAdmin(username, password) {
        const response = await fetch(`${BASE_HOST_URL}/api/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Error al iniciar sesión');
        }

        const data = await response.json();
        if (data.access_token) {
            this.setToken(data.access_token);
            if (data.role) localStorage.setItem('admin_role', data.role);
            return data;
        }

        throw new Error('No se recibió el token de autenticación del backend');
    }
}

export const api = new ApiClient();
