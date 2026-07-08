"""
===========================================================
CLI Expense Tracker

File: expense.py

Description:
Defines the Expense data model, including field validation
and (de)serialization helpers used by the rest of the app.

Author: Kunal Kirtak
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict


# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------

DATE_FORMAT: str = "%Y-%m-%d"
CURRENCY_SYMBOL: str = "₹"


# ----------------------------------------------------------
# Exceptions
# ----------------------------------------------------------

class InvalidExpenseError(ValueError):
    """Raised when expense data fails validation."""


# ----------------------------------------------------------
# Expense Model
# ----------------------------------------------------------

@dataclass
class Expense:
    """
    Represents a single expense record.

    Attributes
    ----------
    expense_id : int
        Unique identifier for the expense.
    title : str
        Short description of the expense.
    category : str
        Spending category (e.g. Food, Travel).
    amount : float
        Amount spent. Must be greater than zero.
    payment_method : str
        Mode of payment (e.g. UPI, Cash, Card).
    expense_date : str
        Date of the expense in YYYY-MM-DD format.
    notes : str
        Optional additional notes.
    """

    expense_id: int
    title: str
    category: str
    amount: float
    payment_method: str
    expense_date: str
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize fields right after construction."""
        self._validate()

    def _validate(self) -> None:
        """
        Ensure the record holds sane, well-formed data.

        Raises
        ------
        InvalidExpenseError
            If any field contains invalid data.
        """

        if not isinstance(self.expense_id, int) or self.expense_id <= 0:
            raise InvalidExpenseError(
                f"expense_id must be a positive integer, got {self.expense_id!r}"
            )

        if not str(self.title).strip():
            raise InvalidExpenseError("title cannot be empty.")

        if not str(self.category).strip():
            raise InvalidExpenseError("category cannot be empty.")

        if not str(self.payment_method).strip():
            raise InvalidExpenseError("payment_method cannot be empty.")

        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise InvalidExpenseError(
                f"amount must be a positive number, got {self.amount!r}"
            )

        try:
            datetime.strptime(self.expense_date, DATE_FORMAT)
        except (TypeError, ValueError) as error:
            raise InvalidExpenseError(
                f"expense_date must be in {DATE_FORMAT} format, "
                f"got {self.expense_date!r}"
            ) from error

        # Normalize currency precision after validation passes.
        self.amount = round(float(self.amount), 2)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Expense into a plain dictionary.

        Returns
        -------
        Dict[str, Any]
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """
        Build an Expense from a dictionary (e.g. loaded from JSON).

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing expense fields.

        Returns
        -------
        Expense

        Raises
        ------
        InvalidExpenseError
            If required keys are missing or values are malformed.
        """

        required_fields = {
            "expense_id",
            "title",
            "category",
            "amount",
            "payment_method",
            "expense_date",
        }

        missing = required_fields - data.keys()

        if missing:
            raise InvalidExpenseError(
                f"Missing required field(s): {', '.join(sorted(missing))}"
            )

        try:
            return cls(
                expense_id=int(data["expense_id"]),
                title=str(data["title"]),
                category=str(data["category"]),
                amount=float(data["amount"]),
                payment_method=str(data["payment_method"]),
                expense_date=str(data["expense_date"]),
                notes=str(data.get("notes", "")),
            )
        except (TypeError, ValueError) as error:
            raise InvalidExpenseError(f"Malformed expense data: {error}") from error

    def __str__(self) -> str:
        return (
            f"[{self.expense_id}] "
            f"{self.title} | "
            f"{self.category} | "
            f"{CURRENCY_SYMBOL}{self.amount:.2f} | "
            f"{self.payment_method} | "
            f"{self.expense_date}"
        )


# ----------------------------------------------------------
# Factory Function
# ----------------------------------------------------------

def create_expense(
    expense_id: int,
    title: str,
    category: str,
    amount: float,
    payment_method: str,
    notes: str = "",
    expense_date: str | None = None,
) -> Expense:
    """
    Factory function for creating a validated Expense.

    Normalizes text casing/whitespace and defaults the date to
    today unless an explicit date is supplied.

    Parameters
    ----------
    expense_id : int
        Unique identifier to assign to the expense.
    title : str
        Expense title.
    category : str
        Expense category.
    amount : float
        Amount spent.
    payment_method : str
        Payment method used.
    notes : str, optional
        Additional notes, by default "".
    expense_date : str, optional
        Date in YYYY-MM-DD format. Defaults to today's date.

    Returns
    -------
    Expense
    """

    resolved_date = expense_date or datetime.now().strftime(DATE_FORMAT)

    return Expense(
        expense_id=expense_id,
        title=title.strip().title(),
        category=category.strip().title(),
        amount=round(float(amount), 2),
        payment_method=payment_method.strip().title(),
        expense_date=resolved_date,
        notes=notes.strip(),
    )


# ----------------------------------------------------------
# Standalone Testing
# ----------------------------------------------------------

if __name__ == "__main__":

    sample = create_expense(
        expense_id=1,
        title="Groceries",
        category="Food",
        amount=1250.75,
        payment_method="UPI",
        notes="Weekly vegetables",
    )

    print(sample)
    print()
    print(sample.to_dict())
