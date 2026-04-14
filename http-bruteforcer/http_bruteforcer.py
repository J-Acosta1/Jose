import requests
import sys
import time
from urllib.parse import urljoin

# HTTP Directory Bruteforcer for Penetration Testing
# This script attempts to discover hidden directories on a web server
# by trying common directory names from a wordlist.
# Use responsibly and only on systems you have permission to test.

def main():
    if len(sys.argv) != 3:
        print("Usage: python http_bruteforcer.py <target_url> <wordlist_file>")
        print("Example: python http_bruteforcer.py http://example.com wordlist.txt")
        sys.exit(1)

    target_url = sys.argv[1]
    wordlist_file = sys.argv[2]

    # Ensure target URL ends with /
    if not target_url.endswith('/'):
        target_url += '/'

    print(f"Starting directory bruteforce on: {target_url}")
    print(f"Using wordlist: {wordlist_file}")
    print("-" * 50)

    try:
        # Read the wordlist
        with open(wordlist_file, 'r') as file:
            directories = [line.strip() for line in file if line.strip()]

        print(f"Loaded {len(directories)} directories from wordlist.")
        print("Scanning... (this may take a while)\n")

        found_dirs = []

        for directory in directories:
            # Construct the full URL
            test_url = urljoin(target_url, directory)

            try:
                # Send GET request with a timeout
                response = requests.get(test_url, timeout=5)

                # Check for successful response (200 OK)
                if response.status_code == 200:
                    print(f"[+] Found: {test_url} (Status: {response.status_code})")
                    found_dirs.append(test_url)
                elif response.status_code == 403:
                    print(f"[!] Forbidden: {test_url} (Status: {response.status_code})")
                elif response.status_code == 301 or response.status_code == 302:
                    print(f"[>] Redirect: {test_url} -> {response.headers.get('Location', 'Unknown')} (Status: {response.status_code})")

                # Add a small delay to avoid overwhelming the server
                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                # Handle connection errors, timeouts, etc.
                print(f"[-] Error accessing {test_url}: {str(e)}")
            except KeyboardInterrupt:
                print("\n[!] Scan interrupted by user.")
                break

        print("\n" + "=" * 50)
        print(f"Scan complete. Found {len(found_dirs)} directories.")
        if found_dirs:
            print("Discovered directories:")
            for dir_url in found_dirs:
                print(f"  - {dir_url}")

    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()