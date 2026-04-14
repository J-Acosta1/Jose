# HTTP Directory Bruteforcer

A simple Python script for discovering hidden directories on web servers during penetration testing.

## Features

- Takes a target URL and wordlist file as arguments
- Sends HTTP GET requests to test for directory existence
- Reports found directories (200 OK), forbidden access (403), and redirects (301/302)
- Includes error handling for connection issues and timeouts
- Respects server load with small delays between requests

## Usage

```bash
python http_bruteforcer.py <target_url> <wordlist_file>
```

Example:
```bash
python http_bruteforcer.py http://example.com common_dirs.txt
```

## Requirements

- Python 3.x
- requests library (`pip install requests`)

## Wordlist Format

The wordlist should contain one directory name per line, e.g.:
```
admin
backup
config
css
images
js
login
test
```

## Important Notes

- **Use only on systems you have explicit permission to test**
- This tool is for educational and authorized penetration testing purposes only
- Be aware of legal implications and terms of service
- Some servers may block or rate-limit automated requests
- Consider using a proxy or VPN for testing

## Output

The script will display:
- `[+]` for found directories (200 status)
- `[!]` for forbidden directories (403 status)
- `[>]` for redirects (301/302 status)
- `[-]` for errors or inaccessible URLs