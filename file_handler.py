"""
===========================================================
CLI Expense Tracker

File: file_handler.py

Description:
Handles all persistence (JSON file) operations for expenses,
including atomic writes so a crash mid-save can never corrupt
or truncate existing data, and quarantining of unreadable
files so a corrupted database is never silently discarded.

Author: Kunal Kirtak
===========================================================
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from expense import Expense, InvalidExpenseError


# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------

LOG_FOLDER = Path("logs")
LOG_FOLDER.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Guard against duplicate log lines if this module gets
    # imported more than once within the same process.
    _handler = logging.FileHandler(
        LOG_FOLDER / "expense_tracker.log", encoding="utf-8"
    )
    _handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(_handler)
    logger.propagate = False


# ----------------------------------------------------------
# Database File
# ----------------------------------------------------------

# Overridable via env var so tests / deployments can point
# at a different data file without touching source code.
DATA_FILE = Path(os.getenv("EXPENSE_DB_PATH", "expenses.json"))


# ----------------------------------------------------------
# Custom Exceptions
# ----------------------------------------------------------

class StorageError(Exception):
    """Raised when reading from or writing to the data file fails."""


class ExpenseNotFoundError(Exception):
    """Raised when an operation references an expense_id that does not exist."""


# ----------------------------------------------------------
# Create Database File (if not exists)
# ----------------------------------------------------------

def initialize_database() -> None:
    """Create expenses.json if it does not already exist."""

    if not DATA_FILE.exists():

        DATA_FILE.write_text("[]", encoding="utf-8")

        logger.info("Created new expenses database at %s", DATA_FILE)


# ----------------------------------------------------------
# Corruption Recovery
# ----------------------------------------------------------

def _quarantine_corrupted_file() -> Path:
    """
    Move an unreadable data file aside so it is never overwritten
    or silently lost, then start fresh with an empty database.

    Returns
    -------
    Path
        Location the corrupted file was moved to.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    quarantine_path = DATA_FILE.with_name(
        f"{DATA_FILE.stem}.corrupted_{timestamp}.json"
    )

    DATA_FILE.replace(quarantine_path)

    DATA_FILE.write_text("[]", encoding="utf-8")

    logger.error(
        "Corrupted database quarantined at %s. A fresh database was created.",
        quarantine_path,
    )

    return quarantine_path


# ----------------------------------------------------------
# Read Expenses
# ----------------------------------------------------------

def load_expenses() -> List[Expense]:
    """
    Read all expenses from the JSON file.

    A file that fails to parse as JSON is quarantined (renamed
    aside) rather than silently discarded, so no data is ever
    lost. Individual malformed records are skipped and logged
    instead of crashing the whole load.

    Returns
    -------
    List[Expense]

    Raises
    ------
    StorageError
        If the data file cannot be read due to an OS-level error.
    """

    initialize_database()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            raw_records = json.load(file)

    except json.JSONDecodeError:
        _quarantine_corrupted_file()
        return []

    except OSError as error:
        logger.exception("Failed to read database file.")
        raise StorageError(f"Could not read {DATA_FILE}: {error}") from error

    expenses: List[Expense] = []

    for record in raw_records:
        try:
            expenses.append(Expense.from_dict(record))
        except InvalidExpenseError as error:
            logger.warning("Skipped malformed expense record: %s", error)

    return expenses


# ----------------------------------------------------------
# Save Expenses
# ----------------------------------------------------------

def save_expenses(expenses: List[Expense]) -> None:
    """
    Persist all expenses to disk atomically.

    Writes to a temporary file in the same directory first,
    then swaps it into place with `os.replace`, so a crash or
    power loss mid-write can never corrupt or truncate the
    existing database.

    Raises
    ------
    StorageError
        If the write operation fails.
    """

    data = [expense.to_dict() for expense in expenses]

    tmp_path: Optional[Path] = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            prefix=f".{DATA_FILE.stem}_",
            suffix=".tmp",
            delete=False,
        ) as tmp_file:

            json.dump(data, tmp_file, indent=4, ensure_ascii=False)
            tmp_path = Path(tmp_file.name)

        os.replace(tmp_path, DATA_FILE)

        logger.info("Expenses saved successfully (%d records).", len(expenses))

    except OSError as error:

        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

        logger.exception("Failed to save expenses.")
        raise StorageError(f"Could not write to {DATA_FILE}: {error}") from error


# ----------------------------------------------------------
# Generate Next Expense ID
# ----------------------------------------------------------

def generate_expense_id(expenses: Optional[List[Expense]] = None) -> int:
    """
    Return the next available expense ID.

    Parameters
    ----------
    expenses : Optional[List[Expense]]
        Pass an already-loaded list to avoid a redundant disk
        read (useful when the caller has just called
        `get_all_expenses`). If omitted, expenses are loaded
        from disk.

    Returns
    -------
    int
    """

    expenses = load_expenses() if expenses is None else expenses

    if not expenses:
        return 1

    return max(expense.expense_id for expense in expenses) + 1


# ----------------------------------------------------------
# Add Expense
# ----------------------------------------------------------

def add_expense(expense: Expense) -> None:
    """
    Add a new expense record to the database.

    Raises
    ------
    InvalidExpenseError
        If an expense with the same ID already exists.
    """

    expenses = load_expenses()

    if any(existing.expense_id == expense.expense_id for existing in expenses):
        raise InvalidExpenseError(
            f"Expense ID {expense.expense_id} already exists."
        )

    expenses.append(expense)

    save_expenses(expenses)

    logger.info("Expense added: %s", expense.expense_id)


# ----------------------------------------------------------
# Get All Expenses
# ----------------------------------------------------------

def get_all_expenses() -> List[Expense]:
    """Return all stored expenses."""

    return load_expenses()


# ----------------------------------------------------------
# Find Expense by ID
# ----------------------------------------------------------

def find_expense(expense_id: int) -> Optional[Expense]:
    """Find an expense by its ID, or return None if no match exists."""

    for expense in load_expenses():
        if expense.expense_id == expense_id:
            return expense

    return None


# ----------------------------------------------------------
# Delete Expense
# ----------------------------------------------------------

def delete_expense(expense_id: int) -> bool:
    """
    Delete an expense by ID.

    Returns
    -------
    bool
        True if an expense was deleted, False if no match was found.
    """

    expenses = load_expenses()

    remaining = [
        expense for expense in expenses if expense.expense_id != expense_id
    ]

    if len(remaining) == len(expenses):
        return False

    save_expenses(remaining)

    logger.info("Expense deleted: %s", expense_id)

    return True


# ----------------------------------------------------------
# Update Expense
# ----------------------------------------------------------

def update_expense(updated_expense: Expense) -> bool:
    """
    Replace an existing expense with new data (matched by expense_id).

    Returns
    -------
    bool
        True if the expense was found and updated, False otherwise.
    """

    expenses = load_expenses()

    for index, expense in enumerate(expenses):

        if expense.expense_id == updated_expense.expense_id:

            expenses[index] = updated_expense

            save_expenses(expenses)

            logger.info("Expense updated: %s", updated_expense.expense_id)

            return True

    return False


# ----------------------------------------------------------
# Search by Category
# ----------------------------------------------------------

def search_by_category(category: str) -> List[Expense]:
    """Search expenses by category (case-insensitive, exact match)."""

    target = category.lower()

    return [
        expense for expense in load_expenses() if expense.category.lower() == target
    ]


# ----------------------------------------------------------
# Search by Payment Method
# ----------------------------------------------------------

def search_by_payment_method(payment_method: str) -> List[Expense]:
    """Search expenses by payment method (case-insensitive, exact match)."""

    target = payment_method.lower()

    return [
        expense
        for expense in load_expenses()
        if expense.payment_method.lower() == target
    ]


# ----------------------------------------------------------
# Search by Title
# ----------------------------------------------------------

def search_by_title(keyword: str) -> List[Expense]:
    """Search expense titles for a keyword (case-insensitive, partial match)."""

    target = keyword.lower()

    return [
        expense for expense in load_expenses() if target in expense.title.lower()
    ]


# ----------------------------------------------------------
# Total Amount
# ----------------------------------------------------------

def total_expense_amount() -> float:
    """Return the total amount spent across all stored expenses."""

    return round(sum(expense.amount for expense in load_expenses()), 2)


# ----------------------------------------------------------
# Standalone Testing
# ----------------------------------------------------------

if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")
    print("Current Expenses")

    for expense in get_all_expenses():
        print(expense)

    print()
    print("Total Spending : ₹", total_expense_amount())
