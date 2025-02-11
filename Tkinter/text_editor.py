import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os

def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete("1.0", tk.END)
    with open(filepath, mode="r", encoding="utf-8") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"Simple Text Editor - {filepath}")

def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, mode="w", encoding="utf-8") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"Simple Text Editor - {filepath}")

window = tk.Tk()
window.geometry("300x300")
window.title("Simple Text Editor")

window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

txt_edit = tk.Text(window)
txt_edit.grid(row=0, column=1, sticky="nsew")

frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_buttons.grid(row=0, column=0, sticky="ns")

btn_open = tk.Button(frm_buttons, text="Open", command=open_file)
btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

btn_save = tk.Button(frm_buttons, text="Save As...", command=save_file)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)

window.mainloop()