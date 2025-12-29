import re
from typing import Optional

import pandas as pd


def load_excel_data(file_path: str, sheet_name: str = "Sheet1") -> pd.DataFrame:
    """
    Load the Excel file and return a cleaned DataFrame.

    This function is based on the data‑loading logic used in the notebooks:
    - Treats the first row as headers.
    - Handles duplicate / empty column names.
    - Normalises date-like column names to a consistent YYYY-MM format where possible.
    """
    # Load the data without assuming headers
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Set the first row as column headers
    headers = df.iloc[0].tolist()

    # Handle duplicate / missing headers
    seen = {}
    new_headers = []
    for header in headers:
        if pd.isna(header):
            new_headers.append("unnamed")
            continue
        if header in seen:
            seen[header] += 1
            new_headers.append(f"{header}_{seen[header]}")
        else:
            seen[header] = 0
            new_headers.append(str(header))

    df.columns = new_headers
    df = df[1:]  # remove header row
    df.reset_index(drop=True, inplace=True)

    # Normalise *values* in date columns if any header looks like a date string
    date_columns = [
        col
        for col in df.columns
        if isinstance(col, str) and re.match(r"^\d{4}-\d{2}-\d{2}", col)
    ]
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m")
        except Exception:
            # Best‑effort; if conversion fails we leave the column as‑is
            pass

    return df


def load_sales_report(path: str = "Sales Report.xlsx") -> pd.DataFrame:
    """
    Convenience wrapper for loading the main sales report.
    """
    return load_excel_data(path, sheet_name="Sheet1")


