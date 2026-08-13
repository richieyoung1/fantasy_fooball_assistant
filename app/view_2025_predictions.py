import tkinter as tk
from tkinter import ttk
import pandas as pd
import os

from scoring import DEFAULT_SCORING, SLIDER_RANGES, calculate_fantasy_points

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

    scoring = {stat: variable.get() for stat, variable in scoring_vars.items()}
    df["Fantasy Points (custom)"] = calculate_fantasy_points(df, scoring)
    predicted_cols = [col for col in df.columns if col.lower().startswith("predicted_")]
    player_column = next((col for col in df.columns if col.lower() == "player"), None)
    if player_column:
        predicted_cols.insert(0, player_column)
    predicted_cols.append("Fantasy Points (custom)")
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
root.geometry("1200x750")

controls = ttk.LabelFrame(root, text="Custom fantasy scoring (points per event)")
controls.pack(fill="x", padx=10, pady=8)
scoring_vars = {}
for index, (stat, default) in enumerate(DEFAULT_SCORING.items()):
    minimum, maximum, resolution = SLIDER_RANGES[stat]
    variable = tk.DoubleVar(value=default)
    scoring_vars[stat] = variable
    group = ttk.Frame(controls)
    group.grid(row=index // 4, column=index % 4, padx=8, pady=4, sticky="ew")
    ttk.Label(group, text=stat).pack(anchor="w")
    tk.Scale(group, from_=minimum, to=maximum, resolution=resolution, orient="horizontal",
             variable=variable, length=240, command=lambda _value: update_table()).pack()
for column in range(4):
    controls.columnconfigure(column, weight=1)

# Dropdown to choose position
position_var = tk.StringVar(value="QB")
position_menu = ttk.OptionMenu(root, position_var, "QB", *PREDICTION_FILES.keys(), command=update_table)
position_menu.pack(pady=6)

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
