from locust import HttpUser, task, between

class ONCCPerformanceTest(HttpUser):
    # Simula el tiempo de espera de un usuario real entre clics (de 1 a 3 segundos)
    wait_time = between(1, 3)

    @task
    def test_home_page(self):
        # Golpea la URL raíz pública del sistema para medir el rendimiento MVC
        self.client.get("/")