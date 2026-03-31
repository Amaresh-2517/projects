import random
import string

def generate_password(platform):

    if platform == "bank":
        length = 16
        chars = string.ascii_letters + string.digits + string.punctuation

    elif platform == "email":
        length = 14
        chars = string.ascii_letters + string.digits

    elif platform == "social":
        length = 12
        chars = string.ascii_letters + string.digits + string.punctuation

    elif platform == "wifi":
        length = 20
        chars = string.ascii_letters + string.digits + string.punctuation

    else:
        length = 10
        chars = string.ascii_letters + string.digits

    password = ''.join(random.choice(chars) for i in range(length))
    return password


platform = input("Enter platform (bank/email/social/wifi/normal): ")

password = generate_password(platform.lower())

print("Generated Strong Password:", password)