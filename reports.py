"""
===========================================================
CLI Expense Tracker

File: reports.py

Description:
Generates statistics, breakdowns, and exportable reports for
stored expenses.

Author: Kunal Kirtak
===========================================================
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional

from expense import Expense

logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# Total Spending
# ----------------------------------------------------------

def calculate_total(expenses: List[Expense]) -> float:
    """Calculate the total amount spent."""

    return round(sum(expense.amount for expense in expenses), 2)


# ----------------------------------------------------------
# Average Expense
# ----------------------------------------------------------

def calculate_average(expenses: List[Expense]) -> float:
    """Calculate the average expense amount."""

    if not expenses:
        return 0.0

    return round(mean(expense.amount for expense in expenses), 2)


# ----------------------------------------------------------
# Highest Expense
# ----------------------------------------------------------

def highest_expense(expenses: List[Expense]) -> Optional[Expense]:
    """Return the single highest expense, or None if the list is empty."""

    if not expenses:
        return None

    return max(expenses, key=lambda expense: expense.amount)


# ----------------------------------------------------------
# Lowest Expense
# ----------------------------------------------------------

def lowest_expense(expenses: List[Expense]) -> Optional[Expense]:
    """Return the single lowest expense, or None if the list is empty."""

    if not expenses:
        return None

    return min(expenses, key=lambda expense: expense.amount)


# ----------------------------------------------------------
# Category Summary
# ----------------------------------------------------------

def category_summary(expenses: List[Expense]) -> Dict[str, float]:
    """
    Return spending grouped by category, sorted highest to
    lowest spend so the biggest spending areas surface first.
    """

    summary: Dict[str, float] = defaultdict(float)

    for expense in expenses:
        summary[expense.category] += expense.amount

    return dict(sorted(summary.items(), key=lambda pair: pair[1], reverse=True))


# ----------------------------------------------------------
# Payment Method Summary
# ----------------------------------------------------------

def payment_summary(expenses: List[Expense]) -> Dict[str, float]:
    """
    Return spending grouped by payment method, sorted highest
    to lowest spend.
    """

    summary: Dict[str, float] = defaultdict(float)

    for expense in expenses:
        summary[expense.payment_method] += expense.amount

    return dict(sorted(summary.items(), key=lambda pair: pair[1], reverse=True))


# ----------------------------------------------------------
# Monthly Summary
# ----------------------------------------------------------

def monthly_summary(expenses: List[Expense]) -> Dict[str, float]:
    """Return spending grouped by month (YYYY-MM), sorted chronologically."""

    summary: Dict[str, float] = defaultdict(float)

    for expense in expenses:
        month = expense.expense_date[:7]
        summary[month] += expense.amount

    return dict(sorted(summary.items()))


# ----------------------------------------------------------
# Expense Statistics
# ----------------------------------------------------------

def generate_statistics(expenses: List[Expense]) -> Dict[str, object]:
    """Generate the core set of dashboard statistics."""

    highest = highest_expense(expenses)
    lowest = lowest_expense(expenses)
    categories = category_summary(expenses)

    return {
        "Total Expenses": len(expenses),
        "Total Spending": calculate_total(expenses),
        "Average Expense": calculate_average(expenses),
        "Highest Expense": highest.amount if highest else 0,
        "Highest Expense Title": highest.title if highest else "-",
        "Lowest Expense": lowest.amount if lowest else 0,
        "Lowest Expense Title": lowest.title if lowest else "-",
        "Top Category": next(iter(categories), "-"),
    }


# ----------------------------------------------------------
# Export Report
# ----------------------------------------------------------

def export_report(
    expenses: List[Expense],
    filename: str = "expense_report.txt",
) -> Path:
    """
    Export a full text report (summary, category / payment /
    monthly breakdowns, and the complete expense list) to disk.

    Returns
    -------
    Path
        Location of the generated report file.
    """

    report_path = Path(filename)

    stats = generate_statistics(expenses)
    category = category_summary(expenses)
    payment = payment_summary(expenses)
    monthly = monthly_summary(expenses)

    with report_path.open("w", encoding="utf-8") as file:

        file.write("=" * 55 + "\n")
        file.write("CLI EXPENSE TRACKER REPORT\n")
        file.write("=" * 55 + "\n\n")

        file.write("SUMMARY\n")
        file.write("-" * 30 + "\n")
        for key, value in stats.items():
            file.write(f"{key}: {value}\n")
        file.write("\n")

        file.write("CATEGORY SUMMARY\n")
        file.write("-" * 30 + "\n")
        for category_name, amount in category.items():
            file.write(f"{category_name:<15}₹{amount:.2f}\n")
        file.write("\n")

        file.write("PAYMENT SUMMARY\n")
        file.write("-" * 30 + "\n")
        for payment_name, amount in payment.items():
            file.write(f"{payment_name:<15}₹{amount:.2f}\n")
        file.write("\n")

        file.write("MONTHLY SUMMARY\n")
        file.write("-" * 30 + "\n")
        for month, amount in monthly.items():
            file.write(f"{month:<15}₹{amount:.2f}\n")
        file.write("\n")

        file.write("ALL EXPENSES\n")
        file.write("-" * 30 + "\n")
        for expense in expenses:
            file.write(str(expense) + "\n")

    logger.info("Expense report exported to %s", report_path)

    return report_path


# ----------------------------------------------------------
# Print Dashboard
# ----------------------------------------------------------

def print_dashboard(expenses: List[Expense]) -> None:
    """Display the dashboard (summary + breakdowns) in the terminal."""

    stats = generate_statistics(expenses)

    print("=" * 60)
    print("EXPENSE DASHBOARD")
    print("=" * 60)

    for key, value in stats.items():
        print(f"{key:<25}: {value}")

    print("\nCATEGORY SUMMARY")
    print("-" * 40)
    for category, amount in category_summary(expenses).items():
        print(f"{category:<20}₹{amount:.2f}")

    print("\nPAYMENT METHOD SUMMARY")
    print("-" * 40)
    for payment, amount in payment_summary(expenses).items():
        print(f"{payment:<20}₹{amount:.2f}")

    print("\nMONTHLY SUMMARY")
    print("-" * 40)
    for month, amount in monthly_summary(expenses).items():
        print(f"{month:<20}₹{amount:.2f}")


# ----------------------------------------------------------
# Standalone Testing
# ----------------------------------------------------------

if __name__ == "__main__":

    from file_handler import get_all_expenses

    expenses = get_all_expenses()

    print_dashboard(expenses)

    report = export_report(expenses)

    print("\nReport saved to:", report)
