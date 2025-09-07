import streamlit as st
from datetime import datetime

def render_sidebar():
    st.sidebar.markdown("<h1 style='text-align:center; color:#20B2AA;'>Weekly Expense Tracker (WET)</h1>",
                        unsafe_allow_html=True)

    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_week = now.isocalendar().week
    current_date = now.strftime("%A, %d %B %Y")

    st.sidebar.markdown(
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

    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='margin-bottom: 10px'></div>", unsafe_allow_html=True)

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

    st.sidebar.markdown("<div style='margin-bottom: 20px'></div>", unsafe_allow_html=True)
    
    # Dark mode toggle
    dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
    return dark_mode
