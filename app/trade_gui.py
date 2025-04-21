import tkinter as tk
from tkinter import ttk
import pandas as pd

# Load player data
players = pd.read_csv("players.csv")

# Clean up duplicates and prefer the correct 2023 FPTS/PPG columns
if "2023 FPTS" not in players.columns and "2023 FPTS_y" in players.columns:
    players["2023 FPTS"] = players["2023 FPTS_y"].fillna(0)
    players["2023 PPG"] = players["2023 PPG_y"].fillna(0)

# Build display label for dropdowns
players["Display"] = players["Player"] + " (" + players["Pos"] + ") - " + \
                     "Val: " + players["Trade Value"].round(1).astype(str) + \
                     ", 2023: " + players["2023 FPTS"].round(1).astype(str) + " FPTS"

# GUI setup
root = tk.Tk()
root.title("Fantasy Football Trade Evaluator")
root.geometry("800x500")

tk.Label(root, text="Team A", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=5)
tk.Label(root, text="Team B", font=("Helvetica", 12, "bold")).grid(row=0, column=2, pady=5)

team_a_list = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40)
team_b_list = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40)
team_a_list.grid(row=1, column=0, padx=10)
team_b_list.grid(row=1, column=2, padx=10)

for label in players["Display"]:
    team_a_list.insert(tk.END, label)
    team_b_list.insert(tk.END, label)

result_label = tk.Label(root, text="", font=("Helvetica", 12), fg="blue")
result_label.grid(row=3, column=0, columnspan=3, pady=20)

def evaluate_trade():
    a_indices = team_a_list.curselection()
    b_indices = team_b_list.curselection()

    if not a_indices or not b_indices:
        result_label.config(text="⚠️ Please select players from both teams.")
        return

    a_value = players.iloc[list(a_indices)]["Trade Value"].sum()
    b_value = players.iloc[list(b_indices)]["Trade Value"].sum()

    a_names = players.iloc[list(a_indices)]["Player"].tolist()
    b_names = players.iloc[list(b_indices)]["Player"].tolist()

    result = f"Team A Total Value: {a_value:.1f}\nPlayers: {', '.join(a_names)}\n\n"
    result += f"Team B Total Value: {b_value:.1f}\nPlayers: {', '.join(b_names)}\n\n"

    if a_value > b_value:
        result += "✅ Advantage: Team A"
    elif b_value > a_value:
        result += "✅ Advantage: Team B"
    else:
        result += "🔁 Fair Trade!"

    result_label.config(text=result)

tk.Button(root, text="Evaluate Trade", command=evaluate_trade, bg="#4CAF50", fg="white", padx=10, pady=5).grid(row=2, column=1)

root.mainloop()
