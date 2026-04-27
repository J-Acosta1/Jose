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
- `-T`, `--timeout`: request timeout in seconds (default: 5.0)
- `-d`, `--delay`: delay between requests in seconds (default: 0.1)
- `-o`, `--output`: set a custom log file path

Example with options:

```bash
python http_bruteforcer.py http://example.com common_dirs.txt -t 20 -T 3 -d 0.05 -o scan_results.log
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
