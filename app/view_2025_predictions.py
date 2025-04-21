import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

PREDICTION_FILES = {
    "QB": "qb_2025_predictions.csv",
    "RB": "rb_2025_predictions.csv",
    "WR": "wr_2025_predictions.csv",
    "TE": "te_2025_predictions.csv"
}

def load_prediction_data(position):
    filename = PREDICTION_FILES.get(position)
    if not filename or not os.path.exists(filename):
        return pd.DataFrame()
    df = pd.read_csv(filename)

    # Only keep columns that are predicted stats
    predicted_cols = [col for col in df.columns if col.startswith("Predicted_")]
    if 'Player' in df.columns:
        predicted_cols.insert(0, 'Player')  # Keep Player name at the front
    return df[predicted_cols]

def update_table(*args):
    position = position_var.get()
    df = load_prediction_data(position)

    # Clear old table
    for row in tree.get_children():
        tree.delete(row)

    if df.empty:
        return

    # Set new columns
    tree["columns"] = list(df.columns)
    for col in tree["columns"]:
        tree.heading(col, text=col, command=lambda c=col: sort_column(c, False))
        tree.column(col, anchor="center", stretch=True)

    # Insert new data
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

def sort_column(col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children()]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: sort_column(col, not reverse))

# --- GUI Setup ---
root = tk.Tk()
root.title("2025 Fantasy Predictions Viewer")
root.geometry("1000x600")

# Dropdown to choose position
position_var = tk.StringVar(value="QB")
position_menu = ttk.OptionMenu(root, position_var, "QB", *PREDICTION_FILES.keys(), command=update_table)
position_menu.pack(pady=10)

# Treeview for table
tree = ttk.Treeview(root, show="headings")
tree.pack(expand=True, fill="both")

# Scrollbars
vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
vsb.pack(side="right", fill="y")
tree.configure(yscrollcommand=vsb.set)

# Initial load
update_table()

root.mainloop()
