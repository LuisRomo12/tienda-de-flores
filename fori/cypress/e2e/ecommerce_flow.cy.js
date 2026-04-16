describe('Flujo E2E - Tienda de Flores', () => {
  before(() => {
    // Para que el pago o agregar al carrito funcione, necesitamos un token
    // Generaremos uno de testing o puedes iniciar sesión vía UI
    // En este caso, simularemos inyectando un token en localStorage para el test,
    // asumiendo que es un JWT válido o que el backend local permite acceso.
    
    // Si tienes un script de seeder local, aquí podrías registrar o loguear al usuario
  })

  // Preservamos el localStorage entre tests para no desloguearnos
  beforeEach(() => {
    // Alternativamente, simulamos un login directo vía request al backend local
    // si conocemos las credenciales. Asumimos usuario dummy "test@test.com" con pwd "123".
    
    // Para no hacer el test propenso a fallar por falta de la base de datos de test, 
    // interceptaremos solo en caso de que la API real local falle, o podemos usar el flujo real
    // En este script priorizamos visitar y verificar la interfaz como pidió el prompt:
    cy.visit('/')
  })

  it('Debe navegar desde la página de inicio al catálogo', () => {
    // 1. Verificar que estamos en Home
    cy.get('h1').contains('Bienvenido').should('be.visible')
    
    // 2. Hacer clic en "Ver Catálogo"
    cy.get('a.btn-primary').contains('Ver Catálogo').click()
    
    // 3. Verificar que la URL cambió al catálogo
    cy.url().should('include', '/catalogo')
    cy.get('.section-header h2').contains('Explorar Productos').should('be.visible')
  })

  it('Debe poder seleccionar un producto y agregarlo al carrito', () => {
    // 1. Ir directo al catálogo
    cy.visit('/catalogo')

    // Esperar a que la API cargue los productos. Tomamos interceptor para seguridad
    cy.intercept('GET', '**/api/flores*').as('getFlores')
    cy.wait('@getFlores', { timeout: 10000 }).its('response.statusCode').should('be.oneOf', [200, 304])

    // 2. Hacer clic en el primer producto de la cuadrícula
    cy.get('.product-card').first().as('firstProduct')
    
    // Extraer el nombre del primer producto para validarlo después en el carrito
    cy.get('@firstProduct').find('.prod-title').invoke('text').then((productName) => {
      
      cy.get('@firstProduct').click()
      
      // 3. Verificar que llegamos a la página de detalle
      cy.url().should('include', '/producto/')
      cy.get('h1').contains(productName).should('be.visible')

      // INYECCIÓN DE LOGIN
      // En lugar de usar cy.window, interceptamos las APIs para no ser bloqueados
      // Y permitimos que la UI proceda. Dado que ProductDetails requiere localStorage
      // dinámicamente antes de agregar al carrito, podemos setearlo así de forma segura:
      cy.window().then((window) => {
         window.localStorage.setItem('token', 'fake.eyJleHAiOjk5OTk5OTk5OTl9.fake')
         window.localStorage.setItem('access_token', 'fake.eyJleHAiOjk5OTk5OTk5OTl9.fake')
      })

      // Interceptamos la llamada al carrito para que nuestro token fake no tire un 401 del backend,
      // logrando testear la UI independientemente del estado de la DB
      cy.intercept('POST', '**/api/user/carrito/items', { 
          statusCode: 200, 
          body: { message: "Item agregado al carrito", item_id: 1 } 
      }).as('addToCart')

      // 4. Agregar al carrito
      cy.get('.add-to-cart-btn').contains('Agregar al Carrito').click()
      cy.wait('@addToCart')

      // Verificar que salió el alert (Cypsress auto-acepta los alert, pero los podemos atrapar)
      cy.on('window:alert', (text) => {
        expect(text).to.contains('¡Flor(es) agregada(s) a tu carrito exitosamente!')
      })
    })
  })

  it('Debe visualizar el producto agregado en el carrito', () => {
    // Interceptamos chequeos de Vue Router para que no nos expulse a /login
    cy.intercept('GET', '**/api/auth/me', { statusCode: 200, body: { id: 1, email: "test@cypress.local", role: "user" } }).as('authMe')
    cy.intercept('GET', '**/api/users/me/preferences', { statusCode: 200, body: { tema: "light", idioma: "es" } }).as('prefs')

    // Interceptamos la obtención del carrito para poner info mockeada de prueba
    cy.intercept('GET', '**/api/user/carrito', { 
        statusCode: 200, 
        body: { 
            carrito_id: 1, 
            items: [
                {
                    id: 1, 
                    tipo: 'flor', 
                    producto_id: 1, 
                    nombre: 'Ramo de Prueba Cypress', 
                    precio: 500, 
                    cantidad: 1,
                    imagen: ''
                }
            ] 
        } 
    }).as('getCart')

    // 1. Navegar al carrito inyectando token EXACTAMENTE ANTES de que Vue inicie
    cy.visit('/carrito', {
      onBeforeLoad(win) {
        win.localStorage.setItem('token', 'fake.eyJleHAiOjk5OTk5OTk5OTl9.fake')
        win.localStorage.setItem('access_token', 'fake.eyJleHAiOjk5OTk5OTk5OTl9.fake')
      }
    })
    cy.wait('@getCart')

    // 2. Afirmar comprobaciones de UI en el carrito
    cy.get('.cart-layout').should('be.visible')
    cy.get('.item-name').contains('Ramo de Prueba Cypress').should('be.visible')
    cy.get('.item-price').contains('$500.00').should('be.visible')
    
    // 3. Verificamos que el total de items sea 1
    cy.get('.item-count-badge').contains('1 Items').should('be.visible')
  })
})
