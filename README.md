# Python Password Tools

This repository contains a small collection of Python scripts related to password generation, password strength estimation, and simple Tkinter GUI apps.

## Files

- `password_generator.py`: GUI app to generate strong passwords based on platform type.
- `password_crack.py`: CLI script to estimate password crack time.
- `password_crack_gui.py`: GUI version of the password crack time estimator.
- `passgen.py`: simple CLI password generator.
- `loginpage.py`: basic Tkinter login page demo.
- `amu.py`: macOS script that attempts to list saved Wi-Fi names and passwords from the keychain.

## Requirements

- Python 3
- Tkinter for GUI apps
- macOS only for `amu.py`

## Run

```bash
python3 password_generator.py
python3 password_crack.py
python3 password_crack_gui.py
python3 passgen.py
python3 loginpage.py
python3 amu.py
```

## Notes

- `password_crack.py` and `password_crack_gui.py` provide rough estimates only.
- `loginpage.py` uses demo credentials and is not intended for real authentication.
- `amu.py` depends on macOS keychain access and may require permissions.
