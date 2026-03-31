import string
import tkinter as tk
from tkinter import messagebox, ttk


def estimate_crack_time(password: str) -> float:
    charset_size = 0

    if any(c.islower() for c in password):
        charset_size += 26

    if any(c.isupper() for c in password):
        charset_size += 26

    if any(c.isdigit() for c in password):
        charset_size += 10

    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)

    if not password or charset_size == 0:
        return 0.0

    combinations = charset_size ** len(password)
    guesses_per_second = 1_000_000_000
    return combinations / guesses_per_second


def format_time(seconds: float) -> str:
    if seconds <= 0:
        return "Instantly"

    units = [
        ("years", 365 * 24 * 3600),
        ("months", 30 * 24 * 3600),
        ("days", 24 * 3600),
        ("hours", 3600),
        ("minutes", 60),
        ("seconds", 1),
    ]

    remaining = int(seconds)
    parts = []

    for label, unit_seconds in units:
        value, remaining = divmod(remaining, unit_seconds)
        if value:
            parts.append(f"{value} {label}")

    return " ".join(parts[:3]) if parts else "Less than 1 second"


def describe_password(password: str) -> str:
    categories = 0
    categories += any(c.islower() for c in password)
    categories += any(c.isupper() for c in password)
    categories += any(c.isdigit() for c in password)
    categories += any(c in string.punctuation for c in password)

    length = len(password)
    if length < 8 or categories <= 1:
        return "Weak"
    if length < 12 or categories == 2:
        return "Moderate"
    if length < 16 or categories == 3:
        return "Strong"
    return "Very strong"


class PasswordCrackTimeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Password Crack Time Estimator")
        self.root.geometry("520x300")
        self.root.resizable(False, False)

        self.password_var = tk.StringVar()
        self.time_var = tk.StringVar(value="Enter a password to estimate crack time.")
        self.strength_var = tk.StringVar(value="Strength: N/A")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Password", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        password_entry = ttk.Entry(frame, textvariable=self.password_var, width=42, show="*")
        password_entry.grid(row=1, column=0, sticky="we", pady=(0, 12))
        password_entry.focus()

        ttk.Button(frame, text="Estimate Crack Time", command=self.calculate).grid(
            row=2, column=0, sticky="we", pady=(0, 12)
        )

        ttk.Label(frame, textvariable=self.strength_var, font=("Arial", 11, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 8)
        )

        result_box = ttk.Label(
            frame,
            textvariable=self.time_var,
            wraplength=470,
            justify="left",
            relief="solid",
            padding=12,
        )
        result_box.grid(row=4, column=0, sticky="nsew")

        note = (
            "This is only a rough estimate based on brute-force guessing at "
            "1 billion guesses per second."
        )
        ttk.Label(frame, text=note, wraplength=470, foreground="#555555").grid(
            row=5, column=0, sticky="w", pady=(12, 0)
        )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

    def calculate(self) -> None:
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("No password", "Enter a password first.")
            return

        seconds = estimate_crack_time(password)
        strength = describe_password(password)

        self.strength_var.set(f"Strength: {strength}")
        self.time_var.set(
            f"Estimated crack time: {format_time(seconds)}\n"
            f"Length: {len(password)} characters"
        )


def main() -> None:
    root = tk.Tk()
    PasswordCrackTimeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
