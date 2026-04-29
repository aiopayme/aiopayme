from dataclasses import dataclass
from .base import BaseCtx


@dataclass
class FiscalData:
    receipt_id: int
    status_code: int
    message: str
    terminal_id: str
    fiscal_sign: str
    qr_code_url: str
    date: str


class SetFiscalDataCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)
        self.transaction_id = params["id"]
        self.type = params["type"]  # "PERFORM" | "CANCEL"
        self.fiscal_data = FiscalData(**params["fiscal_data"])

    def ok(self):
        return {"result": {}}