
import datetime
import socket
import argparse
import sys
import concurrent.futures
from datetime import datetime

from server import get_timestamp 

def scan_port(host, port):
    """
    Scan a single port on the given host.
    
    Args:
        host (str): The IP address of the target host.
        port (int): The port number to scan.
    
    Returns:
        bool: True if the port is open, False otherwise.
    """
    def get_timestamp():
#Returns the current timestamp in a readable format for logging purposes.
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a timeout to avoid hanging on unresponsive ports
        sock.settimeout(1)
        # Attempt to connect to the port
        result = sock.connect_ex((host, port))
        # Close the socket
        sock.close()
        # connect_ex returns 0 if successful (port open)
        return result == 0
    except socket.error as e:
        # Handle socket errors (e.g., network issues)
        print(f"[{get_timestamp()}] Error scanning port {port}: {e}")
        return False

def main():
    """
    Main function to parse arguments and perform port scanning.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Simple Port Scanner')
    parser.add_argument('host', help='Target host (IP or domain)')
    parser.add_argument('-p', '--ports', default='1-1024', 
                        help='Port range or list, e.g., 1-100 or 80,443,22')
    args = parser.parse_args()
    
    host = args.host
    
    # Resolve the host to an IP address
    try:
        ip = socket.gethostbyname(host)
        print(f"[{get_timestamp()}] Scanning host: {host} ({ip})")
    except socket.gaierror:
        print(f"Error: Unable to resolve host {host}")
        sys.exit(1)
    
    # Parse the port specification
    try:
        if '-' in args.ports:
            # Handle range like 1-100
            start, end = map(int, args.ports.split('-'))
            if start < 1 or end > 65535 or start > end:
                raise ValueError("Invalid port range")
            ports = list(range(start, end + 1))
        elif ',' in args.ports:
            # Handle list like 80,443,22
            ports = [int(p.strip()) for p in args.ports.split(',')]
            for p in ports:
                if p < 1 or p > 65535:
                    raise ValueError("Port out of range")
        else:
            # Single port
            port = int(args.ports)
            if port < 1 or port > 65535:
                raise ValueError("Port out of range")
            ports = [port]
    except ValueError as e:
        print(f"[{get_timestamp()}] Error: Invalid port specification. {e}. Use format like 80 or 1-100 or 80,443,22")
        sys.exit(1)
    
    print(f"[{get_timestamp()}] Scanning {len(ports)} ports...")
    
    # Lists to track open and closed ports
    open_ports = []
    closed_ports = []
    
    # Use ThreadPoolExecutor for concurrent scanning to improve performance
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Submit scan tasks
        futures = {executor.submit(scan_port, ip, port): port for port in ports}
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            try:
                is_open = future.result()
                if is_open:
                    open_ports.append(port)
                    print(f"[{get_timestamp()}] Port {port}: OPEN")
                else:
                    closed_ports.append(port)
                    print(f"[{get_timestamp()}] Port {port}: CLOSED")
            except Exception as e:
                print(f"[{get_timestamp()}] Unexpected error scanning port {port}: {e}")
    
    # Print summary
    print(f"[{get_timestamp()}] Summary: {len(open_ports)} open ports, {len(closed_ports)} closed ports")
    if open_ports:
        print(f"[{get_timestamp()}] Open ports: {', '.join(map(str, sorted(open_ports)))}")

if __name__ == "__main__":
    main()