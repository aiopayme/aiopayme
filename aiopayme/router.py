class Router:
    def __init__(self):
        self.handlers = {}

    def on(self, name: str):
        def wrapper(fn):
            self.handlers[name] = fn
            return fn
        return wrapper
    
    def set_fiscal_data(self):
        return self.on("set_fiscal_data")

    def create_transaction(self):
        return self.on("create_transaction")

    def perform_transaction(self):
        return self.on("perform_transaction")

    def cancel_transaction(self):
        return self.on("cancel_transaction")

    def check_transaction(self):
        return self.on("check_transaction")

    def check_perform_transaction(self):
        return self.on("check_perform_transaction")

    def get_statement(self):
        return self.on("get_statement")