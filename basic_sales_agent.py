"""
Basic sales Q&A agent based on the logic from `testNew.ipynb`.

This script:
- Loads `Sales Report.xlsx`
- Answers questions like "Show me total sales for PC-1000"
  by summing all numeric sales columns for the matching product.
"""

from typing import Dict

from langchain_community.llms import Ollama
from langgraph.graph import END, Graph

from sales_data_loader import load_sales_report


# Initialise LLM (not strictly needed for the simple total‑sales tool,
# but kept here to mirror the notebook setup and for future expansion).
llm = Ollama(model="llama3.1:8b", temperature=0.3)  # noqa: F841


# Load data once at startup
data = load_sales_report("Sales Report.xlsx")


def get_product_total_sales(state: Dict) -> Dict:
    """
    Calculate total sales for a specific product.

    The product name is inferred by matching any `Product Name` value
    that appears (case‑insensitive) in the user question.
    """
    question = state["question"]
    product_name = None

    # Simple product name extraction
    for product in data["Product Name"]:
        if str(product).lower() in question.lower():
            product_name = product
            break

    if not product_name:
        return {"result": "Product not found in the data."}

    # Calculate total sales (sum all numeric columns except the first)
    sales_columns = [col for col in data.columns if col != "Product Name"]
    product_data = data[data["Product Name"] == product_name]

    if product_data.empty:
        return {"result": "No sales data available for this product."}

    total_sales = product_data[sales_columns].sum(axis=1).iloc[0]
    return {"result": f"Total sales for {product_name}: {total_sales:.2f}"}


# Minimal LangGraph workflow to mirror the notebook
workflow = Graph()

workflow.add_node("get_sales", get_product_total_sales)
workflow.add_node("format_response", lambda state: {"response": state["result"]})

workflow.add_edge("get_sales", "format_response")
workflow.add_edge("format_response", END)

workflow.set_entry_point("get_sales")
app = workflow.compile()


def run_agent(question: str) -> str:
    """Public helper for other modules or CLI use."""
    result = app.invoke({"question": question})
    return result.get("response", "No response generated")


if __name__ == "__main__":
    # Simple CLI usage
    import argparse

    parser = argparse.ArgumentParser(
        description="Basic sales agent: compute total sales for a given product."
    )
    parser.add_argument(
        "question",
        type=str,
        help='Question about a product, e.g. "Show me total sales for PC-1000"',
    )
    args = parser.parse_args()

    answer = run_agent(args.question)
    print(answer)


