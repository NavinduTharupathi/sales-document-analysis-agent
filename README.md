## Sales Document Analysis Agent – Script Version

This project is a script-based version of your Jupyter notebooks (`test.ipynb`, `testNew.ipynb`, `salesDataPlotting.ipynb`).  
It provides:

- **Shared data loading utility** for the sales Excel file.
- **Basic sales agent** to compute total sales per product.
- **Advanced sales agent** for product breakdowns, top products, and monthly sales.
- **Sales plotting agent** to generate monthly sales charts for a product.

All scripts operate on the same input file: `Sales Report.xlsx`.

---

### Setup

- **1. Create and activate a virtual environment (recommended)**

```bash
cd C:\Users\Navindu\Desktop\sales-document-analysis-agent
python -m venv .venv
.venv\Scripts\activate
```

- **2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

- **3. Install and configure Ollama**

These scripts use the local `Ollama` LLM (as in your notebooks):

1. Install Ollama from the official website.
2. Make sure the `llama3.1:8b` model is available:

```bash
ollama pull llama3.1:8b
```

> If you want to run the scripts without LLM calls, you can temporarily comment out the `Ollama` lines in the agent scripts.

Ensure `Sales Report.xlsx` is present in the project root (same directory as the scripts).

---

### Scripts Overview and How to Run

- **Shared data loader – `sales_data_loader.py`**

  - **What it does**: Loads and cleans `Sales Report.xlsx` into a `pandas.DataFrame`.
  - **Usage**: This is a utility module; it is imported by the other scripts and does not need to be run directly.

---

- **Basic product total sales agent – `basic_sales_agent.py`**

  - **What it does**: Computes the **total sales for a single product** by summing all numeric sales columns.
  - **Example command**:

    ```bash
    python basic_sales_agent.py "Show me total sales for PC-1000"
    ```

  - **Expected output**:

    - A single line such as:
      - `Total sales for PC-1000: 108.62`

---

- **Advanced analysis agent – `advanced_sales_agent.py`**

  - **What it does**: Routes your question to one of several tools:
    - **Product sales breakdown** (per month/column).
    - **Top selling products** (by total sales).
    - **Monthly sales** for a given month.
    - Falls back to a **general LLM answer** when it cannot map the question to a tool.

  - **Example commands**:

    - Top products:

      ```bash
      python advanced_sales_agent.py "What were the top selling products?"
      ```

    - Product-level breakdown:

      ```bash
      python advanced_sales_agent.py "What were the sales for 70mm Casement?"
      ```

    - Monthly sales:

      ```bash
      python advanced_sales_agent.py "How did sales look in 2021-07?"
      ```

  - **Expected output**:

    - A formatted JSON-like string showing products and sales values, or a natural language answer from the LLM.

---

- **Sales plotting agent – `sales_plot_agent.py`**

  - **What it does**: Generates a **PNG line chart** showing monthly sales for a specified product.
  - **Example command**:

    ```bash
    python sales_plot_agent.py "Show me monthly sales plot for 70mm Casement"
    ```

  - **What happens**:
    - The script creates a `plots` folder (if it doesn’t exist).
    - It saves a file like `plots/70mm_Casement_sales.png`.
    - The console prints:
      - A short message (`Sales plot generated for 70mm Casement`).
      - The full path to the saved PNG.

  - **You can open the PNG** with your image viewer to inspect the chart.

---

### Notes

- **Excel file location**: All scripts expect `Sales Report.xlsx` in the project root.
- **Extensibility**: You can import the functions from these scripts into other modules or notebooks for richer applications (e.g. APIs or UIs).
- **LLM dependency**: If you replace Ollama with another LLM backend later, you only need to adjust the LLM initialisation lines in the agent scripts.


