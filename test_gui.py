import tkinter as tk

root = tk.Tk()
root.title("Hello, tkinter!")
root.geometry("300x200")

label = tk.Label(root, text="Welcome to tkinter!")
label.pack()

root.mainloop()
