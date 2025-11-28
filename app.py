import streamlit as st
import datetime
import utils
from pathlib import Path
import numpy as np
import pandas as pd
import io
import plotly.express as px
from utils import (ensure_session_df, categorize_description, parse_upload, style_money,)

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide", initial_sidebar_state="expanded")

#Header
st.markdown("""
            <h1 style='text-align:center; color:#4CAF50;'>💰 Personal Finance & Expense Tracker</h1>
            <p style='text-align:center; font-size:18px;'>
            Track expenses, upload CSVs, visualize spending, and manage your money better.
            </p><br>
        """, unsafe_allow_html=True)

df = ensure_session_df()

#Sidebar

st.sidebar.header("🔧 Options")
menu = st.sidebar.radio("Select", ["➕ Add Transaction", "📤 Upload CSV", "📊 Dashboard", "📁 View All"])

# ADD TRANSACTION 
if menu == "➕ Add Transaction":
    st.subheader("Add New Transaction")

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", datetime.date.today())
        desc = st.text_input("Description")
        amount = st.number_input("Amount (₹)", min_value=1.0, step=0.5)
    with col2:
        ttype = st.selectbox("Type", ["Expense", "Income"])
        category = st.selectbox(
        "Category",
        ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
    )

    if st.button("Add"):
        category = categorize_description(desc)

        new_row = pd.DataFrame([{
            "Date": pd.to_datetime(date),
            "Description": desc,
            "category": category,
            "Amount": amount,
            "Type": ttype
        }])

        st.session_state["transactions_df"] = pd.concat([df, new_row], ignore_index=True)

        st.success("Transaction added successfully!")

# UPLOAD CSV 
elif menu == "📤 Upload CSV":
    st.subheader("Upload Bank Statement CSV")

    uploaded_file = st.file_uploader("Choose CSV File", type=["csv"])
    if uploaded_file:
        try:
            new_data = parse_upload(uploaded_file)
            new_data["category"] = new_data["Description"].apply(categorize_description)

            st.session_state["transactions_df"] = pd.concat([df, new_data], ignore_index=True)

            st.success("CSV uploaded and processed successfully!")

        except Exception as e:
            st.error(str(e))

#Dashboard
elif menu == "📊 Dashboard":

    if df.empty:
        st.warning("No transactions yet. Add or upload to see dashboard.")
    else:
        st.subheader("📊 Financial Dashboard")

        # Summary cards
        col1, col2, col3 = st.columns(3)

        total_income = df[df["Type"] == "Income"]["Amount"].sum()
        total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
        net_savings = total_income - total_expense

        col1.metric("Total Income", style_money(total_income))
        col2.metric("Total Expense", style_money(total_expense))
        col3.metric("Net Savings", style_money(net_savings))

        # Charts
        st.write("### 📌 Category-wise Spending")

        category_expense = df[df["Type"] == "Expense"].groupby("category")["Amount"].sum()

        fig = px.pie(
            names=category_expense.index,
            values=category_expense.values,
            title="Expense by Category",
        )
        st.plotly_chart(fig, use_container_width=True)


# ----------------------------- VIEW ALL --------------------------------
elif menu == "📁 View All":
    st.subheader("All Transactions")

    if df.empty:
        st.info("No data available.")
    else:
        st.dataframe(df)

st.markdown("---")
st.markdown("Built with ❤️")