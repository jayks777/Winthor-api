#DESATIVADO - juliano desligou o bagulho la
import os, httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_USER = os.getenv("API_USER")
API_PASSWORD = os.getenv("API_PASSWORD")


class ApiClient:
    def __init__(self):
        self.token = None

    async def login(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/auth",
                json={
                    "user": API_USER,
                    "password": API_PASSWORD
                }
            )

            response.raise_for_status()

            self.token = response.json()["token"]

    async def request(self, method, endpoint, **kwargs):
        if self.token is None:
            await self.login()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{API_URL}{endpoint}",
                headers=headers,
                **kwargs
            )

        if response.status_code == 401:
            await self.login()

            headers["Authorization"] = f"Bearer {self.token}"

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    f"{API_URL}{endpoint}",
                    headers=headers,
                    **kwargs
                )

        response.raise_for_status()

        return response.json()


api = ApiClient()