# HTTP Directory Bruteforcer

A multithreaded HTTP directory bruteforcer for penetration testing and web application discovery.

## Overview

This tool scans a target web server using a directory wordlist and reports:
- discovered directories (`200 OK`)
- forbidden paths (`403`)
- redirects (`301` / `302`)
- request errors and timeouts

It includes:
- colored console output
- a progress bar
- threaded scanning for faster enumeration
- optional User-Agent customization and random rotation
- optional proxy support and proxy file rotation
- optional delay with jitter and stealth mode
- log file output
- elapsed scan timing and summary

## Files

- `http_bruteforcer.py`: Main bruteforcing script
- `common_dirs.txt`: Example directory wordlist
- `requirements.txt`: Python dependencies

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python http_bruteforcer.py <target_url> <wordlist_file>
```

Example:

```bash
python http_bruteforcer.py http://example.com common_dirs.txt
```

## Options

- `-t`, `--threads`: number of worker threads (default: 10)
- `-T`, `--timeout`: request timeout in seconds (default: 10.0)
- `-d`, `--delay`: base delay between requests in seconds (default: 0.1)
- `-j`, `--jitter`: additional random delay added to each request (default: 0.0)
- `-u`, `--user-agent`: custom User-Agent header for all requests
- `-r`, `--random-user-agent`: rotate User-Agent values randomly from a built-in list
- `--proxy`: HTTP/HTTPS proxy URL to use for requests
- `--proxy-file`: file containing one proxy URL per line
- `--stealth`: enable stealth mode with quieter reporting and slower behavior
- `-o`, `--output`: set a custom log file path

Example with options:

```bash
python http_bruteforcer.py http://example.com common_dirs.txt -t 20 -T 5 -d 0.05 -j 0.1 -r --proxy http://127.0.0.1:8080 --stealth -o scan_results.log
```

## Examples

Use a single proxy for all requests:

```bash
python http_bruteforcer.py http://example.com common_dirs.txt --proxy http://127.0.0.1:8080
```

Use a proxy list and enable stealth mode:

```bash
python http_bruteforcer.py http://example.com common_dirs.txt --proxy-file proxies.txt --stealth -d 0.2 -j 0.15
```

## Output

The script prints scan progress and status messages to the console, and writes details to a log file. At the end of the run it shows:
- total requests tested
- directories found
- elapsed time
- log file path

## Important Notes

- Use this tool only on systems where you have explicit permission to test.
- Unauthorized scanning is illegal and unethical.
- This script is for educational and authorized penetration testing use only.
