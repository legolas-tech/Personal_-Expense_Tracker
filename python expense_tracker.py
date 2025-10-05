#!/usr/bin/env python3
"""
Personal Expense Tracker (CLI)
- Stores data to expenses.csv
- Add expenses, view all, weekly/monthly summaries, export CSV
Dependencies: pandas
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

CSV_FILE = "expenses.csv"
DATE_FMT = "%Y-%m-%d"

# Ensure CSV exists with correct headers
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "category", "amount", "description"])
        df.to_csv(CSV_FILE, index=False)

def load_df():
    ensure_csv()
    df = pd.read_csv(CSV_FILE, parse_dates=["date"])
    # Ensure types
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["category"] = df["category"].fillna("Other")
    df["description"] = df["description"].fillna("")
    return df

def save_df(df):
    df.to_csv(CSV_FILE, index=False, date_format=DATE_FMT)

def add_expense():
    print("\nAdd a new expense (leave description empty if none).")
    date_in = input(f"Date [{datetime.today().strftime(DATE_FMT)}] (YYYY-MM-DD): ").strip()
    if date_in == "":
        date = datetime.today().date()
    else:
        try:
            date = datetime.strptime(date_in, DATE_FMT).date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

    category = input("Category (food/rent/travel/bills/entertainment/other): ").strip()
    if category == "":
        category = "Other"

    amt_raw = input("Amount (numbers only): ").strip()
    try:
        amount = float(amt_raw)
    except:
        print("Invalid amount.")
        return

    desc = input("Description (optional): ").strip()

    df = load_df()
    new = {"date": pd.to_datetime(date), "category": category.title(), "amount": amount, "description": desc}
    df = df.append(new, ignore_index=True)
    save_df(df)
    print("Expense added.\n")

def view_all():
    df = load_df()
    if df.empty:
        print("\nNo expenses recorded yet.\n")
        return
    df_sorted = df.sort_values("date", ascending=False)
    print("\nAll expenses (latest first):\n")
    print(df_sorted.to_string(index=False, columns=["date", "category", "amount", "description"]))
    print()

def summary_period(days=None, month=None, year=None):
    """If days provided -> last `days` days summary.
       Else if month/year provided -> that month summary.
       Else -> error."""
    df = load_df()
    if df.empty:
        print("\nNo expenses to summarize.\n")
        return

    if days is not None:
        end = pd.Timestamp(datetime.today().date())
        start = end - pd.Timedelta(days=days-1)  # include today
        mask = (df["date"] >= start) & (df["date"] <= end)
        label = f"Last {days} days ({start.date()} to {end.date()})"
    else:
        # month & year
        start = pd.Timestamp(year=year, month=month, day=1)
        # compute end of month
        if month == 12:
            end = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
        else:
            end = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
        mask = (df["date"] >= start) & (df["date"] <= end)
        label = f"{start.strftime('%B %Y')}"

    sub = df.loc[mask]
    if sub.empty:
        print(f"\nNo expenses in {label}.\n")
        return

    total = sub["amount"].sum()
    count = len(sub)
    by_cat = sub.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)

    print(f"\nSummary for: {label}")
    print(f"Total expenses: ₹{total:.2f} across {count} entries")
    print("\nBy category:")
    for _, row in by_cat.iterrows():
        pct = (row["amount"] / total) * 100
        print(f"  - {row['category']}: ₹{row['amount']:.2f} ({pct:.1f}%)")
    print("\nTop 5 recent entries:")
    rec = sub.sort_values("date", ascending=False).head(5)
    print(rec.to_string(index=False, columns=["date", "category", "amount", "description"]))
    print()

def prompt_summary():
    print("\nChoose summary type:")
    print("1. Weekly (last 7 days)")
    print("2. Monthly (current month)")
    print("3. Monthly for specific month")
    choice = input("Enter choice [1/2/3]: ").strip()
    if choice == "1":
        summary_period(days=7)
    elif choice == "2":
        today = datetime.today()
        summary_period(month=today.month, year=today.year)
    elif choice == "3":
        mm = input("Enter month [1-12]: ").strip()
        yy = input("Enter year [e.g., 2025]: ").strip()
        try:
            m = int(mm); y = int(yy)
            if 1 <= m <= 12:
                summary_period(month=m, year=y)
            else:
                print("Invalid month.")
        except:
            print("Invalid inputs.")
    else:
        print("Invalid choice.")

def export_csv():
    path = input("Enter filename to export to (e.g., my_expenses.csv): ").strip()
    if path == "":
        print("No filename given.")
        return
    df = load_df()
    df.to_csv(path, index=False, date_format=DATE_FMT)
    print(f"Exported to {path}")

def interactive_menu():
    print("Welcome to Personal Expense Tracker")
    ensure_csv()
    while True:
        print("\nMenu:")
        print("1. Add expense")
        print("2. View all expenses")
        print("3. Weekly/Monthly summary")
        print("4. Export CSV")
        print("5. Exit")
        c = input("Choose option [1-5]: ").strip()
        if c == "1":
            add_expense()
        elif c == "2":
            view_all()
        elif c == "3":
            prompt_summary()
        elif c == "4":
            export_csv()
        elif c == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\nInterrupted. Bye.")
    except Exception as e:
        print("Error:", e)
