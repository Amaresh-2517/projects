import string
def estimate_crack_time(password):
    charset_size = 0

    if any(c.islower() for c in password):
        charset_size += 26

    if any(c.isupper() for c in password):
        charset_size += 26

    if any(c.isdigit() for c in password):
        charset_size += 10

    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)

    length = len(password)

    combinations = charset_size ** length

    guesses_per_second = 1_000_000_000  # 1 billion guesses per second

    seconds = combinations / guesses_per_second

    return seconds


def format_time(seconds):

    years = int(seconds // (365*24*3600))
    seconds %= (365*24*3600)

    months = int(seconds // (30*24*3600))
    seconds %= (30*24*3600)

    days = int(seconds // (24*3600))
    seconds %= (24*3600)

    hours = int(seconds // 3600)
    seconds %= 3600

    minutes = int(seconds // 60)
    seconds = int(seconds % 60)

    return f"{years} years {months} months {days} days {hours} hours {minutes} minutes {seconds} seconds"


password = input("Enter password: ")
seconds = estimate_crack_time(password)
formatted_time = format_time(seconds)

print("\nEstimated Crack Time:")
print(formatted_time)