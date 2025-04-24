import yaml
import requests
import time
from collections import defaultdict

# Load configuration from YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Perform a health check on a given endpoint
def check_health(endpoint):
    url = endpoint['url']
    method = endpoint.get('method', 'GET').upper()
    headers = endpoint.get('headers', {})
    body = endpoint.get('body', None)

    try:
        start_time = time.time()
        response = requests.request(method, url, headers=headers, json=body, timeout=5)
        elapsed_ms = (time.time() - start_time) * 1000  # in milliseconds

        if 200 <= response.status_code < 300 and elapsed_ms <= 500:
            return "UP"
        else:
            return "DOWN"
    except requests.RequestException:
        return "DOWN"

# Monitor all endpoints continuously
def monitor_endpoints(file_path):
    config = load_config(file_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    while True:
        cycle_start = time.time()
        print(f"--- Starting Check Cycle ---")

        for endpoint in config:
            url = endpoint["url"]
            name = endpoint.get("name", url)

            domain = url.split("//")[-1].split("/")[0].split(":")[0]  # Remove port if present
            result = check_health(endpoint)

            domain_stats[domain]["total"] += 1
            if result == "UP":
                domain_stats[domain]["up"] += 1

            print(f"[{name}] ({domain}) status: {result}")

        print("\n--- Availability Summary ---")
        for domain, stats in domain_stats.items():
            availability = int(100 * stats["up"] / stats["total"])
            print(f"{domain}: {availability}% availability")

        print("--- End of Check ---\n")

        # Wait until 15 seconds total cycle time has passed
        elapsed = time.time() - cycle_start
        time.sleep(max(0, 15 - elapsed))

# Entry point of the script
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
