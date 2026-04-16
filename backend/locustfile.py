from locust import HttpUser, task, between
import random

class TiendaFloresUser(HttpUser):
    # Simula un tiempo de espera/lectura aleatorio de los usuarios entre 1 y 4 segundos
    wait_time = between(1, 4)
    
    # Este método se ejecuta automáticamente siempre que un usuario virtual "entra" a la app
    def on_start(self):
        # Puedes establecer estado inicial aquí, pero este script simulará un usuario "anómino" 
        # que revisa el catálogo y luego intenta hacer login
        pass

    @task(3)
    def revisar_catalogo(self):
        # Petición GET al catálogo. El peso (3) significa que este task
        # se ejecutará el triple de veces que el login_usuario
        with self.client.get("/api/flores", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error cargando catálogo: {response.status_code}")

    @task(1)
    def intentos_de_login(self):
        # Petición POST al endpoint de login
        # Aquí puedes usar credenciales dummy para simular el tráfico al servidor auth.
        payload = {
            "email": "usuario_stress_test@example.com",
            "password": "FakePassword123!"
        }
        
        # FastAPI está esperando el UserLogin model por JSON en /api/login
        # Usaremos catch_response porque esperarémos que falle (401) debido a credenciales dummy
        # pero para Locust será considerado "éxito" si simplemente devuelve la respuesta rápida
        with self.client.post("/api/login", json=payload, catch_response=True) as response:
            if response.status_code in [200, 401]:
                # Como son credenciales dummy, un 401 (Unauthorized) es la respuesta correcta del servidor
                response.success()
            elif response.status_code == 429:
                response.failure("Rate Limit Excedido (Se activó la protección Too Many Requests)")
            else:
                response.failure(f"Falla inesperada en login: {response.status_code}")
