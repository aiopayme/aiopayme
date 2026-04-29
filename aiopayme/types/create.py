from .base import BaseCtx, Account


class CreateTransactionCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)

        self.account = Account(**params.get("account", {}))
        self.amount = params["amount"]
        self.payme_id = params["id"]
        self.time = params["time"]

    def ok(self, transaction_id: str, create_time: int):
        result = {
            "result": {
                "transaction": transaction_id,
                "create_time": create_time,
                "state": 1,
            }
        }
        return result