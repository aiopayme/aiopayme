from .base import BaseCtx, Account


class CheckTransactionCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)
        self.transaction_id = params["id"]
        self.account = Account(**params.get("account", {}))

    def ok(self, state: int, create_time: int, perform_time: int = 0, cancel_time: int = 0, reason: int | None = None):
        result = {
            "result": {
                "state": state,
                "create_time": create_time,
                "perform_time": perform_time or 0,
                "cancel_time": cancel_time or 0,
                "transaction": self.transaction_id,
                "reason": reason,
            }
        }
        if reason is not None:
            result["result"]["reason"] = reason
        return result