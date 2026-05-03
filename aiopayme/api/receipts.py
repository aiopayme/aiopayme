from aiopayme.types.detail import FiscalDetail

from .base import BaseAPI


class ReceiptsAPI(BaseAPI):
    async def create(
        self,
        amount: int,
        account: dict,
        detail: FiscalDetail | None = None,
    ) -> dict:
        params = {
            "amount": amount * 100,
            "account": account,
        }
        if detail:
            params["detail"] = detail.to_dict()

        return await self._request("receipts.create", params)

    async def pay(self, invoice_id: str, token: str, payer: dict | None = None) -> dict:
        params: dict = {
            "id": invoice_id,
            "token": token,
        }
        if payer:
            params["payer"] = payer

        return await self._request("receipts.pay", params)

    async def send(self, invoice_id: str, phone: str) -> dict:
        return await self._request("receipts.send", {
            "id": invoice_id,
            "phone": phone,
        })

    async def cancel(self, invoice_id: str) -> dict:
        return await self._request("receipts.cancel", {
            "id": invoice_id,
        })

    async def check(self, invoice_id: str) -> dict:
        return await self._request("receipts.check", {
            "id": invoice_id,
        })

    async def get(self, invoice_id: str) -> dict:
        return await self._request("receipts.get", {
            "id": invoice_id,
        })