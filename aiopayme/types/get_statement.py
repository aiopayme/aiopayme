from .base import BaseCtx


class GetStatementCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)
        self.from_time = params["from"]
        self.to_time = params["to"]

    def ok(self, transactions: list):
        return {
            "result": {
                "transactions": transactions,
            }
        }