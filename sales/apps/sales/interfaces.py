from typing import Optional, TypedDict


class ProductSnapshot(TypedDict):
    name: str
    category: Optional[str] = ''
    price: str
