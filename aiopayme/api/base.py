import base64
import httpx
from typing import Any
from aiopayme.exceptions import PaymeError


class BaseAPI:
    def __init__(self, merchant_id: str, secret_key: str, sandbox: bool = False):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.base_url = (
            "https://checkout.test.paycom.uz/api"
            if sandbox
            else "https://checkout.paycom.uz/api"
        )

    def _headers(self) -> dict:
        token = base64.b64encode(f"{self.merchant_id}:{self.secret_key}".encode()).decode()
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, params: dict) -> dict[str, Any]:
        payload = {
            "id": 1,
            "method": method,
            "params": params,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                print(data["error"])
                raise PaymeError(code=data["error"]["code"])

            return data.get("result", {})