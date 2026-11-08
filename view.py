from __future__ import annotations

import streamlit as st
import pandas as pd

from Functions import calculate_buildable, build_server
from csv_manager import (
    load_products_dict,
    load_product_bom,
    load_warehouse_inventory_dict,
    get_product_by_id,
    save_inventory,
)
from Product_structure import Product, Warehouse

INVENTORY_PATH = "csv/inventory.csv"


def inventory_to_df(warehouse: Warehouse, servers: set[int]) -> pd.DataFrame:
    rows = []
    for product, qty in warehouse.inventory.items():
        kind = "Server" if product.Id in servers else "Part"
        rows.append(
            {
                "ID": product.Id,
                "Type": kind,
                "Part Number": product.PartNumber,
                "Description": product.Description,
                "Qty": qty,
            }
        )
    return pd.DataFrame(rows)


def bom_to_df(
    server: Product,
    inventory_dic: dict[Product, int],
    requested_qty: int,
) -> pd.DataFrame:
    rows = []
    for part, required_qty in server.bom.items():
        available = inventory_dic.get(part, 0)
        needed = required_qty * requested_qty
        rows.append(
            {
                "Part ID": part.Id,
                "Part Number": part.PartNumber,
                "Description": part.Description,
                "Per Server": required_qty,
                "Needed": needed,
                "In Stock": available,
                "Status": "OK" if available >= needed else "Short",
            }
        )
    return pd.DataFrame(rows)


def find_bottleneck(server: Product, inventory_dic: dict[Product, int]) -> str | None:
    if not server.bom:
        return None

    limiting_part = None
    limiting_count = float("inf")

    for part, required_qty in server.bom.items():
        available = inventory_dic.get(part, 0)
        possible = available // required_qty
        if possible < limiting_count:
            limiting_count = possible
            limiting_part = part

    if limiting_part is None:
        return None

    return (
        f"{limiting_part.Description} "
        f"(stock: {inventory_dic.get(limiting_part, 0)}, "
        f"needs {server.bom[limiting_part]} each)"
    )


def init_session() -> None:
    if "initialized" in st.session_state:
        return

    products_dic = load_products_dict()
    load_product_bom(products_dic)
    inventory_dic = load_warehouse_inventory_dict(products_dic)

    st.session_state.products_dic = products_dic
    st.session_state.warehouse = Warehouse(
        Id=1,
        Name="FML",
        inventory=inventory_dic,
    )
    st.session_state.message = ""
    st.session_state.message_type = "success"
    st.session_state.initialized = True


def get_servers(products_dic: dict[int, Product]) -> list[Product]:
    return [product for product in products_dic.values() if product.bom]


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: "IBM Plex Sans", "DM Sans", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(1200px 500px at 10% -10%, #dcebff 0%, transparent 55%),
                radial-gradient(900px 400px at 100% 0%, #e8f6f0 0%, transparent 50%),
                #f7f8fa;
        }

        .hero {
            background: linear-gradient(135deg, #0f2f46 0%, #1a4d68 55%, #246b5e 100%);
            color: #f5fafc;
            padding: 1.4rem 1.6rem;
            border-radius: 18px;
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 28px rgba(15, 47, 70, 0.18);
        }

        .hero h1 {
            margin: 0;
            font-size: 1.7rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .hero p {
            margin: 0.45rem 0 0 0;
            opacity: 0.9;
            font-size: 0.98rem;
        }

        .panel-title {
            margin: 0 0 0.2rem 0;
            font-size: 1.05rem;
            font-weight: 600;
            color: #173447;
        }

        .panel-hint {
            color: #5b6b78;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e3e8ee;
            border-radius: 14px;
            padding: 0.7rem 0.9rem;
        }

        div[data-testid="stMetric"] label {
            color: #3d4d5c !important;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #102433 !important;
        }

        [data-testid="stRadio"] label,
        [data-testid="stRadio"] p,
        [data-testid="stRadio"] div[role="radiogroup"] label,
        [data-testid="stRadio"] div[role="radiogroup"] p {
            color: #102433 !important;
            font-weight: 600 !important;
        }

        [data-testid="stNumberInput"] input {
            color: #102433 !important;
            font-weight: 600 !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1a4d68, #246b5e);
            border: none;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="FML Warehouse | Build Servers",
        page_icon="🖥️",
        layout="wide",
    )
    apply_styles()
    init_session()

    products_dic: dict[int, Product] = st.session_state.products_dic
    warehouse: Warehouse = st.session_state.warehouse
    inventory_dic = warehouse.inventory
    servers = get_servers(products_dic)
    server_ids = {s.Id for s in servers}

    st.markdown(
        """
        <div class="hero">
            <h1>FML Warehouse</h1>
            <p>Check stock, review parts needed, and build servers in a few clear steps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.message:
        if st.session_state.message_type == "success":
            st.success(st.session_state.message)
        else:
            st.error(st.session_state.message)
        st.session_state.message = ""

    total_items = len(inventory_dic)
    total_units = sum(inventory_dic.values())
    server_stock = sum(
        qty for product, qty in inventory_dic.items() if product.Id in server_ids
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Products in stock list", total_items)
    m2.metric("Total units", total_units)
    m3.metric("Finished servers in stock", server_stock)

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.markdown('<p class="panel-title">1. Inventory</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="panel-hint">Current warehouse stock. Parts are used to build servers.</p>',
            unsafe_allow_html=True,
        )

        view_filter = st.radio(
            "Choose which table to show",
            options=["All", "Parts only", "Servers only"],
            horizontal=True,
        )

        inventory_df = inventory_to_df(warehouse, server_ids)
        if view_filter == "Parts only":
            inventory_df = inventory_df[inventory_df["Type"] == "Part"]
        elif view_filter == "Servers only":
            inventory_df = inventory_df[inventory_df["Type"] == "Server"]

        st.dataframe(
            inventory_df,
            use_container_width=True,
            hide_index=True,
            height=320,
        )

        save_col, reload_col = st.columns(2)
        with save_col:
            if st.button("Save inventory", use_container_width=True):
                save_inventory(warehouse, INVENTORY_PATH)
                st.session_state.message = "Inventory saved to csv/inventory.csv"
                st.session_state.message_type = "success"
                st.rerun()
        with reload_col:
            if st.button("Reload from CSV", use_container_width=True):
                st.session_state.clear()
                st.session_state.message = "Inventory reloaded from CSV files"
                st.session_state.message_type = "success"
                st.rerun()

    with right:
        st.markdown('<p class="panel-title">2. Build a server</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="panel-hint">Pick a server, check required parts, then build.</p>',
            unsafe_allow_html=True,
        )

        if not servers:
            st.warning("No servers with a BOM were found.")
            return

        options = {
            f"{s.Description}  ·  ID {s.Id}  ·  {s.PartNumber}": s.Id for s in servers
        }
        selected_label = st.selectbox("Server", list(options.keys()))
        server = get_product_by_id(options[selected_label], products_dic)

        buildable = calculate_buildable(server, inventory_dic)
        bottleneck = find_bottleneck(server, inventory_dic)

        c1, c2 = st.columns(2)
        c1.metric("Can build now", buildable)
        c2.metric("Parts in BOM", len(server.bom))

        if bottleneck:
            st.info(f"Limiting part: {bottleneck}")

        if buildable <= 0:
            requested_qty = 1
            st.error("Not enough parts to build this server right now.")
        else:
            requested_qty = st.number_input(
                "Quantity to build",
                min_value=1,
                max_value=buildable,
                value=1,
                step=1,
            )

        st.markdown("**Parts required (BOM)**")
        bom_df = bom_to_df(server, inventory_dic, int(requested_qty))
        st.dataframe(bom_df, use_container_width=True, hide_index=True)

        can_build = buildable > 0 and 1 <= int(requested_qty) <= buildable
        if st.button(
            "Build server",
            type="primary",
            use_container_width=True,
            disabled=not can_build,
        ):
            message = build_server(server, int(requested_qty), inventory_dic)
            save_inventory(warehouse, INVENTORY_PATH)
            st.session_state.message = f"{message} Inventory updated and saved."
            st.session_state.message_type = "success"
            st.rerun()

    with st.expander("How it works"):
        st.markdown(
            """
            1. Look at **Inventory** on the left.
            2. Choose a **server** on the right.
            3. Check the **BOM** table: each row shows what is needed and what is in stock.
            4. Enter how many to build (cannot exceed **Can build now**).
            5. Click **Build server** — stock is reduced and saved automatically.
            """
        )


if __name__ == "__main__":
    main()
