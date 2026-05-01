import argparse
import logging
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from colorama import Fore, Style, init
from tqdm import tqdm

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
COMMON_USER_AGENTS = [
    DEFAULT_USER_AGENT,
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]


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
        default=10.0,
        help="HTTP request timeout in seconds (default: 10.0)",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=0.1,
        help="Base delay between requests in seconds (default: 0.1)",
    )
    parser.add_argument(
        "-j",
        "--jitter",
        type=float,
        default=0.0,
        help="Additional random jitter added to delay in seconds (default: 0.0)",
    )
    parser.add_argument(
        "-u",
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Custom User-Agent header to use for all requests.",
    )
    parser.add_argument(
        "-r",
        "--random-user-agent",
        action="store_true",
        help="Rotate User-Agent values randomly from the built-in list.",
    )
    proxy_group = parser.add_mutually_exclusive_group()
    proxy_group.add_argument(
        "--proxy",
        help="HTTP/HTTPS proxy URL to use for requests, e.g. http://127.0.0.1:8080",
    )
    proxy_group.add_argument(
        "--proxy-file",
        help="File containing one proxy URL per line.",
    )
    parser.add_argument(
        "--stealth",
        action="store_true",
        help="Enable stealth mode: slower jitter, minimal output, and quieter scan behavior.",
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


def load_wordlist(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return [line.strip() for line in handle if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"Wordlist file not found: {path}")


def load_proxy_list(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            proxies = [line.strip() for line in handle if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty")
            return proxies
    except FileNotFoundError:
        raise FileNotFoundError(f"Proxy file not found: {path}")


def normalize_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Target URL must begin with http:// or https://")
    return url if url.endswith("/") else url + "/"


def get_user_agent(base_user_agent, randomize):
    if randomize:
        return random.choice(COMMON_USER_AGENTS)
    return base_user_agent


def choose_proxy(proxy, proxy_list):
    if proxy_list:
        proxy_url = random.choice(proxy_list)
        return {"http": proxy_url, "https": proxy_url}
    if proxy:
        return {"http": proxy, "https": proxy}
    return None


def delay_with_jitter(base_delay, jitter):
    if base_delay <= 0 and jitter <= 0:
        return 0.0
    return max(0.0, base_delay + random.uniform(0.0, jitter))


def make_headers(user_agent, stealth):
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if stealth:
        headers.update(
            {
                "Connection": "close",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )
    return headers


def format_status(result, stealth=False):
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


def should_report(result, stealth=False):
    if result["error"]:
        return True
    if not stealth:
        return True
    return result["status"] in {200, 301, 302, 403}


def scan_directory(base_url, directory, timeout, base_user_agent, random_user_agent, proxy, proxy_list, delay, jitter, stealth):
    test_url = urljoin(base_url, directory)
    request_user_agent = get_user_agent(base_user_agent, random_user_agent)
    proxy_config = choose_proxy(proxy, proxy_list)
    headers = make_headers(request_user_agent, stealth)

    try:
        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get(
                test_url,
                timeout=timeout,
                allow_redirects=False,
                proxies=proxy_config,
            )

        return {
            "url": test_url,
            "status": response.status_code,
            "reason": response.reason,
            "redirect": response.headers.get("Location"),
            "error": None,
            "directory": directory,
            "user_agent": request_user_agent,
            "proxy": proxy_config,
        }
    except requests.exceptions.RequestException as exc:
        return {
            "url": test_url,
            "status": None,
            "reason": None,
            "redirect": None,
            "error": str(exc),
            "directory": directory,
            "user_agent": request_user_agent,
            "proxy": proxy_config,
        }
    finally:
        wait_time = delay_with_jitter(delay, jitter)
        if wait_time > 0:
            time.sleep(wait_time)


def main():
    init(autoreset=True)
    args = parse_arguments()

    try:
        target_url = normalize_url(args.target_url)
    except ValueError as exc:
        print(Fore.RED + f"Invalid target URL: {exc}" + Style.RESET_ALL)
        sys.exit(1)

    try:
        directories = load_wordlist(args.wordlist_file)
    except (FileNotFoundError, ValueError) as exc:
        print(Fore.RED + str(exc) + Style.RESET_ALL)
        sys.exit(1)

    proxy_list = None
    if args.proxy_file:
        try:
            proxy_list = load_proxy_list(args.proxy_file)
        except (FileNotFoundError, ValueError) as exc:
            print(Fore.RED + str(exc) + Style.RESET_ALL)
            sys.exit(1)

    if not directories:
        print(Fore.YELLOW + "The wordlist is empty. Add directory names and try again." + Style.RESET_ALL)
        sys.exit(1)

    output_path = args.output or f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = create_logger(output_path)
    logger.info("Starting HTTP directory bruteforce")
    logger.info(f"Target URL: {target_url}")
    logger.info(f"Wordlist: {args.wordlist_file}")
    logger.info(f"Threads: {args.threads}, Timeout: {args.timeout}, Delay: {args.delay}, Jitter: {args.jitter}")
    logger.info(f"User-Agent: {args.user_agent}")
    logger.info(f"Random User-Agent: {args.random_user_agent}")
    logger.info(f"Proxy: {args.proxy or args.proxy_file}")
    logger.info(f"Stealth mode: {args.stealth}")

    print(Fore.CYAN + "HTTP Directory Bruteforcer" + Style.RESET_ALL)
    print(Fore.CYAN + "Target:" + Style.RESET_ALL, target_url)
    print(Fore.CYAN + "Wordlist:" + Style.RESET_ALL, args.wordlist_file)
    print(Fore.CYAN + "Output log:" + Style.RESET_ALL, output_path)
    print(Fore.CYAN + "Threads:" + Style.RESET_ALL, args.threads)
    print(Fore.CYAN + "Delay:" + Style.RESET_ALL, args.delay)
    print(Fore.CYAN + "Jitter:" + Style.RESET_ALL, args.jitter)
    if args.proxy:
        print(Fore.CYAN + "Proxy:" + Style.RESET_ALL, args.proxy)
    if args.proxy_file:
        print(Fore.CYAN + "Proxy file:" + Style.RESET_ALL, args.proxy_file)
    print(Fore.CYAN + "Stealth mode:" + Style.RESET_ALL, args.stealth)
    print(Fore.CYAN + "Random User-Agent:" + Style.RESET_ALL, args.random_user_agent)
    print("=" * 70)

    found_dirs = []
    total = len(directories)
    start_time = time.perf_counter()
    progress_disabled = args.stealth

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = {
                executor.submit(
                    scan_directory,
                    target_url,
                    directory,
                    args.timeout,
                    args.user_agent,
                    args.random_user_agent,
                    args.proxy,
                    proxy_list,
                    args.delay,
                    args.jitter,
                    args.stealth,
                ): directory
                for directory in directories
            }

            with tqdm(total=total, desc="Scanning", unit="req", ncols=100, disable=progress_disabled) as progress:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                    except Exception as exc:
                        logger.error(f"Worker failed: {exc}")
                        continue

                    progress.update(1)
                    if not should_report(result, stealth=args.stealth):
                        continue

                    status_line = f"{format_status(result, stealth=args.stealth)} {result['url']}"
                    if result["error"]:
                        status_line += f" - {result['error']}"
                        logger.error(status_line)
                    else:
                        status_line += f" (Status: {result['status']})"
                        if result["status"] in (301, 302) and result["redirect"]:
                            status_line += f" -> {result['redirect']}"
                        logger.info(status_line)

                    print(status_line)
                    if result.get("status") == 200:
                        found_dirs.append(result["url"])

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

#Set-Content -LiteralPath 'c:\Users\Acost\W2\http_bruteforcer.py' -Value $code -Encoding utf8