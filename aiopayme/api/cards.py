from .base import BaseAPI


class CardsAPI(BaseAPI):
    async def create(self, number: str, expire: str, save: bool = True) -> dict:
        return await self._request("cards.create", {
            "card": {
                "number": number,
                "expire": expire,
            },
            "save": save,
        })

    async def get_verify_code(self, token: str) -> dict:
        return await self._request("cards.get_verify_code", {
            "token": token,
        })

    async def verify(self, token: str, code: str) -> dict:
        return await self._request("cards.verify", {
            "token": token,
            "code": code,
        })

    async def check(self, token: str) -> dict:
        return await self._request("cards.check", {
            "token": token,
        })

    async def remove(self, token: str) -> dict:
        return await self._request("cards.remove", {
            "token": token,
        })