import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

from datetime import datetime


# Ensure a folder named "WET 3.0" exists
WET_FOLDER = "WET 3.0"
os.makedirs(WET_FOLDER, exist_ok=True)

# File paths
CATEGORY_FILE = os.path.join(WET_FOLDER, "categories.json")
TRANSACTION_FILE = os.path.join(WET_FOLDER, "saved_transactions.json")
TRANSACTION_JSON = os.path.join(WET_FOLDER, "transactions.json")
TRANSACTION_CSV = os.path.join(WET_FOLDER, "transactions_export.csv")
BUDGET_FILE = os.path.join(WET_FOLDER, "budgets.json")
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
# Define the expected export column order
EXPORT_COLUMNS = [
    "date", "week", "amount(kes)", "transaction fees", "transaction type",
    "category", "subcategory", "payment method",
    "item description (money in)", "item description (money out)"
]

# Initialize files with empty lists
for file_path in [TRANSACTION_JSON, BUDGET_FILE, CATEGORY_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)
        st.sidebar.write(
            f"Transaction file: {os.path.exists(TRANSACTION_JSON)},"
            f"Size: {os.path.getsize(TRANSACTION_JSON)} bytes")

# Initialize categories if not already set
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Savings & Investment": {},
        "Loan Debt Repayment": {},
        "Housing & Rent": {},
        "Food & Beverages": {},
        "Shopping": {},
        "Entertainment": {},
        "Gifts & Donations": {},
        "Transport": {},
        "Debtors lent out": {},
        "Miscellaneous": {},
        "Utilities": {},
        "Personal Care": {},
        "Health": {},
        "Education": {},
        "Reimbursement": {},
    }

dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if not dark_mode:
    st.markdown("""
        <style>
        .stApp {
            filter: invert(90%) hue-rotate(180deg);
        }
        img {
            filter: invert(1) hue-rotate(180deg);
        }
        </style>
    """, unsafe_allow_html=True)
# Initialize page if not already set
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar layout
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#20B2AA;'>Weekly Expense Tracker (WET)</h1>",
                unsafe_allow_html=True)

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_week = now.isocalendar().week
    current_date = now.strftime("%A, %d %B %Y")

    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-between; align-items: center'>
            <div style='text-align: center; width: 100%'>
                <h3>{current_date}</h3>
                <h5 style='color:#2E86C1;'>{current_time}</h5>
                <h5 style='position: absolute; top: 10px; right: 20px;'>Week {current_week}</h5>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("<div style='margin-bottom: 10px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button("HOME"):
            st.session_state.page = "Home"
    with col2:
        if st.button("BUDGET"):
            st.session_state.page = "Budget"
    with col3:
        if st.button("HONEY POT"):
            st.session_state.page = "Honey Pot"

    st.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)


def standardize_columns(df):
    # Clean and rename using STANDARD_COLUMNS
    df.columns = [col.strip() for col in df.columns]
    df.rename(columns={col: STANDARD_COLUMNS.get(col, col) for col in df.columns}, inplace=True)
    print(df.columns)

    # Merge duplicate columns if needed
    if "amount(kes)" not in df.columns:
        if "amount (kes)" in df.columns:
            df["amount(kes)"] = df["amount (kes)"]
            df.drop(columns=["amount (kes)"], inplace=True)

    return df
def validate_columns(df, required_cols):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.warning(f"Missing columns: {', '.join(missing)}")
def load_categories():
    """
    Load subcategories from the categories.json file

    Returns:
        dict: A dictionary where keys are main categories and values are lists of subcategories
    """
    try:
        if os.path.exists(CATEGORY_FILE):
            with open(CATEGORY_FILE, 'r') as file:

                categories_data = json.load(file)

                # Handle different possible structures of the JSON file
                if isinstance(categories_data, dict):
                    # Standard case: dictionary with categories as keys
                    return categories_data
                elif isinstance(categories_data, list):
                    # If it's a list, convert to the expected dictionary format
                    st.warning("Categories file format is a list, converting to dictionary format.")
                    converted_dict = {}
                    for item in categories_data:
                        if isinstance(item, dict):
                            converted_dict.update(item)
                        else:
                            # Handle other list item types if needed
                            pass
                    return converted_dict
                else:
                    st.error("Unexpected format in categories file.")
                    return {}
        else:
            st.error("Categories file not found.")
            return {}
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Error loading categories: {str(e)}")
        return {}

def get_all_subcategories():
    """
    Get all subcategories across all categories

    Returns:
        list: A flattened list of all subcategories
    """
    categories_data = load_categories()
    all_subcategories = []
    for subcats in categories_data.values():
        all_subcategories.extend(subcats)
    return sorted(all_subcategories)
def get_category_for_subcategory(subcategory):
    """
    Find which main category a subcategory belongs to

    Args:
        subcategory (str): The subcategory to find the parent for

    Returns:
        str: The main category that contains this subcategory
    """
    categories_data = load_categories()
    for category, subcats in categories_data.items():
        if subcategory in subcats:
            return category
    return None
# Helper function to get subcategories for a specific category
def get_subcategories_for_category(category):
    """
    Get subcategories for a specific category

    Args:
        category (str): The main category to get subcategories for

    Returns:
        list: List of subcategories for the specified category
    """
    categories_data = load_categories()
    return categories_data.get(category, [])
# Load categories from JSON file
def load_income_categories():
    try:
        if os.path.exists(CATEGORY_FILE):
            with open(CATEGORY_FILE, 'r') as file:
                categories_data = json.load(file)
                return categories_data.get("income_categories", [])
        else:
            # Return default categories if file doesn't exist
            return [
                "Bonus", "Debtors", "Dividends", "Honorarium", "Loan",
                "Reimbursement", "Salary", "Savings", "Scholarship Fund",
                "Stipend", "Windfall"
            ]
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Error loading categories: {str(e)}")
        # Return default categories on error
        return [
            "Bonus", "Debtors", "Dividends", "Honorarium", "Loan",
            "Reimbursement", "Salary", "Savings", "Scholarship Fund",
            "Stipend", "Windfall"
        ]
def load_expense_categories():
    if "categories" not in st.session_state:
        if os.path.exists(CATEGORY_FILE):

            with open(CATEGORY_FILE, "r") as f:
                st.session_state.categories = json.load(f)
        else:
            st.session_state.categories = {
                "Food & Beverages": ["Supermarket", "Market", "Take-out"],
                "Transport": ["Fuel", "Public Transport", "Cab/taxi", "Parking", "transit fee"],
                "Housing & Rent": ["Rent", "Maintenance", "Cleaning"],
                "Shopping": ["electronics", "furniture & decor", "household items", "plants"],
                "Utilities": ["Electricity", "Water", "Internet", "Airtime"],
                "Health": ["Hospital", "Medicine", "Insurance"],
                "Education": ["School fees", "Books", "Tuition"],
                "Entertainment": ["Netflix", "Outings", "Events"],
                "Personal Care": ["Salon", "Toiletries", "Apparel"],
                "Savings & Investment": ["Mshwari", "Sacco", "Chama", "MMF"],
                "Debt Repayment": ["Loan", "Fuliza", "loan expenses"],
                "Lent out": ["private loans", "interest"],
                "Gifts & Donations": ["Charity", "Family Support"],
                "Miscellaneous": ["Other", "Transaction charges"]
            }
            with open(CATEGORY_FILE, "w") as f:
                json.dump(st.session_state.categories, f, indent=4)
def save_transaction(transaction):
    # Initialize 'transactions' as a list if it doesn't exist or is misconfigured
    if 'transactions' not in st.session_state or not isinstance(st.session_state['transactions'], list):
        st.session_state['transactions'] = []
    # Append the new transaction
    st.session_state['transactions'].append(transaction)
def load_json_data(file_path=TRANSACTION_FILE):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Handle case where data is a dictionary instead of a list
            if isinstance(data, dict):
                # Convert dictionary values to a list
                return list(data.values())
            return data
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return []
def save_json_data(file_path, data):
    """
    Save data to a JSON file
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {str(e)}")
def load_budgets_from_file():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            data = json.load(f)

            if isinstance(data, dict):
                st.session_state.budgets = data
            else:
                st.session_state.budgets = {}  # fallback if file is corrupted or list
    else:
        st.session_state.budgets = {}
def create_budget():

    with st.form(key=f"add_budget_form_{period_key}"):
        st.subheader(f"Add Budget for {period_key}")
        category = st.selectbox("Category", options=list(st.session_state.get("categories", {}).keys()))
        selected_subcategory = st.selectbox("Subcategory", options=st.session_state["categories"].get(category, []))
        amount = st.number_input("Amount (Kes)", min_value=0, step=100)

        if st.form_submit_button("Add to Budget"):
            new_item = {
                'category': category,
                'subcategory': selected_subcategory,
                'amount (kes)': amount
            }
            period_data['items'].append(new_item)
            st.success("Budget item added!")
def save_budgets():
    with open(BUDGET_FILE, "w") as f:
        json.dump(st.session_state.budgets, f, indent=4)
def deduplicate_columns(columns):
    seen = {}
    new_cols = []
    for col in columns:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}.{seen[col]}")
    return new_cols
def classify_transaction_type(row):
    money_in = row.get('item description (money in)', None)
    money_out = row.get('item description (money out)', None)

    if pd.notna(money_in) and str(money_in).strip() != '':
        return 'Money In'
    elif pd.notna(money_out) and str(money_out).strip() != '':
        return 'Money Out'
    else:
        return 'Unknown'

# Load transactions from file
transactions = load_json_data(TRANSACTION_FILE)

def export_transactions_to_csv():
    # Load transactions from file
    transactions = load_json_data(TRANSACTION_FILE)

    # Warn if none found
    if not transactions:
        st.warning("No transactions found to export.")
        return

    # Convert to DataFrame and standardize
    df = pd.DataFrame(transactions)
    df = standardize_columns(df)

    # Use the predefined EXPORT_COLUMNS instead of redefining
    desired_order = EXPORT_COLUMNS

    # Ensure all columns from desired_order exist
    for col in desired_order:
        if col not in df.columns:
            if "description" in col or col == "payment method":
                df[col] = ""
            elif col == "date":
                df[col] = pd.NaT
            elif col == "week":
                # Will be calculated from date below
                continue
            else:
                df[col] = 0.0

    # Calculate week from date if date exists
    if "date" in df.columns:
        # Convert to datetime first
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        # Calculate week number (ISO week)
        df["week"] = df["date"].dt.isocalendar().week
        # Format the date column as string
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    else:
        # If no date column, create empty week column
        df["week"] = ""

    # Handle case where week calculation failed for some rows
    df["week"] = df["week"].fillna("").astype(str)

    # Reorder columns safely
    df = df[desired_order]

    # Convert to CSV
    csv_data = df.to_csv(index=False)

    # Let the user download it
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="transactions_export.csv",
        mime="text/csv"
    )


# Main page logic
if st.session_state.page == "Home":
    st.title("Transaction Log")
    st.write("Record your week's expenditure and income.")
    st.markdown("---")

    # Load all categories and subcategories
    all_categories = load_categories()

    # Get main categories for the dropdown
    if isinstance(all_categories, dict):
        main_categories = sorted(list(all_categories.keys()))
    else:
        # If all_categories is a list, extract keys from the dictionaries in the list
        main_categories = []
        for item in all_categories:
            if isinstance(item, dict):
                main_categories.extend(item.keys())
        main_categories = sorted(list(set(main_categories)))  # Remove duplicates

    # Load income categories from file
    income_categories = sorted(load_income_categories())

    payment_methods = ["Cash", "M-Pesa", "Bank Transfer", "Credit Card", "Debit Card", "Other"]

    with st.form(key="expense_form"):
        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None

        transaction_type = st.selectbox("Transaction type", ["Money in (debit)", "Money out (credit)"])
        select = st.form_submit_button("select")
        date = st.date_input("Transaction Date", value=datetime.today())
        amount = st.number_input("Amount(Kes)", min_value=0.0, format="%.2f")
        transaction_fees = st.number_input("Transaction Fees", min_value=0.0, format="%.2f", value=0.0)
        payment_method = st.selectbox("Payment Method", payment_methods)

        if transaction_type == "Money in (debit)":
            category = st.selectbox("Category", income_categories)
            subcategory = st.text_input("Sub Category", "None")
            item_description = st.text_input("Item Description (Money In)", "")
        else:
            # Category selection with subcategories
            main_category = st.selectbox("Main Category", main_categories)
            select_main_category = st.form_submit_button("Select category")
            if select_main_category:
                # Get subcategories for the selected main category
                # Get subcategories for the selected main category
                subcategories = get_subcategories_for_category(main_category)

                # Subcategory selection - this is what was missing
                if subcategories:
                    # Get subcategories for the selected main category
                    subcategories = get_subcategories_for_category(main_category)

                    subcategory = st.selectbox("Sub Category", subcategories)

            item_description = st.text_input("Item Description (money out)", "")

        submitted = st.form_submit_button("Save Transaction")
        # Process form submission INSIDE the form block
        if submitted:

            try:
                # Defensive check: ensure subcategory is defined
                if not subcategory:
                    st.error("Please select a subcategory.")
                else:
                    week = date.isocalendar()[1]
                    transactions = load_json_data(TRANSACTION_FILE)

                    # Ensure transactions is a list
                    if not isinstance(transactions, list):
                        transactions = []

                    transaction = {
                        "date": date.strftime("%Y-%m-%d"),
                        "week": week,
                        "amount(kes)": amount,
                        "transaction fees": transaction_fees,
                        "transaction type": "debit" if transaction_type == "Money in (debit)" else "credit",
                        "category": main_category,
                        "subcategory": subcategory,
                        "payment method": payment_method,
                        "item description (money in)": item_description if transaction_type == "Money in (debit)" else "",
                        "item description (money out)": item_description if transaction_type == "Money out (credit)" else ""
                    }

                    transactions.append(transaction)
                    save_json_data(TRANSACTION_FILE, transactions)
                    st.success("Transaction saved successfully!")

            except Exception as e:
                st.error(f"An error occurred: {e}")





    st.sidebar.subheader("Export saved transactions")

    if st.sidebar.button("Export to CSV"):
        export_transactions_to_csv()

    # 8. MOVE SUMMARY TO SIDEBAR (OUTSIDE FORM)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Financial Summary")

    transactions = load_json_data(TRANSACTION_FILE)

    if transactions:
        # Load transactions into DataFrame
        df = pd.DataFrame(transactions)

        # Standardize column names once
        df = standardize_columns(df)

        # Ensure amount is numeric
        if 'amount(kes)' in df.columns:
            df['amount(kes)'] = pd.to_numeric(df['amount(kes)'], errors='coerce')

        # Filter out invalid rows
        df = df.dropna(subset=["amount(kes)"])

        # Normalize relevant columns for consistent filtering
        if 'transaction type' in df.columns:
            df["transaction type"] = df["transaction type"].str.strip().str.lower()
        if 'category' in df.columns:
            df["category"] = df["category"].str.strip().str.lower()

        # Calculate summary statistics
        if 'transaction type' in df.columns and 'amount(kes)' in df.columns:
            # Use consistent case for filtering
            total_inflow = df[df["transaction type"].str.contains("debit|money in", case=False, na=False)][
                "amount(kes)"].sum()
            total_outflow = df[df["transaction type"].str.contains("credit|money out", case=False, na=False)][
                "amount(kes)"].sum()

            # Look for savings in both income and expense categories
            total_saved = df[
                (df["category"].str.contains("savings", case=False, na=False)) |
                (df["subcategory"].str.contains("savings", case=False, na=False))
                ]["amount(kes)"].sum()

            surplus = total_inflow - total_outflow

            st.sidebar.markdown(f"**Total Inflow (Kes):** {total_inflow:,.2f}")
            st.sidebar.markdown(f"**Total Outflow (Kes):** {total_outflow:,.2f}")
            st.sidebar.markdown(f"**Surplus (Kes):** {surplus:,.2f}")
            st.sidebar.markdown(f"**Total Saved (Kes):** {total_saved:,.2f}")

            st.sidebar.markdown("---")

            # Expense breakdown
            expense_data = df[df["transaction type"].str.contains("credit|money out", case=False, na=False)]

            if not expense_data.empty and 'category' in expense_data.columns:
                # Create expense pie chart
                fig_expense_pie = px.pie(
                    expense_data,
                    names='category',
                    values='amount(kes)',
                    title='Expense Distribution by Category'
                )
                st.sidebar.plotly_chart(fig_expense_pie, use_container_width=True)
            else:
                st.sidebar.info("No expenses recorded yet for category breakdown.")

            # Income breakdown
            income_data = df[df["transaction type"].str.contains("debit|money in", case=False, na=False)]

            if not income_data.empty and 'category' in income_data.columns:
                # Create income pie chart
                fig_income_pie = px.pie(
                    income_data,
                    names='category',
                    values='amount(kes)',
                    title='Income by Category',
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                st.sidebar.plotly_chart(fig_income_pie, use_container_width=True)
            else:
                st.sidebar.info("No income recorded yet for category breakdown.")
        else:
            st.sidebar.warning("Required columns not found in data")
    else:
        st.sidebar.warning("No transactions found")

elif st.session_state.page == "Budget":
    st.title("Budget Management")
    load_expense_categories()
    load_budgets_from_file()
    current_year = datetime.now().year
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    selected_month = st.selectbox(
        "Select Month", months, index=datetime.now().month - 1, key="select_month"
    )

    weeks = [f"Week {i}" for i in range(1, 53)]
    selected_week = st.selectbox(
        "Select Week", weeks, index=min(datetime.now().isocalendar().week - 1, 51), key="select_week"
    )

    period_key = f"{selected_month} {current_year} - {selected_week}"

    if period_key not in st.session_state.budgets:
        st.session_state.budgets[period_key] = {
            'overall_budget': 0,
            'items': []
        }

    st.session_state.current_period = period_key
    period_data = st.session_state.budgets[period_key]

    # Overall budget input
    period_data['overall_budget'] = st.number_input(
        f"Set overall weekly budget for {period_key} (Kes):",
        min_value=0,
        step=1000,
        value=period_data['overall_budget'],
        key=f"overall_{period_key}"
    )
    create_budget()

    # Initialize session state
    if 'budgets' not in st.session_state:
        st.session_state.budgets = {}
    if 'current_period' not in st.session_state:
        st.session_state.current_period = ""

    categories = st.session_state.categories
    all_categories = list(categories.keys())
    fixed_categories = ['Housing & Rent', 'Utilities', 'Health',
                        'Savings & Investment', 'Debt Repayment']

    st.title("Weekly financial analysis")
    # Period selection
    current_year = datetime.now().year
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    selected_month = st.selectbox(
        "Select Month", months,
        index=datetime.now().month - 1,
        key="select_month (budget_page)"
    )
    weeks = [f"Week {i}" for i in range(1, 53)]
    selected_week = st.selectbox(
        "Select Week", weeks,
        index=min(datetime.now().isocalendar().week - 1, 51),
        key = "select_week (budget_page)")

    period_key = f"{selected_month} {current_year} - {selected_week}"

    # Initialize period
    if period_key not in st.session_state.budgets:
        st.session_state.budgets[period_key] = {
            'overall_budget': 0,
            'items': []
        }

    st.session_state.current_period = period_key
    period_data = st.session_state.budgets[period_key]

    #--------

    # Edit budget items
    st.markdown("---")
    st.subheader(f"Edit Budget for {period_key}")
    if not period_data['items']:
        st.warning("No budget items to edit")
    else:
        df = pd.DataFrame(period_data['items'])
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            column_config={
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=all_categories
                ),
                "subcategory": st.column_config.SelectboxColumn(
                    "Subcategory",
                    options=[]
                ),
                "amount": st.column_config.NumberColumn(
                    "Amount (Kes)",
                    format="%d Kes",
                    min_value=0
                ),
            },
            key=f"budget_editor_{period_key}"
        )

        if st.button("Save Changes", key=f"save_{period_key}"):
            period_data['items'] = edited_df.to_dict('records')
            save_budgets()
            st.success("Budget updated!")

    # Clear budget items
    st.markdown("---")
    if st.button("Clear All Budget Items", key=f"clear_{period_key}"):
        period_data['items'] = []
        save_budgets()
        st.success("All budget items cleared!")

    # Track progress
    st.sidebar.subheader("Budget Progress")
    if period_data['items']:
        total_budgeted = sum(item['amount'] for item in period_data['items'])
        fixed_budgeted = sum(
            item['amount'] for item in period_data['items']
            if item['category'] in fixed_categories
        )
        variable_budgeted = sum(
            item['amount'] for item in period_data['items']
            if item['category'] not in fixed_categories
        )

        overall = period_data['overall_budget']
        total_percent = total_budgeted / overall if overall else 0
        fixed_percent = fixed_budgeted / overall if overall else 0
        variable_percent = variable_budgeted / overall if overall else 0

        st.sidebar.subheader("Weekly Allocation")
        st.sidebar.progress(min(total_percent, 1.0))
        st.sidebar.caption(f"Kes {total_budgeted:,.0f} of Kes {overall:,.0f} allocated")

        st.sidebar.subheader("Fixed Expenses")
        st.sidebar.progress(min(fixed_percent, 1.0))
        st.sidebar.caption(f"Kes {fixed_budgeted:,.0f} allocated")

        st.sidebar.subheader("Variable Expenses")
        st.sidebar.progress(min(variable_percent, 1.0))
        st.sidebar.caption(f"Kes {variable_budgeted:,.0f} allocated")

        # Budget feedback
        allocation_percent = total_budgeted / overall if overall else 0
        if allocation_percent < 0.7:
            st.sidebar.info(
                "You're allocating less than 70% of your budget. Consider increasing savings or investments.")
        elif allocation_percent > 1.0:
            st.sidebar.warning("You've allocated more than 100% of your budget! Review your expenses.")
        else:
            st.sidebar.success("Good job! Your budget allocation is within your weekly limit.")

        if fixed_budgeted > 0.6 * overall:
            st.sidebar.warning("Your fixed expenses exceed 60% of your budget. This may limit financial flexibility.")
    else:
        st.sidebar.info("Add budget items to see progress")

elif st.session_state.page == "Honey Pot":
    st.title("Honey Pot")
    st.write("Financial dashboard for tracking net worth and cashflow")

    # 1. Load data with consistent column names using your custom function
    transactions = load_json_data(TRANSACTION_FILE)

    if transactions:
        df = pd.DataFrame(transactions)
        # Standardize column names
        df = standardize_columns(df)
    else:
        df = pd.DataFrame(columns=[
            "date", "week", "amount(kes)", "transaction type",
            "category", "subcategory", "transaction fees",
            "payment method", "item description (money in)", "item description (money out)"
        ])

    # 2. Set opening balance - ensure consistent naming
    st.sidebar.subheader("Set Opening Balance")
    opening_bal = st.sidebar.number_input("Enter Opening Balance (Kes)",
                                          min_value=0.0, format="%.2f",
                                          key="opening_bal")

    if st.sidebar.button("Save Opening Balance"):
        # Store opening balance in session state instead of adding as a transaction
        st.session_state.opening_balance = opening_bal
        st.sidebar.success("Opening balance saved!")

    # Get opening balance from session state or use 0 as default
    opening_balance = st.session_state.get('opening_balance', 0.0)

    # 3. Ensure standardization after any modifications
    df = standardize_columns(df)

    # 4. Add missing columns if they don't exist
    required_columns = [
        "date", "week", "amount(kes)", "transaction type",
        "category", "subcategory", "transaction fees",
        "payment method", "item description (money in)", "item description (money out)"
    ]
    for col in required_columns:
        if col not in df.columns:
            if "description" in col:
                df[col] = ""
            elif col == "date":
                df[col] = pd.NaT
            else:
                df[col] = 0.0

    # 5. Safe calculation of metrics
    try:
        # Normalize transaction type for consistent filtering
        if 'transaction type' in df.columns:
            df["transaction type"] = df["transaction type"].str.strip().str.lower()

        # Create filtered dataframes safely with case-insensitive matching
        expense_df = df[df["transaction type"].str.contains("credit|money out", case=False, na=False)].copy()
        income_df = df[df["transaction type"].str.contains("debit|money in", case=False, na=False)].copy()

        # Convert amounts to numeric
        if 'amount(kes)' in df.columns:
            df['amount(kes)'] = pd.to_numeric(df['amount(kes)'], errors='coerce')
        if 'transaction fees' in df.columns:
            df['transaction fees'] = pd.to_numeric(df['transaction fees'], errors='coerce')

        # Calculate metrics with NaN handling
        total_inflow = income_df["amount(kes)"].sum() if not income_df.empty else 0.0
        total_outflow = expense_df["amount(kes)"].sum() if not expense_df.empty else 0.0

        transaction_costs = df["transaction fees"].sum() if 'transaction fees' in df.columns else 0.0

        total_saved = expense_df[
            (expense_df["category"].str.contains("savings", case=False, na=False)) |
            (expense_df["subcategory"].str.contains("savings", case=False, na=False))
            ]["amount(kes)"].sum() if not expense_df.empty else 0.0

        net_worth = opening_balance + total_inflow - total_outflow - transaction_costs

        # 6. Display metrics safely
        st.subheader("Financial Summary")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Inflow", f"KSh {total_inflow:,.2f}")
        col2.metric("Total Outflow", f"KSh {total_outflow:,.2f}")
        col3.metric("Net Worth", f"KSh {net_worth:,.2f}",
                    delta=f"KSh {net_worth - opening_balance:,.2f} from opening")

        # Additional metrics
        st.metric("Total Saved", f"KSh {total_saved:,.2f}")
        st.metric("Total Transaction Fees", f"KSh {transaction_costs:,.2f}")

    except KeyError as e:
        st.error(f"Missing column in data: {e}")
        st.write("Current columns:", df.columns.tolist())
        # Set default values to prevent further errors
        total_inflow, total_outflow, transaction_costs, total_saved, net_worth = 0.0, 0.0, 0.0, 0.0, opening_balance

    # 7. Cashflow chart with safe column handling
    st.subheader("Monthly Cashflow Overview")
    if not df.empty and 'date' in df.columns:
        try:
            # Create a copy to avoid SettingWithCopyWarning
            chart_df = df.copy()

            # Convert and extract date parts
            chart_df['date'] = pd.to_datetime(chart_df['date'], errors='coerce')
            chart_df = chart_df.dropna(subset=['date'])
            chart_df['Month'] = chart_df['date'].dt.strftime('%Y-%m')

            # Group by month and transaction type
            monthly_data = chart_df.groupby(['Month', 'transaction type'])['amount(kes)'].sum().reset_index()

            # Pivot the data
            cashflow_data = monthly_data.pivot(
                index='Month',
                columns='transaction type',
                values='amount(kes)'
            ).reset_index().fillna(0)

            # Ensure required columns exist
            for col_type in ['debit', 'credit']:
                if col_type not in cashflow_data.columns:
                    cashflow_data[col_type] = 0

            # Rename columns
            cashflow_data.rename(columns={
                'debit': 'Income',
                'credit': 'Expense'
            }, inplace=True)

            # Calculate net cashflow
            cashflow_data['Net'] = cashflow_data['Income'] - cashflow_data['Expense']

            # Sort by month
            cashflow_data = cashflow_data.sort_values('Month')

            # Create chart
            fig = px.bar(
                cashflow_data,
                x='Month',
                y=['Income', 'Expense'],
                title='Monthly Income vs Expenses',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Add net cashflow line
            fig.add_trace(px.line(cashflow_data, x='Month', y='Net',
                                  color_discrete_sequence=['black']).data[0])
            fig.update_layout(showlegend=True)

        except Exception as e:
            st.error(f"Error processing cashflow data: {e}")
            import traceback

            st.write(traceback.format_exc())
    else:
        st.warning("No transaction data available for chart")

    # 8. Recent transactions with safe column handling
    st.subheader("Recent Transactions")
    if not df.empty:
        try:
            # Create safe copy and format
            recent_df = df.copy()
            recent_df['date'] = pd.to_datetime(recent_df['date'], errors='coerce').dt.strftime('%b %d, %Y')
            recent_df = recent_df.sort_values('date', ascending=False).head(10)

            # Display with essential columns only
            display_cols = ['date', 'transaction type', 'amount(kes)', 'category', 'payment method']
            # Add appropriate description column
            if 'transaction type' in recent_df.columns:
                display_cols.append('item description (money in)' if
                                    recent_df['transaction type'].str.contains('debit').any() else
                                    'item description (money out)')

            display_cols = [col for col in display_cols if col in recent_df.columns]

            st.dataframe(
                recent_df[display_cols].rename(columns={
                    'amount(kes)': 'Amount',
                    'item description (money in)': 'Description',
                    'item description (money out)': 'Description'
                })
            )
        except Exception as e:
            st.error(f"Error displaying recent transactions: {e}")
    else:
        st.info("No transactions available")
