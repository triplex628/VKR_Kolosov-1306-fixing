import requests

API_URL = "http://127.0.0.1:8000"

class APIClient:
    def __init__(self):
        self.token = None

    def register(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(f"{API_URL}/users/register", json=data)
        return response.json()

    def login(self, username, password):
        data = {"username": username, "password": password}
        response = requests.post(f"{API_URL}/users/login", data=data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        return response.json()

    def add_workout(self, name, duration):
        if not self.token:
            return {"error": "User not logged in"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"name": name, "duration": duration}
        response = requests.post(f"{API_URL}/workouts", json=data, headers=headers)
        return response.json()
    
    def get_workouts(self):
        if not self.token:
            return {"error": "User not logged in"}

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_URL}/workouts", headers=headers)
        return response.json()


client = APIClient()
