import secrets
import string
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk, messagebox
from typing import Dict


@dataclass(frozen=True)
class PasswordPolicy:
    min_length: int
    require_upper: bool = True
    require_lower: bool = True
    require_digits: bool = True
    require_symbols: bool = True
    exclude_ambiguous: bool = True


class StrongPasswordGenerator:
    _AMBIGUOUS = set("O0oIl1|`'")
    _SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"
    _MIN_PASSWORD_LENGTH = 8
    _MAX_PASSWORD_LENGTH = 64

    def __init__(self) -> None:
        self.policies: Dict[str, PasswordPolicy] = {
            "social": PasswordPolicy(min_length=12),
            "email": PasswordPolicy(min_length=14),
            "shopping": PasswordPolicy(min_length=14),
            "banking": PasswordPolicy(min_length=18),
            "developer": PasswordPolicy(min_length=20),
            "gaming": PasswordPolicy(min_length=12, require_symbols=False),
            "default": PasswordPolicy(min_length=16),
        }

    def get_policy(self, platform_type: str) -> PasswordPolicy:
        return self.policies.get(platform_type.lower(), self.policies["default"])

    def generate(self, platform_type: str, length: int | None = None) -> str:
        policy = self.get_policy(platform_type)
        requested_length = policy.min_length if length is None else length
        target_len = max(requested_length, policy.min_length)

        if target_len > self._MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"Password length must be between {self._MIN_PASSWORD_LENGTH} and {self._MAX_PASSWORD_LENGTH}."
            )

        lower = self._filter_chars(string.ascii_lowercase, policy.exclude_ambiguous)
        upper = self._filter_chars(string.ascii_uppercase, policy.exclude_ambiguous)
        digits = self._filter_chars(string.digits, policy.exclude_ambiguous)

        groups = []
        if policy.require_lower:
            groups.append(lower)
        if policy.require_upper:
            groups.append(upper)
        if policy.require_digits:
            groups.append(digits)
        if policy.require_symbols:
            groups.append(self._SYMBOLS)

        all_chars = "".join(groups)
        if not all_chars:
            raise ValueError("Policy does not allow any character groups.")

        password_chars = [secrets.choice(group) for group in groups]
        password_chars.extend(secrets.choice(all_chars) for _ in range(target_len - len(password_chars)))
        secrets.SystemRandom().shuffle(password_chars)
        return "".join(password_chars)

    def validate(self, password: str, platform_type: str) -> bool:
        policy = self.get_policy(platform_type)
        if len(password) < policy.min_length:
            return False

        checks = [
            any(c.islower() for c in password) if policy.require_lower else True,
            any(c.isupper() for c in password) if policy.require_upper else True,
            any(c.isdigit() for c in password) if policy.require_digits else True,
            any(c in self._SYMBOLS for c in password) if policy.require_symbols else True,
        ]
        return all(checks)

    def _filter_chars(self, chars: str, exclude_ambiguous: bool) -> str:
        if not exclude_ambiguous:
            return chars
        return "".join(c for c in chars if c not in self._AMBIGUOUS)


class PasswordGeneratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Strong Password Generator")
        self.root.geometry("520x290")
        self.root.resizable(False, False)

        self.generator = StrongPasswordGenerator()
        self.platform_var = tk.StringVar(value="default")
        self.length_var = tk.IntVar(value=self.generator.get_policy("default").min_length)
        self.password_var = tk.StringVar(value="")

        self._build_ui()
        self._update_policy_note()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Platform Type").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 8))
        platforms = list(self.generator.policies.keys())
        platform_menu = ttk.Combobox(
            frame,
            textvariable=self.platform_var,
            values=platforms,
            state="readonly",
            width=20,
        )
        platform_menu.grid(row=0, column=1, sticky="w", pady=(0, 8))
        platform_menu.bind("<<ComboboxSelected>>", self._on_platform_change)

        ttk.Label(frame, text="Length").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 8))
        length_spin = ttk.Spinbox(
            frame,
            from_=self.generator._MIN_PASSWORD_LENGTH,
            to=self.generator._MAX_PASSWORD_LENGTH,
            textvariable=self.length_var,
            width=8,
        )
        length_spin.grid(row=1, column=1, sticky="w", pady=(0, 8))

        self.policy_note = ttk.Label(frame, text="", foreground="#444444")
        self.policy_note.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Button(frame, text="Generate Password", command=self.generate_password).grid(
            row=3, column=0, columnspan=2, sticky="we", pady=(0, 10)
        )

        output_entry = ttk.Entry(frame, textvariable=self.password_var, font=("Courier", 12), width=42)
        output_entry.grid(row=4, column=0, columnspan=2, sticky="we", pady=(0, 8))

        actions = ttk.Frame(frame)
        actions.grid(row=5, column=0, columnspan=2, sticky="we")
        ttk.Button(actions, text="Copy", command=self.copy_password).pack(side="left")
        ttk.Button(actions, text="Validate", command=self.validate_password).pack(side="left", padx=(8, 0))

        frame.columnconfigure(1, weight=1)

    def _on_platform_change(self, _event: object) -> None:
        platform = self.platform_var.get()
        min_length = self.generator.get_policy(platform).min_length
        self.length_var.set(max(self.length_var.get(), min_length))
        self._update_policy_note()

    def _update_policy_note(self) -> None:
        platform = self.platform_var.get()
        policy = self.generator.get_policy(platform)
        symbols = "Yes" if policy.require_symbols else "No"
        text = f"Minimum length: {policy.min_length} | Symbols required: {symbols}"
        self.policy_note.config(text=text)

    def generate_password(self) -> None:
        platform = self.platform_var.get()
        try:
            length = int(self.length_var.get())
            if not self.generator._MIN_PASSWORD_LENGTH <= length <= self.generator._MAX_PASSWORD_LENGTH:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid length",
                "Enter a valid length between "
                f"{self.generator._MIN_PASSWORD_LENGTH} and {self.generator._MAX_PASSWORD_LENGTH}.",
            )
            return

        try:
            password = self.generator.generate(platform, length)
        except ValueError as exc:
            messagebox.showerror("Invalid length", str(exc))
            return
        self.password_var.set(password)

    def copy_password(self) -> None:
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("No password", "Generate a password first.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def validate_password(self) -> None:
        password = self.password_var.get().strip()
        platform = self.platform_var.get()

        if not password:
            messagebox.showwarning("No password", "Generate or enter a password first.")
            return

        if self.generator.validate(password, platform):
            messagebox.showinfo("Valid", "Password satisfies the selected platform policy.")
        else:
            min_length = self.generator.get_policy(platform).min_length
            messagebox.showerror(
                "Not valid",
                f"Password does not satisfy '{platform}' policy (minimum length: {min_length}).",
            )


def main() -> None:
    root = tk.Tk()
    PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
