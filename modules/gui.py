# gui.py
import tkinter as tk
from tkinter import messagebox
import getstatements  # Import the function

def generate_report():
    # Get the ticker symbol from the GUI input field
    ticker_request = company_entry.get().upper().strip()
    if ticker_request:
        try:
            # Retrieve and export statements
            getstatements.retrieve_and_export_statements(ticker_request, export=export_var.get())
            messagebox.showinfo("Success", f"Report generated for {ticker_request}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    else:
        messagebox.showwarning("Input Required", "Please enter a company ticker symbol.")

# Set up Tkinter GUI
root = tk.Tk()
root.title("Financial Statement Generator")
root.geometry("300x300")

# Create input field and button
company_label = tk.Label(root, text="Company Ticker:")
company_label.pack(pady=5)
company_entry = tk.Entry(root)
company_entry.pack(pady=5)

export_var = tk.BooleanVar()
export_checkbox = tk.Checkbutton(root, text="Export files", variable=export_var)
export_checkbox.pack(pady=5)

generate_button = tk.Button(root, text="Generate Report", command=generate_report)
generate_button.pack(pady=20)

# Run the application
root.mainloop()
