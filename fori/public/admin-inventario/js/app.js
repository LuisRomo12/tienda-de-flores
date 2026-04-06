// app.js: Controlador principal

import InventoryModel from './data.js';
import InventoryUI from './ui.js';
import { api } from './api.js';

document.addEventListener('DOMContentLoaded', async () => {
    // ─── INICIALIZACIÓN DE INVENTARIO ─────────────────────────────────────────
    const model = new InventoryModel();
    const ui = new InventoryUI();

    // ─── LOGIN SECRETO ──────────────────────────────────────────────────────────
    const loginOverlay = document.getElementById('login-overlay');
    const appLayout = document.getElementById('app-layout');
    const loginUser = document.getElementById('login-user');
    const loginInput = document.getElementById('login-pass');
    const regNombre = document.getElementById('reg-nombre');
    const btnLogin = document.getElementById('btn-login');
    const loginError = document.getElementById('login-error');
    const btnLogout = document.getElementById('btn-logout');
    const togglePass = document.getElementById('toggle-pass');

    // Elementos para el toggle de registro
    const registerFields = document.getElementById('register-fields');
    const toggleAuthMode = document.getElementById('toggle-auth-mode');
    const loginFormTitle = document.getElementById('login-form-title');
    let isLoginMode = true;

    // Toggle modo login / registro
    toggleAuthMode.addEventListener('click', () => {
        isLoginMode = !isLoginMode;
        if (isLoginMode) {
            registerFields.style.display = 'none';
            loginFormTitle.textContent = 'Iniciar Sesión';
            btnLogin.innerHTML = 'Entrar al Jardín 🗝️';
            toggleAuthMode.textContent = '¿No tienes cuenta? Regístrate aquí';
            loginError.style.display = 'none';
        } else {
            registerFields.style.display = 'block';
            loginFormTitle.textContent = 'Registrar Administrador';
            btnLogin.innerHTML = 'Crear Cuenta ✨';
            toggleAuthMode.textContent = '¿Ya tienes cuenta? Inicia Sesión';
            loginError.style.display = 'none';
        }
    });

    // Comprobar sesión al cargar
    if (api.isAuthenticated()) {
        await iniciarSesion();
    }

    // Toggle password visibility
    togglePass.addEventListener('click', () => {
        if (loginInput.type === 'password') {
            loginInput.type = 'text';
            togglePass.textContent = '🙈';
        } else {
            loginInput.type = 'password';
            togglePass.textContent = '👁️';
        }
    });

    // Mostrar error de Auth
    const mostrarErrorLogin = (msg) => {
        loginError.style.display = 'block';
        loginError.textContent = '🌵 ' + msg;
        loginInput.style.borderColor = '#ef4444';
        loginUser.style.borderColor = '#ef4444';
        setTimeout(() => {
            loginError.style.display = 'none';
            loginInput.style.borderColor = '#f0c4d0';
            loginUser.style.borderColor = '#f0c4d0';
        }, 3000);
    };

    // Auth: Login o Registro
    const procesarAuth = async () => {
        if (!loginUser.value || !loginInput.value) {
            mostrarErrorLogin('Completa los campos obligatorios');
            return;
        }

        if (isLoginMode) {
            try {
                // Modificado para usar el username ingresado
                await api.loginAdmin(loginUser.value, loginInput.value);
                await iniciarSesion();
            } catch (error) {
                mostrarErrorLogin('Credenciales inválidas');
            }
        } else {
            if (!regNombre.value) {
                mostrarErrorLogin('El nombre es obligatorio');
                return;
            }
            try {
                const response = await fetch(`${window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com'}/api/admin/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: loginUser.value,
                        password: loginInput.value,
                        nombre: regNombre.value
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Error al registrar');
                }

                alert('¡Administrador registrado exitosamente! Ahora puedes iniciar sesión.');
                toggleAuthMode.click();
                loginInput.value = '';

            } catch (error) {
                mostrarErrorLogin(error.message);
            }
        }
    };

    btnLogin.addEventListener('click', procesarAuth);
    loginInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') procesarAuth();
    });

    // Cerrar sesión
    btnLogout.addEventListener('click', () => {
        api.clearToken();
        loginInput.value = '';
        appLayout.style.display = 'none';
        loginOverlay.style.display = 'flex';
    });

    async function iniciarSesion() {
        loginOverlay.style.display = 'none';
        appLayout.style.display = 'flex';

        // Inicializar datos una vez logueado
        await model.loadData();
        refreshTable();
        refreshAccTable();

        // Poblar select de categorías de accesorios
        const accCatSelect = document.getElementById('acc-categoria');
        if (accCatSelect && model.accCategorias.length > 0) {
            accCatSelect.innerHTML = '<option value="">Selecciona...</option>';
            model.accCategorias.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat.nombre;
                opt.textContent = cat.nombre;
                accCatSelect.appendChild(opt);
            });
        }

        await renderizarDashboard();
        await renderizarPedidos();
        await renderizarEntregas();
        await renderizarVentas();
    }

    // ─── NAVEGACIÓN SIDEBAR ───────────────────────────────────────────────────
    const navBtns = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.content-section');

    const activateSection = (targetId) => {
        navBtns.forEach(b => {
            if (b.getAttribute('data-target') === targetId) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });
        sections.forEach(sec => {
            sec.style.display = sec.id === targetId ? 'block' : 'none';
        });
    };

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            activateSection(btn.getAttribute('data-target'));
        });
    });

    const inlineNavBtns = document.querySelectorAll('.nav-btn-inline');
    inlineNavBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            activateSection(btn.getAttribute('data-target'));
        });
    });

    // ─── LÓGICA DE INVENTARIO Y ACCESORIOS ────────────────────────────────────

    // NOTA: refreshTable se llama ahora dentro de iniciarSesion() tras model.loadData()

    const convertBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const fileReader = new FileReader();
            fileReader.readAsDataURL(file);

            fileReader.onload = () => {
                resolve(fileReader.result);
            };

            fileReader.onerror = (error) => {
                reject(error);
            };
        });
    };

    // 1. Manejo del Formulario (Crear / Editar)
    // Manejo del Formulario (Modificado para imágenes múltiples)
    const imageInput = document.getElementById('imagen');
    const imagePreviewContainer = document.getElementById('image-preview-container');

    // Manejar la vista previa de imágenes al seleccionarlas
    imageInput.addEventListener('change', async () => {
        if (!imagePreviewContainer) return;
        imagePreviewContainer.innerHTML = ''; // Limpiar vista previas
        if (imageInput.files) {
            for (let i = 0; i < imageInput.files.length; i++) {
                try {
                    const base64 = await convertBase64(imageInput.files[i]);
                    const imgPreview = document.createElement('img');
                    imgPreview.src = base64;
                    imgPreview.style.width = '60px';
                    imgPreview.style.height = '60px';
                    imgPreview.style.objectFit = 'cover';
                    imgPreview.style.borderRadius = '8px';
                    imgPreview.style.border = '1px solid #f0c4d0';
                    imagePreviewContainer.appendChild(imgPreview);
                } catch (e) {
                    console.error("Error al previsualizar imagen", e);
                }
            }
        }
    });

    document.getElementById('product-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('product-id').value;
        const nombre = document.getElementById('nombre').value;
        const categoria = document.getElementById('categoria').value;
        const precio = document.getElementById('precio').value;
        const stock = document.getElementById('stock').value;

        const sku = document.getElementById('sku').value;
        const tags = document.getElementById('tags').value;
        const descripcion_detallada = document.getElementById('descripcion_detallada').value;
        const recomendaciones = document.getElementById('recomendaciones').value;

        let imagenesExtraData = [];

        // 1. Verificamos si el usuario subió fotos
        if (imageInput.files && imageInput.files.length > 0) {
            for (let i = 0; i < imageInput.files.length; i++) {
                try {
                    const imgData = await convertBase64(imageInput.files[i]);
                    imagenesExtraData.push(imgData);
                } catch (error) {
                    console.error("Error al leer la imagen", error);
                    alert("Error al procesar una de las imágenes");
                    return;
                }
            }
        }

        // 2. Preparamos los datos básicos
        const productData = {
            nombre, categoria, precio, stock,
            sku, tags, descripcion_detallada, recomendaciones
        };

        // 3. Agregamos las imágenes (La primera es la principal, el resto extras, o todas extras si el back lo soporta)
        if (imagenesExtraData.length > 0) {
            // Asignamos la primera como URL principal para retrocompatibilidad
            productData.imagen_url = imagenesExtraData[0];
            // Mandamos el array completo
            productData.imagenes_extra = imagenesExtraData;
        }

        try {
            if (id) {
                // Modo Edición
                await model.editProduct(id, productData);
                ui.showMessage('Flor actualizada correctamente');
            } else {
                // Modo Creación
                await model.addProduct(productData);
                ui.showMessage('Flor agregada al inventario');
            }
            ui.resetForm();
            if (imagePreviewContainer) imagePreviewContainer.innerHTML = ''; // Resetear previews
            refreshTable();
        } catch (error) {
            console.error("Error guardando producto:", error);
            ui.showMessage('Error al guardar en el servidor', 'error');
        }
    });

    // 2. Cancelar Edición
    document.getElementById('btn-cancel').addEventListener('click', () => {
        ui.resetForm();
    });

    // 3. Filtros y Búsqueda (Evento 'input' para búsqueda en tiempo real)
    const searchInput = document.getElementById('search-input');
    const filterSelect = document.getElementById('filter-category');

    [searchInput, filterSelect].forEach(el => {
        el.addEventListener('input', () => {
            const term = searchInput.value;
            const cat = filterSelect.value;
            const filtered = model.filterProducts(term, cat);
            ui.renderTable(filtered);
        });
    });

    // 4. Manejo de Eliminación (Escuchando el CustomEvent de ui.js)
    document.addEventListener('delete-product', async (e) => {
        const id = e.detail;
        if (confirm('¿Estás seguro de que quieres eliminar esta flor del inventario?')) {
            try {
                await model.deleteProduct(id);
                refreshTable();
                mostrarToast('Flor eliminada del jardín 🥀');
            } catch (err) {
                console.error(err);
                ui.showMessage('Error eliminando la flor', 'error');
            }
        }
    });

    // Función auxiliar para repintar la tabla
    function refreshTable() {
        const products = model.getProducts();
        ui.renderTable(products);
        renderizarDashboard(); // Actualizar dashboard si cambia inventario
    }

    // =========================================================================
    // LÓGICA DE ACCESORIOS
    // =========================================================================

    const accImageInput = document.getElementById('acc-imagen');
    const accImagePreviewContainer = document.getElementById('acc-image-preview-container');

    if (accImageInput) {
        accImageInput.addEventListener('change', async () => {
            if (!accImagePreviewContainer) return;
            accImagePreviewContainer.innerHTML = '';
            if (accImageInput.files && accImageInput.files.length > 0) {
                try {
                    const base64 = await convertBase64(accImageInput.files[0]);
                    const imgPreview = document.createElement('img');
                    imgPreview.src = base64;
                    imgPreview.style.width = '60px';
                    imgPreview.style.height = '60px';
                    imgPreview.style.objectFit = 'cover';
                    imgPreview.style.borderRadius = '8px';
                    imgPreview.style.border = '1px solid #f0c4d0';
                    accImagePreviewContainer.appendChild(imgPreview);
                } catch (e) {
                    console.error("Error al previsualizar imagen", e);
                }
            }
        });
    }

    const accForm = document.getElementById('acc-form');
    if (accForm) {
        accForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const id = document.getElementById('acc-id').value;
            const nombre = document.getElementById('acc-nombre').value;
            const categoria = document.getElementById('acc-categoria').value;
            const precio = document.getElementById('acc-precio').value;
            const stock = document.getElementById('acc-stock').value;
            const sku = document.getElementById('acc-sku').value;
            const descripcion_detallada = document.getElementById('acc-descripcion').value;

            let imagen_data = null;
            if (accImageInput.files && accImageInput.files.length > 0) {
                try {
                    imagen_data = await convertBase64(accImageInput.files[0]);
                } catch (error) {
                    console.error("Error al leer la imagen", error);
                    alert("Error al procesar la imagen del accesorio");
                    return;
                }
            }

            const accData = {
                nombre, categoria, precio, stock,
                sku, descripcion_detallada, imagen: imagen_data
            };

            try {
                if (id) {
                    // Modo Edición
                    await model.editAccessory(id, accData);
                    ui.showMessage('Accesorio actualizado correctamente');
                } else {
                    // Modo Creación
                    await model.addAccessory(accData);
                    ui.showMessage('Accesorio agregado al inventario');
                }
                ui.resetAccForm();
                if (accImagePreviewContainer) accImagePreviewContainer.innerHTML = '';
                refreshAccTable();
            } catch (error) {
                console.error("Error guardando accesorio:", error);
                ui.showMessage('Error al guardar en el servidor', 'error');
            }
        });
    }

    const btnAccCancel = document.getElementById('acc-btn-cancel');
    if (btnAccCancel) {
        btnAccCancel.addEventListener('click', () => {
            ui.resetAccForm();
            if (accImagePreviewContainer) accImagePreviewContainer.innerHTML = '';
        });
    }

    const accSearchInput = document.getElementById('acc-search-input');
    const accFilterSelect = document.getElementById('acc-filter-category');

    if (accSearchInput && accFilterSelect) {
        [accSearchInput, accFilterSelect].forEach(el => {
            el.addEventListener('input', () => {
                const term = accSearchInput.value;
                const cat = accFilterSelect.value;
                const filtered = model.filterAccessories(term, cat);
                ui.renderAccTable(filtered);
            });
        });
    }

    document.addEventListener('delete-accessory', async (e) => {
        const id = e.detail;
        if (confirm('¿Estás seguro de que quieres eliminar este accesorio del inventario?')) {
            try {
                await model.deleteAccessory(id);
                refreshAccTable();
                mostrarToast('Accesorio eliminado 🎀');
            } catch (err) {
                console.error(err);
                ui.showMessage('Error eliminando el accesorio', 'error');
            }
        }
    });

    function refreshAccTable() {
        const accs = model.getAccessories();
        ui.renderAccTable(accs);
    }

    // ─── RENDERIZADO DE NUEVAS SECCIONES (CONECTADAS AL BACKEND) ──────────────────────────────────────

    function getStatusClass(status) {
        if (!status) return 'pendiente';
        switch (status.toLowerCase()) {
            case 'completado': case 'entregado': return 'completado';
            case 'en_camino': case 'en ruta': return 'en-ruta';
            default: return 'pendiente';
        }
    }

    async function renderizarDashboard() {
        const products = model.getProducts();
        const accessories = model.getAccessories();

        const totalFlores = products.reduce((acc, p) => acc + Number(p.stock), 0);
        const valorFlores = products.reduce((acc, p) => acc + (Number(p.precio) * Number(p.stock)), 0);

        const totalAccesorios = accessories.reduce((acc, a) => acc + Number(a.stock), 0);
        const valorAccesorios = accessories.reduce((acc, a) => acc + (Number(a.precio) * Number(a.stock)), 0);

        const valorInventario = valorFlores + valorAccesorios;

        // Fetch de los pedidos más recientes de PostgreSQL
        let pedidos = [];
        let ingresosHoy = 0;
        let pedidosHoyCount = 0;
        try {
            pedidos = await api.get('/vista_pedidos?limit=3') || [];
            const resumenHoy = await api.get('/resumen_ventas_diario?limit=1') || [];

            // Si hay ventas para el día de hoy, según la base de datos
            if (resumenHoy.length > 0 && new Date(resumenHoy[0].dia).toDateString() === new Date().toDateString()) {
                ingresosHoy = resumenHoy[0].ingresos;
                pedidosHoyCount = resumenHoy[0].total_pedidos;
            }
        } catch (e) {
            console.error(e);
        }

        const html = `
            <div style="display: flex; justify-content: flex-end; margin-bottom: 24px;">
                <button id="btn-exportar-dashboard" class="btn-secondary" style="padding: 8px 16px; border-radius: 8px; border: 1.5px solid #f0c4d0; background: white; color: #9e6070; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; opacity: ${products.length > 0 ? '1' : '0.5'};" ${products.length === 0 ? 'disabled' : ''}>
                    📥 Exportar Inventario
                </button>
            </div>
            
            <div class="dashboard-grid">
                <div class="stat-card">
                    <div class="stat-icon" style="background: #fce4ec; color: #c4536a;">🌷</div>
                    <div class="stat-content">
                        <h3>Total Flores</h3>
                        <p>${totalFlores}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #ffedd5; color: #ea580c;">🎀</div>
                    <div class="stat-content">
                        <h3>Total Accesorios</h3>
                        <p>${totalAccesorios}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #e0f2fe; color: #0284c7;">📦</div>
                    <div class="stat-content">
                        <h3>Pedidos Hoy (Entregados)</h3>
                        <p>${pedidosHoyCount}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #dcfce7; color: #16a34a;">💰</div>
                    <div class="stat-content">
                        <h3>Ingresos Hoy</h3>
                        <p>$${parseFloat(ingresosHoy).toFixed(2)}</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon" style="background: #f3e8ff; color: #9333ea;">💎</div>
                    <div class="stat-content">
                        <h3>Valor Inventario</h3>
                        <p>$${valorInventario.toFixed(2)}</p>
                    </div>
                </div>
            </div>

            <div class="list-card">
                <h3>Pedidos Recientes</h3>
                ${pedidos.length > 0 ? pedidos.map(order => `
                    <div class="list-item">
                        <div>
                            <div style="font-weight: 600; color: #3d1520; margin-bottom: 4px;">${order.cliente_email || 'Invitado'}</div>
                            <div style="font-size: 0.8rem; color: #9e6070;">#PED-${order.id}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 600; color: #c4536a; margin-bottom: 4px;">$${Number(order.total).toFixed(2)}</div>
                            <span class="status-badge ${getStatusClass(order.estado)}">${order.estado.replace('_', ' ')}</span>
                        </div>
                    </div>
                `).join('') : '<p style="padding: 20px; color: #9e6070; text-align: center;">No hay pedidos recientes.</p>'}
            </div>
        `;
        document.getElementById('dashboard-content').innerHTML = html;

        // Añadir manejador de eventos para exportar JSON del Inventario
        const btnExportarDash = document.getElementById('btn-exportar-dashboard');
        if (btnExportarDash && (products.length > 0 || accessories.length > 0)) {
            btnExportarDash.disabled = false;
            btnExportarDash.style.opacity = '1';

            // Eliminar event listeners anteriores clonando el nodo
            const nuevoBtn = btnExportarDash.cloneNode(true);
            btnExportarDash.parentNode.replaceChild(nuevoBtn, btnExportarDash);

            nuevoBtn.addEventListener('click', () => {
                try {
                    const dataExport = {
                        flores: products,
                        accesorios: accessories
                    };
                    const dataStr = JSON.stringify(dataExport, null, 2);
                    const blob = new Blob([dataStr], { type: "application/json" });
                    const url = URL.createObjectURL(blob);

                    const hoy = new Date().toISOString().split('T')[0];
                    const fileName = `inventario_completo_${hoy}.json`;

                    const a = document.createElement("a");
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();

                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);

                    mostrarToast('🌷🎀 Reporte de inventario generado exitosamente');
                } catch (err) {
                    console.error("Error al exportar JSON:", err);
                    mostrarToast('❌ Error generando el reporte de inventario');
                }
            });
        }
    }

    async function renderizarPedidos() {
        let pedidos = [];
        try {
            pedidos = await api.get('/vista_pedidos') || [];
        } catch (e) { console.error(e); }

        const html = `
            <div class="list-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: none; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 0;">Todos los Pedidos</h3>
                    <button id="btn-exportar-pedidos" class="btn-secondary" style="padding: 8px 16px; border-radius: 8px; border: 1.5px solid #f0c4d0; background: white; color: #9e6070; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 8px; font-weight: 600; opacity: ${pedidos.length > 0 ? '1' : '0.5'};" ${pedidos.length === 0 ? 'disabled' : ''}>
                        📥 Exportar Reporte
                    </button>
                </div>
                ${pedidos.length > 0 ? pedidos.map(order => `
                    <div class="list-item">
                        <div>
                            <div style="font-weight: 600; color: #3d1520; margin-bottom: 4px;">#PED-${order.id} - ${order.cliente_email || 'Invitado'}</div>
                            <div style="font-size: 0.8rem; color: #9e6070;">Fecha: ${new Date(order.fecha_pedido).toLocaleDateString()}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 600; color: #c4536a; margin-bottom: 4px;">$${Number(order.total).toFixed(2)}</div>
                            <span class="status-badge ${getStatusClass(order.estado)}">${order.estado.replace('_', ' ')}</span>
                        </div>
                    </div>
                `).join('') : '<p style="padding: 20px; color: #9e6070; text-align: center;">No se han encontrado pedidos.</p>'}
            </div>
        `;
        document.getElementById('pedidos-content').innerHTML = html;

        // Añadir manejador de eventos para exportar JSON
        const btnExportar = document.getElementById('btn-exportar-pedidos');
        if (btnExportar && pedidos.length > 0) {
            btnExportar.addEventListener('click', () => {
                try {
                    // 1. Convertir el objeto JS a una cadena JSON formateada (2 espacios)
                    const dataStr = JSON.stringify(pedidos, null, 2);

                    // 2. Crear un archivo "virtual" (Blob) y un enlace para descargar
                    const blob = new Blob([dataStr], { type: "application/json" });
                    const url = URL.createObjectURL(blob);

                    const hoy = new Date().toISOString().split('T')[0];
                    const fileName = `reporte_pedidos_${hoy}.json`;

                    // 3. Simular el clic usando un ancla fantasma
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();

                    // Limpieza
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);

                    mostrarToast('📦 Reporte JSON generado exitosamente');
                } catch (err) {
                    console.error("Error al exportar JSON:", err);
                    mostrarToast('❌ Error generando el reporte de pedidos');
                }
            });
        }
    }

    async function renderizarEntregas() {
        // Obtenemos de la vista pedidos todos los que estén pendientes o en_camino para entregar
        let entregasProgramadas = [];
        try {
            entregasProgramadas = await api.get('/entregas_pendientes') || [];
        } catch (e) { console.error(e); }

        const html = `
            <div class="list-card">
                <h3>Rutas Programadas</h3>
                ${entregasProgramadas.length > 0 ? entregasProgramadas.map(delivery => `
                    <div class="list-item">
                        <div>
                            <div style="font-weight: 600; color: #3d1520; margin-bottom: 4px;">Repartidor: ${delivery.repartidor || 'Sin asignar'} (P: #PED-${delivery.id})</div>
                            <div style="font-size: 0.8rem; color: #9e6070;">📍 ${delivery.direccion_entrega}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 600; color: #3d1520; margin-bottom: 4px;">🕒 ${delivery.fecha_entrega ? new Date(delivery.fecha_entrega).toLocaleString() : 'No definida'}</div>
                            <span class="status-badge ${getStatusClass(delivery.estado)}">${delivery.estado.replace('_', ' ')}</span>
                        </div>
                    </div>
                `).join('') : '<p style="padding: 20px; color: #9e6070; text-align: center;">No hay rutas de entrega pendientes.</p>'}
            </div>
        `;
        document.getElementById('entregas-content').innerHTML = html;
    }

    async function renderizarVentas() {
        // En una implementación real, calcularíamos "Ventas de Hoy", "Esta Semana", "Este Mes" sumando la data de 'resumen_ventas_diario'
        // Por ahora mantendré el layout general e inyectaré algunos de los componentes si tenemos data real,
        // o dejaré un "placeholder" de diseño pero usando los fetch estructuralmente correctos.

        // Obtener resumen diario desde Postgres
        let resumenDiario = [];
        let totalGeneral = 0;
        let totalPedidosGeneral = 0;

        try {
            resumenDiario = await api.get('/resumen_ventas_diario') || [];
            totalGeneral = resumenDiario.reduce((acc, v) => acc + Number(v.ingresos), 0);
            totalPedidosGeneral = resumenDiario.reduce((acc, v) => acc + Number(v.total_pedidos), 0);
        } catch (e) { console.error(e); }

        const html = `
            <!-- Top Cards -->
            <div class="dashboard-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-bottom: 24px;">
                <div class="stat-card" style="flex-direction: column; align-items: flex-start; gap: 8px; justify-content: center; min-height: 120px;">
                    <div style="font-size: 0.75rem; color: #c4aab2; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">VENTAS TOTALES (HISTÓRICO)</div>
                    <div style="font-size: 2.2rem; color: #3d1520; font-weight: 700; font-family: 'Georgia', serif;">$${totalGeneral.toFixed(2)}</div>
                    <div style="font-size: 0.8rem; color: #10b981; font-weight: 500;">▲ Conectado a Postgres</div>
                </div>
                <div class="stat-card" style="flex-direction: column; align-items: flex-start; gap: 8px; justify-content: center; min-height: 120px;">
                    <div style="font-size: 0.75rem; color: #c4aab2; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">PEDIDOS TOTALES</div>
                    <div style="font-size: 2.2rem; color: #3d1520; font-weight: 700; font-family: 'Georgia', serif;">${totalPedidosGeneral}</div>
                    <div style="font-size: 0.8rem; color: #10b981; font-weight: 500;">▲ Entregados con éxito</div>
                </div>
            </div>

            <!-- Table Card -->
            <div class="list-card" style="padding: 24px; max-width: 900px; margin: 0 auto;">
                <h3 style="display: flex; align-items: center; gap: 8px; font-size: 0.95rem; color: #3d1520; border-bottom: none; margin-bottom: 20px;"><span style="color: #a78bfa;">📊</span> Resumen Diario (Desde Base de Datos)</h3>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #fce4ec;">
                            <th style="padding: 12px 20px; text-align: left; font-size: 0.75rem; color: #c4536a; font-weight: 700; background: transparent;">Fecha</th>
                            <th style="padding: 12px 20px; text-align: center; font-size: 0.75rem; color: #c4536a; font-weight: 700; background: transparent;">Ingresos</th>
                            <th style="padding: 12px 20px; text-align: center; font-size: 0.75rem; color: #c4536a; font-weight: 700; background: transparent;">Pedidos</th>
                            <th style="padding: 12px 20px; text-align: center; font-size: 0.75rem; color: #c4536a; font-weight: 700; background: transparent;">Ticket Prom.</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${resumenDiario.length > 0 ? resumenDiario.map(row => `
                            <tr style="border-bottom: 1px solid #fce4ec;">
                                <td style="padding: 14px 20px; font-size: 0.85rem; color: #3d1520; font-weight: 500;">${row.dia}</td>
                                <td style="padding: 14px 20px; font-size: 0.85rem; color: #3d1520; font-weight: 700; text-align: center;">$${Number(row.ingresos).toFixed(2)}</td>
                                <td style="padding: 14px 20px; font-size: 0.85rem; color: #9e6070; text-align: center;">${row.total_pedidos}</td>
                                <td style="padding: 14px 20px; font-size: 0.85rem; color: #c4536a; text-align: center;">$${Number(row.ticket_promedio).toFixed(2)}</td>
                            </tr>
                        `).join('') : '<tr><td colspan="4" style="padding: 20px; text-align: center; color: #9e6070;">Ningún pedido ha sido entregado aún.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
        document.getElementById('ventas-content').innerHTML = html;
    }

    // ─── TOAST NOTIFICATIONS MÁS BONITAS ──────────────────────────────────────
    function mostrarToast(mensaje) {
        const toast = document.getElementById('toast');
        toast.textContent = mensaje;
        toast.style.display = 'block';
        toast.style.animation = 'fadeIn 0.3s ease';

        setTimeout(() => {
            toast.style.animation = 'fadeIn 0.3s ease reverse forwards';
            setTimeout(() => {
                toast.style.display = 'none';
                toast.style.animation = '';
            }, 300);
        }, 3000);
    }

    // Sobrescribir ui.showMessage para usar el Toast nuevo si es de éxito
    const oldShowMessage = ui.showMessage;
    ui.showMessage = function (msg, type) {
        if (type !== 'error') {
            mostrarToast("🌸 " + msg);
        } else {
            oldShowMessage.call(this, msg, type);
        }
    };
});