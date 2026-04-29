# aiopayme

[![PyPI version](https://badge.fury.io/py/aiopayme.svg)](https://pypi.org/project/aiopayme)
[![Python versions](https://img.shields.io/pypi/pyversions/aiopayme)](https://pypi.org/project/aiopayme)
[![License](https://img.shields.io/github/license/aiopayme/aiopayme)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/aiopayme)](https://pypi.org/project/aiopayme)
[![Telegram](https://img.shields.io/badge/Telegram-aiopayme-blue?logo=telegram)](https://t.me/aiopayme)

Async Python library for [Payme](https://payme.uz) integration.

## Documentation

[aiopayme.github.io](https://aiopayme.github.io)

## Installation

```bash
pip install aiopayme
```

## Quick Example

```python
from aiopayme import Payme, Dispatcher, Router
from aiopayme.types import CheckPerformTransactionCtx

payme = Payme(
    merchant_id="your_merchant_id",
    secret_key="your_secret_key",
    sandbox=True,
)

dp = Dispatcher()
router = Router()

@router.check_perform_transaction()
async def check_perform(ctx: CheckPerformTransactionCtx):
    ...

dp.include_router(router)
payme.setup(dp)
```

## License

MIT