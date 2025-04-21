import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext

# Load the updated clustered QB data
df = pd.read_csv("qb_2023_stats.csv")

# Set GUI window
root = tk.Tk()
root.title("Quarterback Styles Viewer")
root.geometry("850x600")

# Dropdown filter
style_var = tk.StringVar()
style_options = ["All"] + sorted(df["QB Style"].unique().tolist())
style_dropdown = ttk.Combobox(root, textvariable=style_var, values=style_options, state="readonly")
style_dropdown.set("All")
style_dropdown.pack(pady=10)

# Text display area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
text_area.pack(padx=10, pady=10)

# Display QB stats
def update_display(*args):
    selected_style = style_var.get()
    filtered_df = df if selected_style == "All" else df[df["QB Style"] == selected_style]

    text_area.delete(1.0, tk.END)
    for _, row in filtered_df.iterrows():
        text_area.insert(tk.END, f"🏈 {row['Player']} ({row['Team']})\n")
        text_area.insert(tk.END, f"  Style: {row['QB Style']}\n")
        text_area.insert(tk.END, f"  Age: {row['Age']} | Games: {row['Games']}\n")
        text_area.insert(tk.END, f"  Completions: {row['Completions']} / Attempts: {row['Attempts']}\n")
        text_area.insert(tk.END, f"  Yards: {row['Yards']} | TDs: {row['Touchdowns']} | INTs: {row['Interceptions']}\n")
        text_area.insert(tk.END, f"  Passer Rating: {row['Passer Rating']}\n")
        text_area.insert(tk.END, f"  Rush Attempts: {row['Rush Attempts']} | Yards: {row['Rush Yards']} | TDs: {row['Rush TDs']}\n")
        text_area.insert(tk.END, "-" * 60 + "\n")

style_dropdown.bind("<<ComboboxSelected>>", update_display)

# Initial display
update_display()

root.mainloop()
print("✅ QB Styles Viewer GUI is running. Close the window to exit.")