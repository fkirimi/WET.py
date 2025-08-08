💧 WET 3.0 — Weekly Expense Tracker
=============================================
"Welcome to WET; because Money is a flow"

A simple, local-first app to track your money weekly, set budgets, and visualize your financial health — built with Python + Streamlit.

⚙Features
=============================================
1- Money Tracking
-

Record transactions (income & expense)

Includes: date, week, category, subcategory, payment method, fees

2- Budgets
-
Set weekly/monthly budgets per category

Progress bars & color-coded comparisons

3- Dashboard
-
Real-time summaries (inflow, outflow, surplus)

Pie charts, bar charts, and net worth health indicator (✅ / ❌)

4- Data Management
-
Local storage in JSON files

CSV import/export

Opening balance setup

Quick Start
===========================================
bash
Copy
Edit
# 1. Install dependencies
pip install streamlit pandas plotly

# 2. Run the app
streamlit run app.py
Your data will be saved inside the WET 3.0/ folder

Files:
-

transactions.json

budgets.json

categories.json

transactions_export.csv

Tech Stack
-
Framework: Streamlit

Language: Python

Libraries: pandas, plotly, json, datetime

Data: Stored locally, no external database needed

Navigation
=================================================
Home – Add/view transactions

Budget – Set, edit, and analyze category budgets

Honey Pot – Net worth tracking, savings goals, and cashflow charts

📁 File Structure
-
pgsql
Copy
Edit
WET 3.0/
├── categories.json
├── budgets.json
├── transactions.json
├── transactions_export.csv

Contribute / Feedback
-
Feel free to fork, open issues, or submit PRs! 
Feedback and improvements are welcome.

