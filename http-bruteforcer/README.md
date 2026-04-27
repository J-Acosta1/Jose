# HTTP Brute Forcer

A Python-based HTTP authentication brute force tool for testing and security research.

## Features

- Brute force HTTP Basic Authentication
- Customizable wordlist support
- Efficient multi-threaded requests
- Detailed logging and reporting
- Progress tracking

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python http_bruteforcer.py --url <target_url> --wordlist <wordlist_file>
```

### Arguments

- `--url`: Target URL to brute force (required)
- `--wordlist`: Path to wordlist file (required)
- `--threads`: Number of threads (default: 5)
- `--timeout`: Request timeout in seconds (default: 5)

### Example

```bash
python http_bruteforcer.py --url http://target.com --wordlist wordlist.txt --threads 10
```

## Wordlist Format

The wordlist file should contain one credential per line in the format:
```
username:password
```

## Disclaimer

This tool is for authorized security testing and educational purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before conducting penetration testing.

## License

MIT License
