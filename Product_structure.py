from __future__ import annotations
from dataclasses import dataclass,field


@dataclass(frozen=True)
class Product:
    Id: int
    PartNumber: str
    Description: str
    bom: dict[Product, int] = field(default_factory=dict, compare=False, hash=False,repr=False)

@dataclass()
class Warehouse:
    Id: int
    Name: str
    inventory: dict[Product, int]
