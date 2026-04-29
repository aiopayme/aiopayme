from .base import BaseCtx, Account


class CancelTransactionCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)
        self.transaction_id = params["id"]
        self.reason = params.get("reason")
        self.account = Account(**params.get("account", {}))

    def ok(self, *, transaction: str, state: int, cancel_time: int, reason: int | None):
        return {
            "result": {
                "transaction": transaction,
                "state": state,
                "cancel_time": cancel_time,
                "reason": reason,
            }
        }