import json
import os
import streamlit as st
from config import CATEGORY_FILE, TRANSACTION_FILE, BUDGET_FILE

def load_json_data(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return list(data.values())
            return data
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return []

def save_json_data(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {str(e)}")

def load_categories():
    # Your existing load_categories function
    pass

def load_budgets_from_file():
    # Your existing load_budgets_from_file function
    pass

def save_budgets():
    # Your existing save_budgets function
    pass
