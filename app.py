"""
===========================================================
CLI Expense Tracker

File: app.py

Description:
Main entry point and menu controller. Wires together the
Expense model (expense.py), persistence layer (file_handler.py),
and reporting utilities (reports.py) into an interactive,
menu-driven command-line application.

Author: Kunal Kirtak
===========================================================
"""

from __future__ import annotations

from expense import Expense, InvalidExpenseError, create_expense
from file_handler import (
    StorageError,
    add_expense,
    delete_expense,
    find_expense,
    generate_expense_id,
    get_all_expenses,
    initialize_database,
    search_by_category,
    search_by_payment_method,
    search_by_title,
    total_expense_amount,
    update_expense,
)
from reports import export_report, print_dashboard
from utils import (
    clear_screen,
    confirm_action,
    display_expenses,
    format_currency,
    get_non_empty_input,
    get_positive_float,
    get_positive_int,
    get_valid_date,
    pause,
    print_footer,
    print_header,
    print_menu,
)


# ----------------------------------------------------------
# Add Expense
# ----------------------------------------------------------

def handle_add_expense() -> None:
    """Prompt for expense details and save a new record."""

    print_header("ADD EXPENSE")

    title = get_non_empty_input("Title: ")
    category = get_non_empty_input("Category: ")
    amount = get_positive_float("Amount: ")
    payment_method = get_non_empty_input("Payment Method: ")
    notes = input("Notes (optional): ").strip()

    if confirm_action("Use today's date?"):
        expense_date = None
    else:
        expense_date = get_valid_date("Date (YYYY-MM-DD): ")

    try:
        expense_id = generate_expense_id()

        expense = create_expense(
            expense_id=expense_id,
            title=title,
            category=category,
            amount=amount,
            payment_method=payment_method,
            notes=notes,
            expense_date=expense_date,
        )

        add_expense(expense)

        print(f"\nExpense added successfully:\n  {expense}")

    except InvalidExpenseError as error:
        print(f"\nCould not add expense: {error}")

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# View All Expenses
# ----------------------------------------------------------

def handle_view_all() -> None:
    """Display every stored expense in a table."""

    print_header("ALL EXPENSES")

    try:
        display_expenses(get_all_expenses())

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Search by Category
# ----------------------------------------------------------

def handle_search_by_category() -> None:
    print_header("SEARCH BY CATEGORY")

    category = get_non_empty_input("Category: ")

    try:
        display_expenses(search_by_category(category))

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Search by Payment Method
# ----------------------------------------------------------

def handle_search_by_payment_method() -> None:
    print_header("SEARCH BY PAYMENT METHOD")

    payment_method = get_non_empty_input("Payment Method: ")

    try:
        display_expenses(search_by_payment_method(payment_method))

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Search by Title
# ----------------------------------------------------------

def handle_search_by_title() -> None:
    print_header("SEARCH BY TITLE")

    keyword = get_non_empty_input("Keyword: ")

    try:
        display_expenses(search_by_title(keyword))

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Update Expense
# ----------------------------------------------------------

def handle_update_expense() -> None:
    """Look up an expense by ID and let the user edit any field."""

    print_header("UPDATE EXPENSE")

    try:
        expense_id = get_positive_int("Expense ID to update: ")
        existing = find_expense(expense_id)

        if existing is None:
            print(f"\nNo expense found with ID {expense_id}.")
            return

        print(f"\nCurrent record:\n  {existing}")
        print("\nPress Enter to keep the current value for any field.\n")

        title = input(f"Title [{existing.title}]: ").strip() or existing.title
        category = (
            input(f"Category [{existing.category}]: ").strip() or existing.category
        )
        payment_method = (
            input(f"Payment Method [{existing.payment_method}]: ").strip()
            or existing.payment_method
        )
        notes = input(f"Notes [{existing.notes}]: ").strip() or existing.notes

        amount_input = input(f"Amount [{existing.amount}]: ").strip()
        amount = float(amount_input) if amount_input else existing.amount

        date_input = input(f"Date [{existing.expense_date}]: ").strip()
        expense_date = date_input if date_input else existing.expense_date

        updated = Expense(
            expense_id=expense_id,
            title=title.strip().title(),
            category=category.strip().title(),
            amount=round(float(amount), 2),
            payment_method=payment_method.strip().title(),
            expense_date=expense_date,
            notes=notes.strip(),
        )

        if update_expense(updated):
            print(f"\nExpense updated successfully:\n  {updated}")
        else:
            print(f"\nNo expense found with ID {expense_id}.")

    except ValueError as error:
        print(f"\nInvalid input: {error}")

    except InvalidExpenseError as error:
        print(f"\nCould not update expense: {error}")

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Delete Expense
# ----------------------------------------------------------

def handle_delete_expense() -> None:
    print_header("DELETE EXPENSE")

    try:
        expense_id = get_positive_int("Expense ID to delete: ")
        existing = find_expense(expense_id)

        if existing is None:
            print(f"\nNo expense found with ID {expense_id}.")
            return

        print(f"\nRecord:\n  {existing}")

        if not confirm_action("Are you sure you want to delete this expense?"):
            print("\nDeletion cancelled.")
            return

        if delete_expense(expense_id):
            print(f"\nExpense {expense_id} deleted successfully.")
        else:
            print(f"\nNo expense found with ID {expense_id}.")

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Dashboard Report
# ----------------------------------------------------------

def handle_dashboard() -> None:
    print_header("DASHBOARD REPORT")

    try:
        print_dashboard(get_all_expenses())

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Export Report
# ----------------------------------------------------------

def handle_export_report() -> None:
    print_header("EXPORT REPORT")

    filename = (
        input("Output filename [expense_report.txt]: ").strip()
        or "expense_report.txt"
    )

    try:
        report_path = export_report(get_all_expenses(), filename=filename)
        print(f"\nReport exported to: {report_path.resolve()}")

    except StorageError as error:
        print(f"\nStorage error: {error}")

    except OSError as error:
        print(f"\nCould not write report file: {error}")


# ----------------------------------------------------------
# Total Spending
# ----------------------------------------------------------

def handle_total_spending() -> None:
    print_header("TOTAL SPENDING")

    try:
        total = total_expense_amount()
        print(f"\nTotal spending across all expenses: {format_currency(total)}")

    except StorageError as error:
        print(f"\nStorage error: {error}")


# ----------------------------------------------------------
# Menu Dispatch Table
# ----------------------------------------------------------

MENU_ACTIONS = {
    "1": handle_add_expense,
    "2": handle_view_all,
    "3": handle_search_by_category,
    "4": handle_search_by_payment_method,
    "5": handle_search_by_title,
    "6": handle_update_expense,
    "7": handle_delete_expense,
    "8": handle_dashboard,
    "9": handle_export_report,
    "10": handle_total_spending,
}


# ----------------------------------------------------------
# Main Loop
# ----------------------------------------------------------

def main() -> None:
    """Initialize storage and run the interactive menu loop."""

    try:
        initialize_database()
    except StorageError as error:
        print(f"Fatal: could not initialize database: {error}")
        return

    while True:
        clear_screen()
        print_menu()

        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print_footer()
            break

        action = MENU_ACTIONS.get(choice)

        if action is None:
            print("\nInvalid option. Please choose a number from the menu.")
        else:
            clear_screen()
            action()

        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
