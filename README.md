# Weekend financier

A lightweight, simple Python application to track and analyze household finances.

Load your financial data from CSV, JSON, or Excel files and visualize your finances with matplotlib.

I just made this for myself because I found other finance tools annoying, but maybe someone else could use something like this too.

## Installation

1. Install Python 3.7+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the program:
   ```bash
   python main.py
   ```
   This will use the default file `examples/example.csv`

   To specify your own file:
   ```bash
   python main.py path/to/your/file.csv
   python main.py examples/example.json
   python main.py examples/example.xlsx
   ```

   Example files are provided in `examples/` for CSV, JSON, and Excel formats.
   You can put your own data files anywhere - to create a `data/` folder, do the following:

5. Create a `data/` folder**:
   ```bash
   mkdir data
   ```
6. Create your financial data file in CSV, JSON, or Excel format. Use the example files in `examples/` as a template.
   ```bash
   # Copy an example to use as a template
   cp examples/example.csv data/my_finances.csv
   # Then edit data/my_finances.csv with your actual data
   ```

7. Run the program with your data file.
   ```bash
   python main.py data/my_finances.csv
   ```

   Or with JSON or Excel:
   ```bash
   python main.py data/my_finances.json
   python main.py data/my_finances.xlsx
   ```

   The program does the following:
   - Display a financial summary in the console
   - Generate static PNG charts
   - Create an interactive web dashboard that opens in your browser

## How to add your own data

The program supports **CSV**, **JSON**, and **Excel** (.xlsx, .xls) files.

All file formats must have the following fields:

- `category`: Category label. Optional, not used.
- `item`: Name of the item. Can be anything, such as "Salary" or "Fun". String
- `amount`: The amount of money. Float.
- `type`: Type of item. One of: `income`, `expense`, `savings`, `debt`.
- `frequency`: How often it occurs. One of: `monthly`, `yearly`, `weekly`, `one-time`.

**CSV format:**

```csv
category,item,amount,type,frequency
Income,Salary,7500,income,monthly
Expenses,Mortgage,2500,expense,monthly
Savings,Emergency Fund Balance,15000,savings,one-time
```

**JSON format:**

```json
[
  {
    "category": "Income",
    "item": "Salary",
    "amount": 7500,
    "type": "income",
    "frequency": "monthly"
  },
  {
    "category": "Expenses",
    "item": "Mortgage",
    "amount": 2500,
    "type": "expense",
    "frequency": "monthly"
  }
]
```

**Excel format:**

Excel files in `.xlsx` or `.xls` should have the same columns as CSV files in the first sheet.

### Take snapshots

By default, charts are saved without dates.
Use `--snapshot` when you want to keep historical snapshots.
To save charts with a date suffix:

```bash
python main.py --snapshot
```

This creates files like:
- `reports/expenses_chart_2024-01-15.png`
- `reports/financial_dashboard_2024-01-15.html`

To save snapshots to a custom directory:
```bash
python main.py --output-dir custom_folder/ --snapshot
```

To save charts to the current directory instead of `reports/`:
```bash
python main.py --output-dir .
```


## Requirements

* Python 3.7+
* matplotlib for static charts
* plotly (for optional interactive web dashboard - falls back to static charts if not installed)

Tested with Python 3.10 on Linux.

## License

This project is open source and available for personal use.
