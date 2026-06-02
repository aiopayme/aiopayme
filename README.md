# aiopayme

[![PyPI version](https://badge.fury.io/py/aiopayme.svg)](https://pypi.org/project/aiopayme)
[![Python versions](https://img.shields.io/pypi/pyversions/aiopayme)](https://pypi.org/project/aiopayme)
[![License](https://img.shields.io/github/license/aiopayme/aiopayme)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/aiopayme)](https://pepy.tech/project/aiopayme)
[![Docs](https://img.shields.io/badge/docs-aiopayme.github.io-teal)](https://aiopayme.github.io)
[![Habr](https://img.shields.io/badge/Habr-статья-blue?logo=habr)](https://habr.com/ru/articles/1042466/)
[![Telegram](https://img.shields.io/badge/Telegram-aiopayme-blue?logo=telegram)](https://t.me/aiopayme)

## Tutorial

[![YouTube](https://img.shields.io/badge/YouTube-Как_подключить_Payme_к_боту-red?logo=youtube&style=for-the-badge)](https://www.youtube.com/watch?v=XI-xrN6DxtI)

Async Python library for [Payme](https://payme.uz) integration.

## Quick Start

### 1. Install

```bash
pip install aiopayme
```

### 2. Create your models

```python
# models/order.py

import enum
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    amount = Column(BigInteger, nullable=False)
    status = Column(String, default=OrderStatus.PENDING.value)
    payme_transaction_id = Column(String, nullable=True)
```

```python
# models/payme.py

from sqlalchemy import Column, Integer, String, BigInteger
from models.order import Base


class PaymeTransaction(Base):
    __tablename__ = "payme_transactions"

    id = Column(Integer, primary_key=True)
    payme_id = Column(String, unique=True, nullable=False)
    order_id = Column(Integer, nullable=True)
    state = Column(Integer, default=1)
    amount = Column(BigInteger, nullable=False)
    create_time = Column(BigInteger, nullable=False)
    perform_time = Column(BigInteger, default=0)
    cancel_time = Column(BigInteger, default=0)
    reason = Column(Integer, nullable=True)
```

### 3. Create services/payme.py

```python
# services/payme.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from aiopayme.exceptions import Errors
from aiopayme.utils import time_to_payme
from aiopayme.types import (
    CheckPerformTransactionCtx,
    CreateTransactionCtx,
    PerformTransactionCtx,
    CancelTransactionCtx,
    CheckTransactionCtx,
    GetStatementCtx,
)

from models import OrderStatus, Order, PaymeTransaction


class PaymeService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order(self, order_id) -> Order | None:
        return await self.db.scalar(
            select(Order).where(Order.id == int(order_id))
        )

    async def get_transaction(self, payme_id: str) -> PaymeTransaction | None:
        return await self.db.scalar(
            select(PaymeTransaction).where(PaymeTransaction.payme_id == payme_id)
        )

    async def get_active_transaction(self, order_id: int) -> PaymeTransaction | None:
        return await self.db.scalar(
            select(PaymeTransaction).where(
                PaymeTransaction.order_id == order_id,
                PaymeTransaction.state == 1,
            )
        )

    async def get_transactions(self, from_time: int, to_time: int):
        return (await self.db.scalars(
            select(PaymeTransaction).where(
                PaymeTransaction.create_time >= from_time,
                PaymeTransaction.create_time <= to_time,
            )
        )).all()


    async def check_perform(self, ctx: CheckPerformTransactionCtx):
        order = await self.get_order(ctx.account.order_id)
        if not order:
            raise Errors.invalid_account()
        if order.amount * 100 != ctx.amount:
            raise Errors.invalid_amount()
        return ctx.ok(allow=True)

    async def create_transaction(self, ctx: CreateTransactionCtx):
        tx = await self.get_transaction(ctx.payme_id)
        order = await self.get_order(ctx.account.order_id)

        if not order:
            raise Errors.invalid_account()
        if order.amount * 100 != ctx.amount:
            raise Errors.invalid_amount()

        if tx:
            if tx.state == -1:
                raise Errors.unable_to_perform()
            return ctx.ok(transaction_id=tx.payme_id, create_time=tx.create_time)

        if order.status == OrderStatus.PAID:
            raise Errors.invalid_account()

        existing_tx = await self.get_active_transaction(order.id)
        if existing_tx:
            rejected = PaymeTransaction(
                payme_id=ctx.payme_id,
                order_id=order.id,
                amount=ctx.amount,
                create_time=ctx.time,
                state=-1,
                cancel_time=time_to_payme(),
                reason=3,
            )
            self.db.add(rejected)
            await self.db.commit()
            raise Errors.unable_to_perform()

        tx = PaymeTransaction(
            payme_id=ctx.payme_id,
            order_id=order.id,
            amount=ctx.amount,
            create_time=ctx.time,
            state=1,
        )

        self.db.add(tx)
        await self.db.execute(
            update(Order)
            .where(Order.id == order.id)
            .values(payme_transaction_id=ctx.payme_id)
        )
        await self.db.commit()
        return ctx.ok(transaction_id=tx.payme_id, create_time=tx.create_time)

    async def perform_transaction(self, ctx: PerformTransactionCtx):
        tx = await self.get_transaction(ctx.transaction_id)
        if not tx:
            raise Errors.transaction_not_found()

        if tx.state == 2:
            return ctx.ok(transaction_id=tx.payme_id, perform_time=tx.perform_time, state=2)

        tx.state = 2
        tx.perform_time = time_to_payme()
        await self.db.execute(
            update(Order)
            .where(Order.id == tx.order_id)
            .values(status=OrderStatus.PAID.value)
        )
        await self.db.commit()
        return ctx.ok(transaction_id=tx.payme_id, perform_time=tx.perform_time, state=2)

    async def cancel_transaction(self, ctx: CancelTransactionCtx):
        tx = await self.get_transaction(ctx.transaction_id)
        if not tx:
            raise Errors.transaction_not_found()

        if tx.state in (-1, -2):
            return ctx.ok(
                transaction=tx.payme_id,
                cancel_time=tx.cancel_time,
                state=tx.state,
                reason=tx.reason,
            )

        tx.state = -2 if tx.state == 2 else -1
        tx.cancel_time = time_to_payme()
        tx.reason = ctx.reason
        await self.db.execute(
            update(Order)
            .where(Order.id == tx.order_id)
            .values(status=OrderStatus.CANCELLED.value)
        )
        await self.db.commit()
        return ctx.ok(
            transaction=tx.payme_id,
            state=tx.state,
            cancel_time=tx.cancel_time,
            reason=tx.reason,
        )

    async def check_transaction(self, ctx: CheckTransactionCtx):
        tx = await self.get_transaction(ctx.transaction_id)
        if not tx:
            raise Errors.transaction_not_found()

        return ctx.ok(
            state=tx.state,
            create_time=tx.create_time,
            perform_time=tx.perform_time,
            cancel_time=tx.cancel_time,
            reason=tx.reason,
        )

    async def get_statement(self, ctx: GetStatementCtx):
        from_time = ctx.from_time
        to_time = ctx.to_time
        if from_time > to_time:
            from_time, to_time = to_time, from_time

        txs = await self.get_transactions(from_time, to_time)
        return ctx.ok(transactions=[
            {
                "id": tx.payme_id,
                "time": tx.create_time,
                "amount": tx.amount,
                "account": {"order_id": tx.order_id},
                "state": tx.state,
                "create_time": tx.create_time,
                "perform_time": tx.perform_time or 0,
                "cancel_time": tx.cancel_time or 0,
                "reason": tx.reason,
            }
            for tx in txs
        ])
```

### 4. Add router

```python
# handlers/payme.py

from aiopayme import Router
from aiopayme.types import *
from sqlalchemy.ext.asyncio import AsyncSession

from services.payme import PaymeService

router = Router()

@router.check_perform_transaction()
async def check_perform(ctx: CheckPerformTransactionCtx, db: AsyncSession):
    return await PaymeService(db).check_perform(ctx)

@router.create_transaction()
async def create_transaction(ctx: CreateTransactionCtx, db: AsyncSession):
    return await PaymeService(db).create_transaction(ctx)

@router.perform_transaction()
async def perform_transaction(ctx: PerformTransactionCtx, db: AsyncSession):
    return await PaymeService(db).perform_transaction(ctx)

@router.cancel_transaction()
async def cancel_transaction(ctx: CancelTransactionCtx, db: AsyncSession):
    return await PaymeService(db).cancel_transaction(ctx)

@router.check_transaction()
async def check_transaction(ctx: CheckTransactionCtx, db: AsyncSession):
    return await PaymeService(db).check_transaction(ctx)

@router.get_statement()
async def get_statement(ctx: GetStatementCtx, db: AsyncSession):
    return await PaymeService(db).get_statement(ctx)
```

### 5. Setup and mount to FastAPI

```python
# main.py

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession
from aiopayme import Payme, Dispatcher
from handlers.payme import router as payme_router

payme = Payme(
    merchant_id="your_merchant_id",
    secret_key="your_secret_key",
    sandbox=True,
)

dp = Dispatcher()
dp.include_router(payme_router)
payme.setup(dp)
payme.provide(AsyncSession, SessionLocal)

app = FastAPI()

@app.post("/webhook/payme")
async def payme_webhook(request: Request):
    return await payme.handle(
        data=await request.json(),
        headers=dict(request.headers),
    )
```

### 6. Generate pay link

```python
@app.post("/order/create")
async def create_order(data: OrderCreate):
    async with SessionLocal() as db:
        result = await db.execute(
            insert(Order).values(
                amount=data.amount,
            ).returning(Order.id)
        )
        order_id = result.scalar()
        await db.commit()

    pay_link = payme.generate_pay_link(
        amount=data.amount,
        account={
            "order_id": order_id,
        }
    )

    return {"order_id": order_id, "pay_link": pay_link}
```

## Documentation

Full documentation at [aiopayme.github.io](https://aiopayme.github.io)

## License

MIT