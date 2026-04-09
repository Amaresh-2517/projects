from cryptography.fernet import Fernet
from utils import generate_key

def decrypt_file(filename, password):
    with open(filename, 'rb') as file:
        data = file.read()

    salt = data[:16]
    encrypted_data = data[16:]

    key = generate_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted_data)

        output_file = filename.replace(".enc", "_decrypted")
        with open(output_file, 'wb') as file:
            file.write(decrypted)

        print("File decrypted successfully!")

    except:
        print("Wrong password or corrupted file!")

if __name__ == "__main__":
    file = input("Enter encrypted file: ")
    password = input("Enter password: ")
    decrypt_file(file, password)