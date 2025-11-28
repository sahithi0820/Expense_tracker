import pandas as pd
from datetime import datetime

_CATEGORY_KEYWORDS = {
    "Groceries": ["grocery", "super", "mart", "bigbasket"],
    "Dining": ["restaurant", "dine", "cafe", "coffee", "dominos", "mc", "kfc", "pizza"],
    "Transport": ["uber", "ola", "taxi", "train", "bus", "metro", "petrol"],
    "Rent": ["rent", "landlord", "housing"],
    "Utilities": ["electric", "water", "bill", "gas", "utility"],
    "Entertainment": ["netflix", "prime", "movie", "theater", "spotify"],
    "Health": ["pharm", "clinic", "hospital", "dental", "doctor"],
    "Shopping": ["amazon", "flipkart", "myntra", "store"],
    "Subscriptions": ["subscription", "membership"],
    "Education": ["college", "university", "course", "udemy", "coursera"],
    "Insurance": ["insurance", "premium"],
    "Taxes": ["tax", "gst"],
    "Transfers": ["transfer", "neft", "imps", "rtgs", "upi", "paytm", "phonepe"]
}


def categorize_description(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return "Uncategorized"

    txt = text.lower()

    for cat, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in txt for kw in keywords):
            return cat

    return "Uncategorized"


def parse_upload(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]

    # Auto-detect column names
    mapping = {}
    for col in df.columns:
        low = col.lower()
        if "date" in low:
            mapping[col] = "Date"
        elif "desc" in low:
            mapping[col] = "Description"
        elif "amount" in low:
            mapping[col] = "Amount"
        elif "type" in low or "income" in low or "expense" in low:
            mapping[col] = "Type"
        else:
            mapping[col] = col

    df = df.rename(columns=mapping)

    # Required columns
    if not all(c in df.columns for c in ["Date", "Description", "Amount"]):
        raise ValueError("CSV must include: Date, Description, Amount")

    # Clean columns
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").fillna(method="ffill")
    df["Amount"] = df["Amount"].astype(float)

    # Detect Type if missing
    if "Type" not in df.columns:
        df["Type"] = df["Amount"].apply(lambda x: "Income" if x >= 0 else "Expense")

    return df[["Date", "Description", "Amount", "Type"]]


def ensure_session_df():
    import streamlit as st

    if "transactions_df" not in st.session_state:
        st.session_state["transactions_df"] = pd.DataFrame(
            columns=["Date", "Description", "Category", "Amount", "Type"]
        )

    df = st.session_state["transactions_df"]
    return df

def style_money(x):
    try:
        return "₹{:,.2f}".format(float(x))
    except:
        return str(x)