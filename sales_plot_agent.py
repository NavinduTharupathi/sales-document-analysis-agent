"""
Sales plotting agent based on `salesDataPlotting.ipynb`.

This script:
- Loads `Sales Report.xlsx`
- Generates a PNG line chart for monthly sales of a given product.

Instead of returning base64 HTML for notebooks, it saves a PNG file
and prints the path, so it can be used as a normal script.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
from langchain_community.llms import Ollama  # kept for parity / future use
from langgraph.graph import END, Graph

from sales_data_loader import load_sales_report


llm = Ollama(model="llama3.1:8b", temperature=0.3)  # noqa: F841


data = load_sales_report("Sales Report.xlsx")


def plot_product_sales(state: Dict) -> Dict:
    """Generate a sales plot for the specified product and save it as PNG."""
    question = state["question"]
    product_name = None

    # Extract product name from question
    for product in data["Product Name"]:
        if str(product).lower() in question.lower():
            product_name = product
            break

    if not product_name:
        return {"result": "Product not found in the data.", "plot_path": None}

    product_data = data[data["Product Name"] == product_name]
    if product_data.empty:
        return {"result": "No sales data available for this product.", "plot_path": None}

    # Identify date-like columns (as in the notebook: columns starting with '202')
    date_cols = [col for col in data.columns if isinstance(col, str) and col.startswith("202")]
    sales = product_data[date_cols].iloc[0]
    months = [pd.to_datetime(col).strftime("%b %Y") for col in sales.index]

    # Create plot
    plt.figure(figsize=(10, 5))
    plt.plot(months, sales.values, marker="o", linestyle="-")
    plt.title(f"Monthly Sales for {product_name}")
    plt.xlabel("Month")
    plt.ylabel("Sales Amount")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Save to file
    output_dir = Path("plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = str(product_name).replace(" ", "_").replace("/", "_")
    output_path = output_dir / f"{safe_name}_sales.png"

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    with open(output_path, "wb") as f:
        f.write(buf.read())
    plt.close()

    return {
        "result": f"Sales plot generated for {product_name}",
        "plot_path": str(output_path),
    }


workflow = Graph()

workflow.add_node("generate_plot", plot_product_sales)
workflow.add_node(
    "format_response",
    lambda state: {"response": state["result"], "plot_path": state.get("plot_path", "")},
)

workflow.add_edge("generate_plot", "format_response")
workflow.add_edge("format_response", END)
workflow.set_entry_point("generate_plot")

app = workflow.compile()


def run_agent(question: str) -> Dict[str, str]:
    """
    Run the plotting agent.

    Returns a dict with:
    - response: textual description
    - plot_path: filesystem path to the generated PNG (if any)
    """
    result = app.invoke({"question": question})
    return {
        "response": result.get("response", "No response generated"),
        "plot_path": result.get("plot_path", ""),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a monthly sales plot for a specific product."
    )
    parser.add_argument(
        "question",
        type=str,
        help='Question, e.g. "Show me monthly sales plot for 70mm Casement"',
    )
    args = parser.parse_args()

    result = run_agent(args.question)
    print(result["response"])
    if result["plot_path"]:
        print(f"Plot saved to: {result['plot_path']}")


