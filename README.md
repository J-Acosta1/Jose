# Jose# Socket Connection Project

This project demonstrates a basic client-server communication system using Python sockets.

## Files

- `server.py`: The server script that listens for connections and handles client requests.
- `client.py`: The client script that connects to the server and sends/receives messages.

## Usage

1. Run the server first:
   ```
   python server.py
   ```

2. In another terminal, run the client:
   ```
   python client.py
   ```

The client will send a message to the server, and the server will respond.

## Requirements

- Python 3.x (socket module is built-in)

## Notes

- The server listens on localhost:12345.
- This is a simple example for educational purposes.
- For production use, consider security implications and proper error handling.