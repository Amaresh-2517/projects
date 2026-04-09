import os
from cryptography.fernet import Fernet
from utils import generate_key

def encrypt_file(filename, password):
    salt = os.urandom(16)
    key = generate_key(password, salt)
    fernet = Fernet(key)

    with open(filename, 'rb') as file:
        data = file.read()

    encrypted = fernet.encrypt(data)

    with open(filename + ".enc", 'wb') as file:
        file.write(salt + encrypted)

    print("File encrypted successfully!")

if __name__ == "__main__":
    file = input("Enter file name: ")
    password = input("Enter password: ")
    encrypt_file(file, password)