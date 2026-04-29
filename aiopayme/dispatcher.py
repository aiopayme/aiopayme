from aiopayme.router import Router

class Dispatcher(Router):
    def include_router(self, router: Router):
        self.handlers.update(router.handlers)

    def include_routers(self, *routers: Router):
        for router in routers:
            self.include_router(router)

    def set_fiscal_data(self):
        return self.on("set_fiscal_data")