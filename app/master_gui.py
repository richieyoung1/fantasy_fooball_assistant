import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# Define the script paths
scripts = {
    "QB Stats Viewer": "qb_gui.py",
    "QB Style Viewer": "qb_style_gui.py",
    "Trade Evaluator": "trade_gui.py"
}

# Function to launch a script
def launch_script(script_name):
    script_path = scripts.get(script_name)
    if script_path and os.path.exists(script_path):
        try:
            subprocess.Popen(["python", script_path], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {script_name}.\n\n{e}")
    else:
        messagebox.showerror("Error", f"Script '{script_path}' not found.")

# GUI setup
root = tk.Tk()
root.title("Fantasy Football Assistant - Master GUI")
root.geometry("400x250")
root.resizable(False, False)

tk.Label(root, text="Select a tool to open", font=("Helvetica", 14, "bold")).pack(pady=20)

for name in scripts:
    tk.Button(root, text=name, width=30, font=("Helvetica", 12),
              command=lambda n=name: launch_script(n)).pack(pady=8)

root.mainloop()
print("✅ Master GUI is running. Close the window to exit.")