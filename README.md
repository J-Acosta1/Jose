[![GitHub Repo](https://img.shields.io/badge/GitHub-Jose-blue?logo=github)](https://github.com/J-Acosta1/Jose)

# Jose

This repository contains various Python scripts for networking and penetration testing.

## Socket Connection Project

This project demonstrates a basic client-server communication system using Python sockets.

### Files

- `server.py`: The server script that listens for connections and handles client requests.
- `client.py`: The client script that connects to the server and sends/receives messages.

### Usage

1. Run the server first:
   ```
   python server.py
   ```

2. In another terminal, run the client:
   ```
   python client.py
   ```

The client will send a message to the server, and the server will respond.

### Requirements

- Python 3.x (socket module is built-in)

### Notes

- The server listens on localhost:12345.
- This is a simple example for educational purposes.
- For production use, consider security implications and proper error handling.

## HTTP Directory Bruteforcer

A penetration testing tool for discovering hidden directories on web servers.

### Files

- `http_bruteforcer.py`: The main bruteforcing script
- `HTTP_BRUTEFORCER_README.md`: Detailed documentation for the bruteforcer
- `common_dirs.txt`: Sample wordlist of common directory names

### Usage

```bash
python http_bruteforcer.py <target_url> <wordlist_file>
```

Example:
```bash
python http_bruteforcer.py http://example.com common_dirs.txt
```

### Requirements

- Python 3.x
- `requests`
- `tqdm`
- `colorama`

Install dependencies with:
```bash
pip install -r requirements.txt
```

### Important Notes

- **Use only on systems you have explicit permission to test**
- This tool is for educational and authorized penetration testing purposes only
- Be aware of legal implications and terms of service