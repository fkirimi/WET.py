import os
import streamlit as st

# Folder and file paths
WET_FOLDER = "WET 3.0"
os.makedirs(WET_FOLDER, exist_ok=True)

CATEGORY_FILE = os.path.join(WET_FOLDER, "categories.json")
TRANSACTION_FILE = os.path.join(WET_FOLDER, "saved_transactions.json")
TRANSACTION_JSON = os.path.join(WET_FOLDER, "transactions.json")
TRANSACTION_CSV = os.path.join(WET_FOLDER, "transactions_export.csv")
BUDGET_FILE = os.path.join(WET_FOLDER, "budgets.json")

# Standard column mappings
STANDARD_COLUMNS = {
    "Transaction Name": "transaction name",
    "Date": "date",
    "Amount(Kes)": "amount(kes)",
    "Category": "category",
    "Sub Category": "subcategory",
    "Status": "status",
    "Transaction Type": "transaction type",
    "Transaction Fees": "transaction fees",
    "item description (money in)": "item description (money in)",
    "item description (money out)": "item description (money out)",
    "Payment Method": "payment method"
}

# Export column order
EXPORT_COLUMNS = [
    "date", "week", "amount(kes)", "transaction fees", "transaction type",
    "category", "subcategory", "payment method",
    "item description (money in)", "item description (money out)"
]

# Initialize session state defaults
def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None
    if "categories" not in st.session_state:
        st.session_state.categories = {}
    if "budgets" not in st.session_state:
        st.session_state.budgets = {}
    if "current_period" not in st.session_state:
        st.session_state.current_period = ""
    if "opening_balance" not in st.session_state:
        st.session_state.opening_balance = 0.0
