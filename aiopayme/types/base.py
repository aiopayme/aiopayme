from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from aiopayme.client import Payme

class Account:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class BaseCtx:
    def __init__(self, raw: dict):
        self.raw = raw
        self.payme: Optional["Payme"] = None