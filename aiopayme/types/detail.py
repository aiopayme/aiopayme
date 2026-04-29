from dataclasses import dataclass


@dataclass
class FiscalItem:
    title: str
    price: int
    count: float
    code: str
    units: int
    package_code: str


@dataclass
class FiscalDetail:
    receipt_type: int
    items: list[FiscalItem]

    def __post_init__(self):
        self.items = [
            item if isinstance(item, FiscalItem) else FiscalItem(**item)
            for item in self.items
        ]

    def to_dict(self) -> dict:
        return {
            "receipt_type": self.receipt_type,
            "items": [
                {
                    "title": item.title,
                    "price": item.price,
                    "count": item.count,
                    "code": item.code,
                    "units": item.units,
                    "package_code": item.package_code,
                }
                for item in self.items
            ]
        }