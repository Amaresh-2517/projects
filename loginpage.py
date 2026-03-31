import tkinter as tk
from tkinter import messagebox

# Main window
root = tk.Tk()
root.title("Login Page")
root.geometry("350x250")
root.resizable(True, True)

# Login function
def login():
    username = entry_username.get()
    password = entry_password.get()

    # Dummy credentials
    if username == "admin" and password == "1234":
        messagebox.showinfo("Login Success", "Welcome, Admin!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Title
label_title = tk.Label(root, text="Login", font=("Arial", 20, "bold"))
label_title.pack(pady=15)

# Username
label_username = tk.Label(root, text="Username")
label_username.pack()
entry_username = tk.Entry(root, width=30)
entry_username.pack(pady=5)

# Password
label_password = tk.Label(root, text="Password")
label_password.pack()
entry_password = tk.Entry(root, width=30, show="*")
entry_password.pack(pady=5)

# Login button
login_button = tk.Button(root, text="Login", width=15, command=login)
login_button.pack(pady=20)

# Run app
root.mainloop()