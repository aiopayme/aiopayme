from .base import BaseCtx, Account


class CheckPerformTransactionCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)
        self.account = Account(**params.get("account", {}))
        self.amount = params["amount"]

    def ok(self, allow: bool = True):
        return {
            "result": {
                "allow": allow,
            }
        }