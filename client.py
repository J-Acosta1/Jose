import socket
from datetime import datetime

#Helper function to generate a timestamp for logging
def get_timestamp():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Client script for basic client-server communication using sockets

def main():
    # Define the host and port to connect to (server details)
    HOST = 'localhost'
    PORT = 12345

    try:
        # Create a socket object using IPv4 and TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[{get_timestamp()}] Socket created successfully.")

        # Connect to the server
        client_socket.connect((HOST, PORT))
        print(f"[{get_timestamp()}] Connected to server at {HOST}:{PORT}.")

        # Send data to the server
        message = "Hello from client!"
        client_socket.send(message.encode('utf-8'))
        print(f"[{get_timestamp()}] Message sent to server.")

        # Receive response from the server (up to 1024 bytes)
        data = client_socket.recv(1024)
        if data:
            print(f"[{get_timestamp()}] Received response: {data.decode('utf-8')}")

    except socket.error as e:
        print(f"[{get_timestamp()}] Socket error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the client socket
        try:
            client_socket.close()
            print(f"[{get_timestamp()}] Client socket closed.")
        except:
            pass

if __name__ == "__main__":
    main()