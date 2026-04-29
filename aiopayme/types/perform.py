from .base import BaseCtx, Account


class PerformTransactionCtx(BaseCtx):
    def __init__(self, params: dict, raw: dict):
        super().__init__(raw)
        self.transaction_id = params["id"]

    def ok(
        self,
        *,
        transaction_id: str,
        perform_time: int,
        state: int = 2,
    ):
        return {
            "result": {
                "transaction": transaction_id,
                "perform_time": perform_time,
                "state": state,
            }
        }