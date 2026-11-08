from __future__ import annotations
from Functions import calculate_buildable,build_server, display_inventory 
from csv_manager import load_products_dict, load_product_bom, load_warehouse_inventory_dict, get_product_by_id, save_inventory
from Product_structure import Warehouse


def main() -> None :
  
    products_dic = load_products_dict()
    load_product_bom(products_dic)
    inventory_dic = load_warehouse_inventory_dict(products_dic)         #product dictionary + quantity of products


    Fml= Warehouse(Id=1,Name= "FML", inventory= inventory_dic)
    display_inventory(Fml)
    
    while True:
        server_id = int(input("Enter the server id u want to build(0 to quit): "))
        if server_id == 0 :
            break

        if server_id in products_dic and  server_id > 4 :               #only server ids, no part id

            server= get_product_by_id(server_id, products_dic)           #get instance
            answer = input(f"\n{server}\ndid you mean this server?(yes / no) ")

            if answer == "yes":
            
                buildable = calculate_buildable(server, inventory_dic)
                print(f"\nyou can build {buildable} of this server")

                req = int(input("how many servers do you want to build?"))
                if 0 < req <= buildable :

                    message = build_server(server, req, inventory_dic)
                    print(message)

                    print("\nupdating inventory...")
                    display_inventory(Fml)

                else :
                    print (f"Requested quantity is not a valid amount, you should enter a number between 0 and {buildable}.")

        else:
            print("wrong server id")

    save_inventory(Fml, "csv/inventory.csv")
    
if __name__ == "__main__":
    main()


