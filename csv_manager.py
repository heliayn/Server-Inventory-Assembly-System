import pandas as pd
from Product_structure import Product,Warehouse


def get_product_by_id(server_id : int, products_dic: dict[int,Product]) -> Product:
    product = products_dic[server_id]

    return product

def load_products_dict() -> dict[int , Product] :    
    df_inventory = pd.read_csv("csv/product.csv")

    products_dic = {
        int(row["Id"]): Product(
            Id=int(row["Id"]),
            PartNumber=str(row["PartNumber"]),
            Description=str(row["Description"]),
        )
        for _, row in df_inventory.iterrows()
    }
    return products_dic


def load_product_bom(products_dic: dict[int, Product]) -> None:    
    df_relationships = pd.read_csv("csv/Relations.csv", usecols= ["S_Id", "P_Id", "Qty"])

    for _,row in df_relationships.iterrows():
        server = get_product_by_id(int(row["S_Id"]), products_dic)
        component = get_product_by_id(int(row["P_Id"]), products_dic)
        quantity = int(row["Qty"])
        
        server.bom[component] = quantity

def load_warehouse_inventory_dict(products_dic: dict[int,Product]) -> dict[Product, int]:
    df_inventory = pd.read_csv("csv/inventory.csv", usecols= ["product_Id","Qty"])
    
    inventory_dic: dict[Product, int] = {
        products_dic[int(row["product_Id"])]: int(row["Qty"])
        for _, row in df_inventory.iterrows()
    }

    return inventory_dic

# {
#     Product(Id=1, PartNumber='8786735',Description='DDR4 64 G-Ram_A'): 175,
#     Product( Id=4,PartNumber='8786738', Description='DDR4 64 G-Ram_B'): 155,
#     Product(Id=2, PartNumber='3258646', Description='Gen 11 core i7-Cpu_A'): 156,
#     .
#     .
#     .
# }


def save_inventory(warehouse: Warehouse , path:str) -> None:
    df = pd.DataFrame([
        {   "Id" : row_id,
            "wh_Id" : warehouse.Id,
            "product_Id": product.Id,
            "Qty": qty,
        }
        for row_id,(product, qty) in enumerate( warehouse.inventory.items())
    ])
    df.to_csv(path, index=False)
