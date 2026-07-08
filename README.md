# 💰 CLI Expense Tracker

A production-quality, menu-driven command-line application for tracking personal expenses — built entirely with Python's standard library. It supports adding, searching, updating, and deleting expenses, generating dashboards and exportable reports, and stores data safely with atomic writes and corruption recovery.

---

## ✨ Features

- **Add / View / Update / Delete** expense records with full field validation
- **Search** expenses by category, payment method, or title keyword
- **Dashboard** with total, average, highest, and lowest spending at a glance
- **Category, payment method, and monthly** spending breakdowns
- **Exportable text reports** (`.txt`) summarizing all statistics and records
- **Safe persistence**:
  - Atomic writes (temp file + `os.replace`) so a crash mid-save never corrupts data
  - Corrupted JSON files are automatically quarantined (renamed aside) instead of being silently overwritten or discarded
  - Malformed individual records are skipped and logged rather than crashing the app
- **Input validation** for amounts, dates, and IDs, including a confirmation prompt for unusually large amounts
- **Indian Rupee (₹) formatted** currency display throughout
- **Logging** of all key operations to `logs/expense_tracker.log`

---

## 🗂️ Project Structure

```
cli-expense-tracker/
├── app.py              # Entry point — menu controller, wires everything together
├── expense.py           # Expense data model, validation, (de)serialization
├── file_handler.py      # JSON persistence layer (CRUD, atomic writes, recovery)
├── reports.py            # Statistics, breakdowns, dashboard, report export
├── utils.py              # Input prompts, formatting, table display, menu UI
├── expenses.json          # Local data store (auto-created on first run)
├── Output/
│   ├── Output Screenshots  # images of working of project
│   └── expense_report.txt
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.10+** (uses `dataclasses`, `pathlib`, `X | None` type hints)
- Standard library only — no third-party dependencies required

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/cli-expense-tracker.git
cd cli-expense-tracker
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

This project has **no external dependencies**, but `requirements.txt` is included for completeness and future extensions:

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

On first run, `expenses.json` and a `logs/` folder are created automatically.

---

## 📖 Usage

Once running, you'll see an interactive menu:

```
============================================================
                  CLI EXPENSE TRACKER
============================================================
1. Add Expense
2. View All Expenses
3. Search by Category
4. Search by Payment Method
5. Search by Title
6. Update Expense
7. Delete Expense
8. Dashboard Report
9. Export Report
10. Total Spending
0. Exit
```

Simply enter the number of the option you want and follow the prompts.

### Custom data file location

You can point the app at a different JSON file using an environment variable:

```bash
EXPENSE_DB_PATH=/path/to/custom_expenses.json python app.py
```

---

## 🧪 Sample Data

A sample `expenses.json` is included so you can explore the dashboard and reports immediately without manually adding records. Delete or replace it to start with a clean slate.

---

## 🔒 Data Safety Design

| Concern | How it's handled |
|---|---|
| Crash mid-write | Writes go to a temp file first, then atomically replace the real file via `os.replace` |
| Corrupted JSON on disk | The bad file is renamed to `expenses.corrupted_<timestamp>.json` and a fresh empty database is created — nothing is lost |
| One bad record among many good ones | The bad record is skipped and logged; the rest of the database loads normally |

---

## 📌 Roadmap Ideas

- [ ] CSV / Excel export
- [ ] Budget limits and alerts per category
- [ ] Multi-currency support
- [ ] Unit test suite (`pytest`)

---

## 👤 Author

**Kunal Kirtak**

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
