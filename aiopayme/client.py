from __future__ import annotations

import base64
import inspect
import logging

from urllib.parse import quote
from decimal import Decimal

from typing import Any, Callable

from aiopayme.types.base import Account
from aiopayme.protocol.methods import METHODS
from aiopayme.exceptions import PaymeError, Errors
from aiopayme.api.cards import CardsAPI
from aiopayme.api.receipts import ReceiptsAPI

logger = logging.getLogger("aiopayme")
logger.setLevel(logging.DEBUG)

class Payme:
    def __init__(self,
                 merchant_id: str,
                 secret_key: str,
                 sandbox: bool = False,
                 echo: bool = False):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.sandbox = sandbox
        self.echo = echo

        self._dispatcher = None
        self._context: dict[type, Any] = {}
        self._providers: dict[type, Callable] = {}

        self.cards = CardsAPI(merchant_id, secret_key, sandbox)
        self.receipts = ReceiptsAPI(merchant_id, secret_key, sandbox)

    async def handle(self, data: dict, headers: dict | None = None):
        headers = {k.lower(): v for k, v in (headers or {}).items()}

        method = data.get("method")

        if self.echo:
            logger.debug(f"Incoming request: method={method}, id={data.get('id')}")

        if not self._verify_auth(headers.get("authorization")):
            logger.warning("Authorization failed")
            return Errors.access_denied().to_dict()

        if not self._dispatcher:
            logger.warning("Dispatcher not set")
            return Errors.internal().to_dict()

        params = data.get("params", {})

        if method not in METHODS:
            logger.warning(f"Method not found: {method}")
            return Errors.method_not_found().to_dict()

        name, ctx_cls = METHODS[method]
        handler = self._dispatcher.handlers.get(name)

        if not handler:
            logger.warning(f"Handler not found: {name}")
            return Errors.method_not_found().to_dict()

        ctx = ctx_cls(params=params, raw=data)
        ctx.payme = self

        try:
            sig = inspect.signature(handler)
            kwargs = {}
            factories_ctx = []

            for param_name, param in sig.parameters.items():
                if param_name == "ctx":
                    continue

                ann = param.annotation

                if ann in self._context:
                    kwargs[param_name] = self._context[ann]

                elif ann in self._providers:
                    factory = self._providers[ann]
                    instance = factory()
                    if hasattr(instance, "__aenter__"):
                        instance = await instance.__aenter__()
                        factories_ctx.append(instance)
                    kwargs[param_name] = instance

            try:
                result = await handler(ctx, **kwargs)
                if self.echo:
                    logger.debug(f"Handler '{name}' completed successfully")
                return result

            finally:
                for instance in factories_ctx:
                    if hasattr(instance, "__aexit__"):
                        await instance.__aexit__(None, None, None)

        except PaymeError as e:
            logger.warning(f"PaymeError in '{name}': code={e.code}")
            return e.to_dict()
        except Exception as e:
            logger.exception(f"Unhandled exception in '{name}': {e}")
            return Errors.internal().to_dict()

    def setup(self, dispatcher) -> None:
        self._dispatcher = dispatcher

    def set_context(self, **kwargs):
        for key, value in kwargs.items():
            self._context[type(value)] = value

    def provide(self, typ: type, factory: Callable):
        """
        Usage:
            payme.provide(DbSession, get_db)
        """

        self._providers[typ] = factory


    def generate_pay_link(
        self,
        amount: int | Decimal,
        account: "Account | dict",
        return_url: str | None = None,
        ) -> str:
        
        if hasattr(account, "__dict__"):
            account = account.__dict__
        
        parts = [f"m={self.merchant_id}"]

        for key, value in account.items():
            parts.append(f"ac.{key}={value}")

        parts.append(f"a={amount * 100}")

        if return_url:
            parts.append(f"c={quote(return_url)}")

        params = ";".join(parts) + ";"

        encoded = base64.b64encode(params.encode()).decode()

        base_url = (
            "https://checkout.test.paycom.uz"
            if self.sandbox
            else "https://checkout.paycom.uz"
        )

        return f"{base_url}/{encoded}"
    
    def _verify_auth(self, auth: str | None) -> bool:
        if not auth:
            return False
        try:
            decoded = base64.b64decode(auth.replace("Basic ", "")).decode()
            login, key = decoded.split(":", 1)
            return login == "Paycom" and key == self.secret_key
        except Exception:
            return False
