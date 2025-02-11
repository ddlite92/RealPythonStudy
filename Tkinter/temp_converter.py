import tkinter as tk

window = tk.Tk()
window.title("Temperature Converter")
window.geometry("200x50")
# window.resizable(width=False, height=False)

def fahrenheit_to_celsius():
    """Convert the value for Fahrenheit to Celsius and insert the
    result into lbl_result.
    """
    fahrenheit = ent_temperature.get()
    celsius = (5 / 9) * (float(fahrenheit) - 32)
    lbl_result["text"] = f"{round(celsius, 2)} \N{DEGREE CELSIUS}"

frm_entry = tk.Frame(master=window)
frm_entry.grid(row=0, column=0, padx=10)

btn_convert = tk.Button(
    master=window,
    text="\N{RIGHTWARDS BLACK ARROW}",
    command=fahrenheit_to_celsius
)

ent_temperature = tk.Entry(master=frm_entry, width=10)
ent_temperature.grid(row=0, column=0, sticky="e")

lbl_temp = tk.Label(master=frm_entry, text="\N{DEGREE FAHRENHEIT}")
lbl_temp.grid(row=0, column=1, sticky="w")

lbl_result = tk.Label(master=window, text="\N{DEGREE CELSIUS}")
lbl_result.grid(row=0, column=2, padx=10)

btn_convert.grid(row=0, column=1, pady=10)


window.mainloop()