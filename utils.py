"""
===========================================================
CLI Expense Tracker

File: utils.py

Description:
Utility functions for input validation, formatting, and
console display used throughout the application.

Author: Kunal Kirtak
===========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from expense import Expense


# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------

DATE_FORMAT = "%Y-%m-%d"
LARGE_AMOUNT_THRESHOLD = 1_000_000.0


# ----------------------------------------------------------
# Clear Screen
# ----------------------------------------------------------

def clear_screen() -> None:
    """Print blank lines to visually separate screens."""

    print("\n" * 3)


# ----------------------------------------------------------
# Print Header
# ----------------------------------------------------------

def print_header(title: str) -> None:
    """Print a formatted section header."""

    print("=" * 60)
    print(title.center(60))
    print("=" * 60)


# ----------------------------------------------------------
# Pause
# ----------------------------------------------------------

def pause() -> None:
    """Wait until the user presses Enter."""

    input("\nPress Enter to continue...")


# ----------------------------------------------------------
# Validate Non-Empty String
# ----------------------------------------------------------

def get_non_empty_input(message: str) -> str:
    """Prompt repeatedly until a non-empty string is entered."""

    while True:

        value = input(message).strip()

        if value:
            return value

        print("Input cannot be empty.")


# ----------------------------------------------------------
# Confirmation Prompt
# ----------------------------------------------------------

def confirm_action(message: str) -> bool:
    """Ask the user to confirm an action with a Y/N prompt."""

    while True:

        choice = input(f"{message} (Y/N): ").strip().lower()

        if choice in ("y", "yes"):
            return True

        if choice in ("n", "no"):
            return False

        print("Please enter Y or N.")


# ----------------------------------------------------------
# Validate Positive Float
# ----------------------------------------------------------

def get_positive_float(message: str) -> float:
    """
    Prompt repeatedly until a valid positive float is entered.

    Flags unusually large values (e.g. an accidental extra
    zero) and asks the user to confirm before accepting them.
    """

    while True:

        try:
            value = float(input(message))

            if value <= 0:
                print("Amount must be greater than zero.")
                continue

            if value >= LARGE_AMOUNT_THRESHOLD and not confirm_action(
                f"That's {format_currency(value)} — did you mean to enter this?"
            ):
                continue

            return round(value, 2)

        except ValueError:
            print("Please enter a valid number.")


# ----------------------------------------------------------
# Validate Positive Integer
# ----------------------------------------------------------

def get_positive_int(message: str) -> int:
    """Prompt repeatedly until a valid positive integer is entered."""

    while True:

        try:
            value = int(input(message))

            if value <= 0:
                print("Value must be greater than zero.")
                continue

            return value

        except ValueError:
            print("Please enter a valid integer.")


# ----------------------------------------------------------
# Date Validation
# ----------------------------------------------------------

def get_valid_date(message: str) -> str:
    """Prompt repeatedly until a date in YYYY-MM-DD format is entered."""

    while True:

        date_text = input(message).strip()

        try:
            datetime.strptime(date_text, DATE_FORMAT)
            return date_text

        except ValueError:
            print(f"Invalid date format. Use {DATE_FORMAT}.")


# ----------------------------------------------------------
# Currency Formatting
# ----------------------------------------------------------

def format_currency(amount: float) -> str:
    """Format a numeric amount as an Indian Rupee currency string."""

    return f"₹{amount:,.2f}"


# ----------------------------------------------------------
# Display Expense Table
# ----------------------------------------------------------

def display_expenses(expenses: List[Expense]) -> None:
    """Display all expenses in a formatted table."""

    if not expenses:
        print("\nNo expense records found.")
        return

    separator = "-" * 115

    print(separator)
    print(
        f"{'ID':<5}{'Title':<20}{'Category':<18}"
        f"{'Amount':<15}{'Payment':<15}{'Date':<15}"
    )
    print(separator)

    for expense in expenses:
        print(
            f"{expense.expense_id:<5}"
            f"{expense.title:<20}"
            f"{expense.category:<18}"
            f"{format_currency(expense.amount):<15}"
            f"{expense.payment_method:<15}"
            f"{expense.expense_date:<15}"
        )

    print(separator)


# ----------------------------------------------------------
# Menu
# ----------------------------------------------------------

def print_menu() -> None:
    """Display the main application menu."""

    print_header("CLI EXPENSE TRACKER")

    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Search by Category")
    print("4. Search by Payment Method")
    print("5. Search by Title")
    print("6. Update Expense")
    print("7. Delete Expense")
    print("8. Dashboard Report")
    print("9. Export Report")
    print("10. Total Spending")
    print("0. Exit")


# ----------------------------------------------------------
# Footer
# ----------------------------------------------------------

def print_footer() -> None:
    """Display the closing message."""

    print("\n")
    print("=" * 60)
    print("Thank you for using CLI Expense Tracker")
    print("=" * 60)


# ----------------------------------------------------------
# Standalone Testing
# ----------------------------------------------------------

if __name__ == "__main__":

    print_header("UTILITY FUNCTIONS TEST")

    print(format_currency(9876543.75))
    print(confirm_action("Continue?"))
