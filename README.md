# Server Warehouse Inventory & Assembly Management

A Python-based warehouse management application for checking component availability, calculating **how many servers can be assembled from current stock**, and updating inventory after an assembly operation.

The project provides two ways to interact with the same inventory and Bill of Materials (BOM) logic:

- **Streamlit web interface** (`view.py`) — an interactive dashboard for inventory inspection, assembly planning, and building servers.
- **Command-line interface** (`Main.py`) — a terminal-based workflow for selecting and building servers.

> **Project context:** A Computer Engineering university project demonstrating CSV-based data management, object-oriented modeling, BOM processing, and a practical inventory workflow. This is a prototype, not a production warehouse/ERP system.

## The Problem

A sales or warehouse team needs to answer questions such as:

- Which components and finished servers are currently in stock?
- What parts are required to assemble a particular server model?
- How many units of that server can be built without exceeding the available stock?
- Which component is limiting the maximum build quantity?
- How does the stock change after an assembly operation?

Checking each component independently is not enough: every server model has its own BOM specifying the type and quantity of components required for one unit. This application uses those relationships to determine assembly capacity and maintain a CSV-based inventory.

## Features

### Streamlit dashboard

- Display stock with **All**, **Parts only**, and **Servers only** filters.
- Show summary metrics for listed products, total quantities, and finished-server stock.
- Select a server model from products with an associated BOM.
- Show **Can build now**, BOM item count, and the most limiting component.
- Inspect a BOM table showing the quantity needed per server, total required quantity, current stock, and availability status.
- Enter a build quantity constrained to the currently calculated capacity.
- Build servers, deduct the consumed parts, increase finished-server stock, and **save the updated inventory to CSV automatically**.
- Save the current inventory manually or reload its contents from CSV.

### Command-line version

- Print the current inventory.
- Choose a server by ID and confirm the selected product.
- Display the maximum buildable quantity.
- Enter a valid build quantity and update the in-memory inventory.
- Save inventory changes to CSV **when the command-line session ends**.

## Technology Stack

| Technology | Role |
| --- | --- |
| Python 3.10+ | Application logic and data models |
| Streamlit | Web interface |
| Pandas | CSV loading, tabular views, and inventory export |
| Python `dataclasses` | `Product` and `Warehouse` models |
| CSV files | Product catalog, BOM relationships, and stock persistence |

## Project Structure

```text
project-root/
├── view.py                  # Streamlit user interface
├── Main.py                  # Command-line interface
├── Product_structure.py     # Product and Warehouse data models
├── csv_manager.py           # Load product/BOM/inventory CSVs; save inventory
├── Functions.py             # Build-capacity and inventory-update logic
├── csv/
│   ├── product.csv          # Product catalog
│   ├── Relations.csv        # BOM relationships
│   └── inventory.csv        # Stored quantities of parts and servers
└── README.md
```

**Important:** The three CSV files must be present in the `csv/` directory for the application to run. They are read through relative paths, so start the program from the project root.

## Installation

### 1. Get the project

Download the project or clone its GitHub repository, then open a terminal in the project root (the directory containing `view.py`).

### 2. Create a virtual environment (recommended)

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install pandas streamlit
```

If you maintain a `requirements.txt` containing these dependencies, you can instead run:

```bash
python -m pip install -r requirements.txt
```

### 4. Prepare the data files

Make sure the directory and filenames match the structure below exactly (including the capital **R** in `Relations.csv`):

```text
csv/product.csv
csv/Relations.csv
csv/inventory.csv
```

## Running the Application

### Web interface (recommended)

From the project root:

```bash
python -m streamlit run view.py
```

Streamlit normally opens the app in your browser. If needed, visit:

```text
http://localhost:8501
```

**Typical workflow**

1. Review the **Inventory** table and optionally filter it by parts or finished servers.
2. Select a model from **Build a server**.
3. Check **Can build now**, the limiting part, and the **Parts required (BOM)** table.
4. Choose the quantity you want to assemble.
5. Click **Build server**. The application updates inventory and saves it to `csv/inventory.csv`.
6. Use **Save inventory** to save manually, or **Reload from CSV** to reload the saved data.

### Command-line interface

```bash
python Main.py
```

Follow the terminal prompts to select a server ID, confirm the selected model, and enter a build quantity. Enter **`0`** at the server-ID prompt to finish the session and save the inventory.

> **Implementation note:** The current command-line implementation identifies potential servers using IDs greater than `4`, whereas the Streamlit version identifies servers by whether they have a non-empty BOM. Keep this difference in mind when preparing the catalog.

## Data Files and Required Columns

The application uses three CSV files:

| CSV file | Required columns | Purpose |
| --- | --- | --- |
| `csv/product.csv` | `Id`, `PartNumber`, `Description` | Defines parts and server products. `Id` is used to reference them elsewhere. |
| `csv/Relations.csv` | `S_Id`, `P_Id`, `Qty` | Each row defines a parent server/product (`S_Id`), a component (`P_Id`), and how many units of that component are required. |
| `csv/inventory.csv` | `product_Id`, `Qty` | Loads the stock quantity for each product. |

When inventory is saved, `csv_manager.py` writes these columns to `csv/inventory.csv`:

```text
Id,wh_Id,product_Id,Qty
```

`Id` is the output row identifier, `wh_Id` is the warehouse ID, and `product_Id` / `Qty` are the values used when loading inventory.

The product IDs referenced in the BOM and inventory files must exist in `product.csv`. BOM quantities should be positive integers. Back up `inventory.csv` before demonstration or test builds, because successful builds change the stored quantities.

## How Server Assembly Capacity Is Calculated

Each server's **Bill of Materials (BOM)** maps the required components to their quantities per server. The maximum number of servers that can be built is the smallest per-component capacity:

```text
Buildable servers = min(available quantity of component // required quantity per server)
```

**Illustrative example:**

| Component | Available in stock | Required per server | Supports building |
| --- | ---: | ---: | ---: |
| CPU | 12 | 2 | 6 servers |
| RAM module | 30 | 4 | 7 servers |
| SSD | 10 | 1 | 10 servers |

The maximum assembly capacity is **6 servers**, because CPUs are the limiting component. These numbers are only an example, not values taken from the project's CSV files.

When a build is performed:

1. The required quantity for each part is multiplied by the requested number of servers.
2. That amount is subtracted from the corresponding part's stock.
3. The completed server's stock is increased by the requested quantity.
4. The web interface saves the new quantities immediately; the CLI saves on exit.

## Code Organization

| File | Responsibility |
| --- | --- |
| `Product_structure.py` | Defines `Product` (ID, part number, description, BOM) and `Warehouse` (ID, name, inventory). |
| `csv_manager.py` | Reads the catalog, BOM relationships, and inventory; writes updated inventory to CSV. |
| `Functions.py` | Calculates buildable quantity, applies stock consumption and server production, and prints inventory. |
| `view.py` | Builds the Streamlit dashboard, inventory and BOM tables, bottleneck display, input controls, and save/reload actions. |
| `Main.py` | Provides the interactive terminal workflow. |

## Current Scope and Limitations

- Inventory is stored in local CSV files, **not** a database. The application does not implement concurrent or multi-user stock updates.
- CSV filenames, relative paths, and column names must match the expected structure.
- The program assumes valid product references and sensible quantities in the source CSVs; comprehensive input-data validation is not implemented.
- The underlying `build_server()` function updates quantities directly. Capacity validation is performed by the current UI/CLI workflows, so calling that function independently requires validation by the caller.
- The CLI expects numeric input for server IDs and quantities; invalid text input can raise an error.
- The Streamlit implementation keeps a working inventory in session state and saves it when a build is completed or when **Save inventory** is clicked.
- There is no direct integration with Odoo, another ERP system, or an external database in the current version.

## Possible Future Improvements

- Add robust CSV schema validation and more informative error handling.
- Use a transactional database with an audit trail for inventory movements.
- Add user authentication and role-based permissions.
- Support multiple warehouses and concurrent users.
- Introduce unit tests for stock calculation and assembly edge cases.
- Integrate with an ERP system such as Odoo through a suitable API.

## Notes for University Evaluation

The project illustrates how a **BOM-based inventory problem** can be translated into a working application: data is loaded from CSV files, represented with Python classes, processed through reusable business-logic functions, and presented through both graphical and command-line interfaces. The prototype demonstrates assembly-capacity computation and stock updates; its limitations should be considered before any real-world deployment.
