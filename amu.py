import subprocess
import re
def get_saved_wifi_names():
    try:
        # Dump keychain and extract SSIDs
        output = subprocess.check_output(
            ["security", "dump-keychain"],
            stderr=subprocess.DEVNULL,
            text=True
        )

        ssids = set()

        for line in output.split("\n"):
            if "acct" in line:
                match = re.search(r'"acct"<blob>="(.*?)"', line)
                if match:
                    ssids.add(match.group(1))

        return list(ssids)

    except Exception as e:
        print("Error fetching WiFi names:", e)
        return []
def get_wifi_password(ssid):
    try:
        command = f'security find-generic-password -ga "{ssid}"'
        output = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in output.split("\n"):
            if "password:" in line:
                return line.split("password:")[1].strip().strip('"')

        return "No password found"

    except subprocess.CalledProcessError:
        return "Access denied / Not saved"


def main():
    print("\nSaved WiFi Networks & Passwords (macOS)\n")
    print("-" * 50)

    ssids = get_saved_wifi_names()

    if not ssids:
        print("No WiFi networks found.")
        return

    for ssid in ssids:
        password = get_wifi_password(ssid)
        print(f"WiFi Name : {ssid}")
        print(f"Password  : {password}")
        print("-" * 50)


if __name__ == "__main__":
    main()