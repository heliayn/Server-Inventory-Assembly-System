from __future__ import annotations
from Product_structure import Product,Warehouse
import pandas as pd

def calculate_buildable(
    server: Product,
    inventory_dic: dict[Product, int],
) -> int:

    if not server.bom:
        return 0
    
    possible_Qty = float ("inf")
    
    for part, required_qty in server.bom.items():
        available_Qty = inventory_dic.get(part, 0)
        possible_Qty = min(possible_Qty, available_Qty // required_qty)
        
    return int(possible_Qty)


def build_server(
    server: Product,
    requested_qty: int,
    inventory_dic: dict[Product, int],
) -> str:

    for part, required_Qty in server.bom.items():
        consumed_Qty = requested_qty * required_Qty
        inventory_dic[part] -= consumed_Qty

    inventory_dic[server] = (inventory_dic.get(server, 0) + requested_qty)

    return f"{requested_qty} servers built successfully!"


def display_inventory(Fml: Warehouse):
    rows = [
        {
            "Id": product.Id,
            "PartNumber" : product.PartNumber,
            "Description" : product.Description,
            "Qty": qty,
             
        }
        for product, qty in Fml.inventory.items()
    ]
    df = pd.DataFrame(rows)  
    print(df.to_string(index=False))
