import argparse
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urljoin

import requests
from colorama import Fore, Style, init
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="HTTP directory bruteforcer for penetration testing. Use only with permission."
    )
    parser.add_argument("target_url", help="Target URL to scan, e.g. http://example.com")
    parser.add_argument("wordlist_file", help="Path to the wordlist file")
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=10,
        help="Number of parallel threads to use (default: 10)",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        type=float,
        default=5.0,
        help="HTTP request timeout in seconds (default: 5.0)",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=0.1,
        help="Delay between requests in seconds (default: 0.1)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Optional output log file. Defaults to results_<timestamp>.log",
    )
    return parser.parse_args()


def create_logger(filepath):
    logger = logging.getLogger("http_bruteforcer")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(filepath, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def format_status(result):
    if result["error"]:
        return Fore.RED + "[-] ERROR" + Style.RESET_ALL

    status = result["status"]
    if status == 200:
        return Fore.GREEN + "[FOUND]" + Style.RESET_ALL
    if status == 403:
        return Fore.YELLOW + "[FORBIDDEN]" + Style.RESET_ALL
    if status in (301, 302):
        return Fore.CYAN + "[REDIRECT]" + Style.RESET_ALL
    if status == 404:
        return Fore.WHITE + "[NOT FOUND]" + Style.RESET_ALL
    if status >= 500:
        return Fore.MAGENTA + "[SERVER ERROR]" + Style.RESET_ALL

    return Fore.BLUE + "[STATUS]" + Style.RESET_ALL


def scan_directory(base_url, directory, timeout):
    test_url = urljoin(base_url, directory)
    try:
        response = requests.get(test_url, timeout=timeout, allow_redirects=False)
        return {
            "url": test_url,
            "status": response.status_code,
            "reason": response.reason,
            "redirect": response.headers.get("Location"),
            "error": None,
            "directory": directory,
        }
    except requests.exceptions.RequestException as exc:
        return {
            "url": test_url,
            "status": None,
            "reason": None,
            "redirect": None,
            "error": str(exc),
            "directory": directory,
        }


def normalize_url(url):
    return url if url.endswith("/") else url + "/"


def main():
    init(autoreset=True)
    args = parse_arguments()

    target_url = normalize_url(args.target_url)
    output_path = args.output or f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    results = []

    try:
        with open(args.wordlist_file, "r", encoding="utf-8") as wordlist:
            directories = [line.strip() for line in wordlist if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + f"Error: wordlist file '{args.wordlist_file}' not found." + Style.RESET_ALL)
        sys.exit(1)

    if not directories:
        print(Fore.YELLOW + "The wordlist is empty. Add directory names and try again." + Style.RESET_ALL)
        sys.exit(1)

    logger = create_logger(output_path)
    logger.info("Starting HTTP directory bruteforce")
    logger.info(f"Target URL: {target_url}")
    logger.info(f"Wordlist: {args.wordlist_file}")
    logger.info(f"Threads: {args.threads}, Timeout: {args.timeout}, Delay: {args.delay}")

    print(Fore.CYAN + "HTTP Directory Bruteforcer" + Style.RESET_ALL)
    print(Fore.CYAN + "Target:" + Style.RESET_ALL, target_url)
    print(Fore.CYAN + "Wordlist:" + Style.RESET_ALL, args.wordlist_file)
    print(Fore.CYAN + "Output log:" + Style.RESET_ALL, output_path)
    print(Fore.CYAN + "Threads:" + Style.RESET_ALL, args.threads)
    print("=" * 70)

    found_dirs = []
    total = len(directories)
    start_time = time.perf_counter()

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {executor.submit(scan_directory, target_url, directory, args.timeout): directory for directory in directories}
            with tqdm(total=total, desc="Scanning", unit="req", ncols=100) as progress:
                for future in as_completed(futures):
                    result = future.result()
                    progress.update(1)

                    if result["error"]:
                        line = f"{format_status(result)} {result['url']} - {result['error']}"
                        logger.error(line)
                        print(line)
                        continue

                    status_line = f"{format_status(result)} {result['url']} (Status: {result['status']})"
                    if result["status"] in (301, 302) and result["redirect"]:
                        status_line += f" -> {result['redirect']}"

                    logger.info(status_line)
                    print(status_line)

                    if result["status"] == 200:
                        found_dirs.append(result["url"])

                    if args.delay > 0:
                        time.sleep(args.delay)

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nScan interrupted by user." + Style.RESET_ALL)
        logger.warning("Scan interrupted by user")

    finally:
        elapsed = time.perf_counter() - start_time
        summary = (
            "\n" + "=" * 70 + "\n"
            + f"Scan complete. Total tested: {total}\n"
            + f"Directories found: {len(found_dirs)}\n"
            + f"Elapsed time: {elapsed:.2f} seconds\n"
            + f"Log file: {output_path}\n"
        )
        logger.info(summary)
        print(summary)

        if found_dirs:
            print(Fore.GREEN + "Discovered directories:" + Style.RESET_ALL)
            for url in found_dirs:
                print(Fore.GREEN + "  - " + url + Style.RESET_ALL)

    return 0


if __name__ == "__main__":
    main()