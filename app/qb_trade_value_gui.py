import tkinter as tk
import pandas as pd

# Load predicted QB trade values
df = pd.read_csv("qb_trade_values.csv")

# Sort by trade value (optional)
df = df.sort_values(by="Predicted Trade Value", ascending=False)

# GUI setup
root = tk.Tk()
root.title("QB Trade Value Viewer")
root.geometry("700x500")

label = tk.Label(root, text="Quarterback Trade Values", font=("Helvetica", 16, "bold"))
label.pack(pady=10)

text_area = tk.Text(root, wrap=tk.WORD, font=("Courier", 10))
text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

for _, row in df.iterrows():
    text_area.insert(tk.END,
        f"{row['Player']}\n"
        f"Yards: {row['Yards']:.0f} | TD: {row['TD']:.0f} | INT: {row['INT']:.0f} | Cmp%: {row['Cmp%']:.1f} | Y/A: {row['Y/A']:.1f}\n"
        f"FantasyPts: {row['FantasyPts']:.1f} | Trade Value: {row['Predicted Trade Value']:.1f}\n"
        f"{'-'*70}\n"
    )

root.mainloop()
