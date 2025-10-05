import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

CSV_FILE = "expenses.csv"

# Ensure file exists
def ensure_csv():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
        df.to_csv(CSV_FILE, index=False)
    return df

def load_data():
    df = ensure_csv()
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Expense Tracker", page_icon="💰")
st.title("💰 Personal Expense Tracker")
st.write("Track your expenses, view summaries, and visualize your spending trends.")

menu = ["Add Expense", "View All", "Summary"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- ADD EXPENSE ----------------
if choice == "Add Expense":
    st.subheader("➕ Add a New Expense")

    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Food", "Rent", "Travel", "Bills", "Entertainment", "Other"])
    amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
    description = st.text_input("Description (optional)")

    if st.button("Add Expense"):
        new_row = {"Date": date, "Category": category, "Amount": amount, "Description": description}
        df = load_data()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("✅ Expense added successfully!")

# ---------------- VIEW ALL ----------------
elif choice == "View All":
    st.subheader("📋 All Expenses")
    df = load_data()
    if df.empty:
        st.warning("No expenses recorded yet.")
    else:
        st.dataframe(df.sort_values("Date", ascending=False))
        total = df["Amount"].sum()
        st.info(f"💵 Total Spent: ₹{total:.2f}")

# ---------------- SUMMARY ----------------
elif choice == "Summary":
    st.subheader("📊 Expense Summary")
    df = load_data()

    if df.empty:
        st.warning("No data to summarize.")
    else:
        period = st.selectbox("Select Period", ["Weekly (7 days)", "Monthly (30 days)", "All Time"])
        if period == "Weekly (7 days)":
            start_date = datetime.today() - pd.Timedelta(days=7)
            filtered = df[df["Date"] >= start_date]
        elif period == "Monthly (30 days)":
            start_date = datetime.today() - pd.Timedelta(days=30)
            filtered = df[df["Date"] >= start_date]
        else:
            filtered = df

        if filtered.empty:
            st.warning("No expenses found for this period.")
        else:
            total = filtered["Amount"].sum()
            st.write(f"**Total Spent:** ₹{total:.2f}")

            # CATEGORY-WISE PIE CHART
            cat_sum = filtered.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            ax1.pie(cat_sum, labels=cat_sum.index, autopct="%1.1f%%", startangle=90, counterclock=False)
            ax1.set_title("Spending by Category")
            st.pyplot(fig1)

            # DAILY EXPENSE BAR CHART
            daily_sum = filtered.groupby(filtered["Date"].dt.date)["Amount"].sum()
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.bar(daily_sum.index, daily_sum.values, color="skyblue")
            ax2.set_title("Daily Spending Trend")
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Amount (₹)")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

            # Show table
            st.dataframe(filtered.sort_values("Date", ascending=False))
