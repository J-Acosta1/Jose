import socket
from datetime import datetime

#Helper function to generate a timestamp for logging
def get_timestamp():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
# Server script for basic client-server communication using sockets

def main():
    # Define the host and port for the server
    HOST = 'localhost'
    PORT = 12345

    try:
        # Create a socket object using IPv4 and TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[{get_timestamp()}] Socket created successfully.")

        # Bind the socket to the host and port
        server_socket.bind((HOST, PORT))
        print(f"Socket bound to {HOST}:{PORT}.")

        # Listen for incoming connections (max 1 queued connection)
        server_socket.listen(1)
        print(f"Server is listening for connections...")

        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"[{get_timestamp()}] Connection established with {client_address}.")

        # Receive data from the client (up to 1024 bytes)
        data = client_socket.recv(1024)
        if data:
            print(f"[{get_timestamp()}] Received data: {data.decode('utf-8')}")

            # Send a response back to the client
            response = "Hello from server!"
            client_socket.send(response.encode('utf-8'))
            print(f"Response sent to client.")

        # Close the client socket
        client_socket.close()
        print(f"[{get_timestamp()}] Client connection closed.")

    except socket.error as e:
        print(f"[{get_timestamp()}] Socket error: {e}")
    except Exception as e:
        print(f"[{get_timestamp()}] An error occurred: {e}")
    finally:
        # Close the server socket
        try:
            server_socket.close()
            rint(f"[get_timestampServer socket closed.")
        except:
            pass

if __name__ == "__main__":
    main()