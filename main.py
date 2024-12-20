import os.path
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from account_classifier import categorize_accounts
from sklearn.metrics import accuracy_score

# Initialize main window
root = tk.Tk()
root.title("Account It!")
root.resizable(False, False)
root.geometry("400x200")

file_path = ""  # Global file path variable

def select_file():
    global file_path  # Use the global variable to store the selected file path
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    if file_path:
        filename = os.path.basename(file_path)
        file_label.config(text=f"Selected file: {filename}")
        process_file(file_path)  # Pass the correct file path
    return file_path


def read_file(file_path):
    """Reads the Excel file and checks for required columns."""
    try:
        df = pd.read_excel(file_path)

        # Check if required columns exist
        if 'Account Name' not in df.columns or 'Balance' not in df.columns:
            raise ValueError("The Excel file must contain 'Account Name' and 'Balance' columns.")

        return df
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")


def categorize_data(df):
    """Categorizes the accounts into Balance Sheet, Revenues, and Expenses."""
    balance_sheet, income_statement_revenues, income_statement_expenses = categorize_accounts(df)
    return balance_sheet, income_statement_revenues, income_statement_expenses

def generate_income_statement(revenues, expenses):
    # Create a DataFrame for the formatted statement
    income_statement = pd.DataFrame(columns=['Description', 'Amount'])

    # Add revenues
    total_revenues = revenues['Balance'].sum()
    income_statement = pd.concat([income_statement, revenues.rename(columns={'Account Name': 'Description', 'Balance': 'Amount'})])
    income_statement = pd.concat([income_statement, pd.DataFrame({'Description': ['Total Revenues'], 'Amount': [total_revenues]})])

    # Add expenses
    total_expenses = expenses['Balance'].sum()
    income_statement = pd.concat([income_statement, pd.DataFrame({'Description': ['', 'Expenses:'], 'Amount': [None, None]})])
    income_statement = pd.concat([income_statement, expenses.rename(columns={'Account Name': 'Description', 'Balance': 'Amount'})])
    income_statement = pd.concat([income_statement, pd.DataFrame({'Description': ['Total Expenses'], 'Amount': [total_expenses]})])

    # Add net income
    net_income = total_revenues - total_expenses
    income_statement = pd.concat([income_statement, pd.DataFrame({'Description': ['Net Income (Profit) for the Period'], 'Amount': [net_income]})])

    return income_statement


def generate_and_save_income_statement(income_statement_revenues, income_statement_expenses, file_path):
    """Generates and saves the income statement to an Excel file."""
    # Make sure the generate_income_statement function is defined
    income_statement = generate_income_statement(income_statement_revenues, income_statement_expenses)

    output_file_path = file_path.replace(".xlsx", "_Income_Statement.xlsx")
    income_statement.to_excel(output_file_path, index=False)

    return output_file_path


def process_file(file_path):
    """Main function to process the file."""
    try:
        # Step 1: Read the file
        df = read_file(file_path)

        # Step 2: Categorize data into Balance Sheet, Revenues, and Expenses
        balance_sheet, income_statement_revenues, income_statement_expenses = categorize_data(df)

        # Step 3: Generate and save the income statement
        output_file_path = generate_and_save_income_statement(income_statement_revenues, income_statement_expenses, file_path)

        # Print the categorized lists for debugging
        print("Income Statement Revenues:", income_statement_revenues['Account Name'].tolist())
        print("Income Statement Expenses:", income_statement_expenses['Account Name'].tolist())
        print("Balance Sheet:", balance_sheet['Account Name'].tolist())

        # Show success message
        messagebox.showinfo("Success", f"File loaded and categorized successfully! Income statement saved to: {output_file_path}")

    except Exception as e:
        # Show error message if an exception occurs
        messagebox.showinfo("Error", str(e))


select_button = tk.Button(root, text="Select Trial Balance File", command=select_file)
select_button.pack(pady=20)

file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=10)

root.mainloop()
