from locust import HttpUser, task
from core.locust.common import fake, get_csrf_token


class NotepadBehavior(HttpUser):
    contador = 0

    def on_start(self):
        self.signup()

    @task
    def signup(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/signup", data={"email": fake.email(), "password": fake.password(), "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")

    @task(2)
    def load_notepad(self):
        print("Cargando notepads")
        response = self.client.get("/notepad")
        if response.status_code == 200:
            print("Lista cargada de manera correcta")
        else:
            print("Error en la carga de la lista")

    @task(1)
    def create_notepad(self):
        title = NotepadBehavior.contador
        NotepadBehavior.contador += 1
        print("Creando nuevo notepad")
        response = self.client.post("/notepad/create", data={"title": title, "body": "This is an example"})

        if response.status_code in (200, 302):
            print("Notepad creado de manera correcta")
        else:
            print("Error al crear el notepad")
