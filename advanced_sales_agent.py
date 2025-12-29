"""
Advanced sales analysis agent based on `test.ipynb`.

This script exposes a simple CLI around three tool types:
- Product sales breakdown for specific products
- Top selling products
- Monthly sales for a given month

The original notebook used LangGraph's `StateGraph`. Here we keep the
same tool logic but orchestrate it directly in Python for simplicity.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, TypedDict

import pandas as pd
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from sales_data_loader import load_sales_report


class AgentState(TypedDict):
    question: str
    data: pd.DataFrame
    intermediate_steps: List[str]
    final_answer: str


# Initialise LLM
llm = Ollama(model="llama3.1:8b")


def get_product_sales(state: AgentState) -> Dict:
    """Get sales data for specific products mentioned in the question."""
    question = state["question"]
    data = state["data"]

    products = []
    for product in data["Product Name"]:
        if str(product).lower() in question.lower():
            products.append(product)

    if not products:
        return {"result": "No matching products found in the data."}

    results = []
    for product in products:
        product_data = data[data["Product Name"] == product]
        if not product_data.empty:
            sales = product_data.iloc[:, 1:].to_dict(orient="records")[0]
            results.append({"product": product, "sales": sales})

    return {"result": results}


def get_top_products(state: AgentState) -> Dict:
    """Get top selling products by total sales across all columns."""
    data = state["data"].copy()

    sales_columns = data.columns[1:]
    data["Total Sales"] = data[sales_columns].sum(axis=1)

    top_products = data.nlargest(5, "Total Sales")[["Product Name", "Total Sales"]]
    return {"result": top_products.to_dict(orient="records")}


def get_monthly_sales(state: AgentState) -> Dict:
    """Get sales for a specific month (e.g. '2021-07')."""
    question = state["question"]
    data = state["data"]

    # Exclude 'Product Name' and potential 'Total Sales'
    months_in_data = [c for c in data.columns if c not in ("Product Name", "Total Sales")]
    found_month = None

    for month in months_in_data:
        if isinstance(month, str) and month in question:
            found_month = month
            break

    if not found_month:
        return {"result": "No specific month mentioned in the question."}

    monthly_sales = data[["Product Name", found_month]].sort_values(
        found_month, ascending=False
    )
    return {"result": monthly_sales.to_dict(orient="records")}


def router(state: AgentState) -> str:
    """Route to the appropriate tool based on the question."""
    question = state["question"].lower()
    data = state["data"]

    month_columns = [
        col
        for col in data.columns
        if isinstance(col, str) and re.match(r"^\d{4}-\d{2}$", col)
    ]

    if "product" in question and ("sales" in question or "sell" in question):
        return "get_product_sales"
    elif "top" in question and ("product" in question or "selling" in question):
        return "get_top_products"
    elif "month" in question or any(month in question for month in month_columns):
        return "get_monthly_sales"
    else:
        return "general_query"


def general_query(state: AgentState) -> Dict:
    """Handle general queries that don't match specific tools."""
    prompt = ChatPromptTemplate.from_template(
        """
You are an expert data analyst. Answer the user's question based on the provided sales data.

Question: {question}

Available data columns: {columns}

Provide a helpful response. If you can't answer based on the data, say so.
"""
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke(
        {"question": state["question"], "columns": list(state["data"].columns)}
    )

    return {"result": response}


def call_tool(state: AgentState) -> Dict:
    """Call the appropriate tool based on the router's decision."""
    tool_name = router(state)

    if tool_name == "get_product_sales":
        response = get_product_sales(state)
    elif tool_name == "get_top_products":
        response = get_top_products(state)
    elif tool_name == "get_monthly_sales":
        response = get_monthly_sales(state)
    else:
        response = general_query(state)

    return {"tool_response": response, "state": state}


def update_state(state: AgentState, tool_response: Dict) -> AgentState:
    """Update the state with the tool's response."""
    new_state: AgentState = state.copy()
    new_state["intermediate_steps"] = list(state["intermediate_steps"])
    new_state["intermediate_steps"].append(tool_response["result"])
    return new_state


def generate_final_answer(state: AgentState) -> Dict:
    """Generate a final answer from the intermediate steps."""
    if len(state["intermediate_steps"]) == 0:
        return {"final_answer": "I couldn't find an answer to your question."}

    final_answer = state["intermediate_steps"][-1]

    if isinstance(final_answer, (list, dict)):
        try:
            final_answer = json.dumps(final_answer, indent=2)
        except Exception:
            pass

    return {"final_answer": str(final_answer)}


def run_agent(question: str) -> str:
    """High-level helper that runs the full tool + summarisation pipeline."""
    data = load_sales_report("Sales Report.xlsx")
    state: AgentState = {
        "question": question,
        "data": data,
        "intermediate_steps": [],
        "final_answer": "",
    }

    tool_call = call_tool(state)
    updated_state = update_state(state, tool_call["tool_response"])
    final = generate_final_answer(updated_state)
    return final["final_answer"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Advanced sales analysis agent (product, top products, monthly sales)."
    )
    parser.add_argument(
        "question",
        type=str,
        help='Question, e.g. "What were the top selling products?"',
    )
    args = parser.parse_args()

    print(run_agent(args.question))


