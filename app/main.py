import socket  # noqa: F401


def main():

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    while True:  # Allow multiple connections
        client, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")

        client_msg = client.recv(4096).decode().split(" ")
        print(f"Received request: {client_msg}")  # Debugging output

        if len(client_msg) < 2:
            client.sendall(b"HTTP/1.1 400 Request Failed\r\n\r\n")
            client.close()
            continue

        request_path = client_msg[1]

        if request_path == "/":
            client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        elif request_path.startswith("/echo/"):
            value = request_path[6:]  # Extract text after "/echo/"
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
            client.sendall(response.encode())
        else:
            client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

        client.close()  # Close the connection after handling the request


if __name__ == "__main__":
    main()
