import socket  # noqa: F401
import threading


def handle_client(client):
    #Handles a single client request in a separate thread
    try:
        request_data = client.recv(4096).decode()
        client_msg = request_data.split(" ")
        print(f"Received request: {client_msg}")  # Debugging output

         
        if len(client_msg) < 2:
            client.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            client.close()
            return

        request_path = client_msg[1]

        if request_path == "/":
            client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")

        elif request_path.startswith("/echo/"):
            value = request_path[6:]  # Extract text after "/echo/"
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
            client.sendall(response.encode())

        #Read user agent header
        elif request_path.startswith("/user-agent"):
          user_agent = next((line.split(": ", 1)[1] for line in request_data.split("\r\n") if line.lower().startswith("user-agent:")), "Unknown")             
          response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}" 
          client.sendall(response.encode())

        else:
          client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    
    except Exception as e:
        print(f"Error handling client: {e}")      
    finally:
        client.close()    


def main():

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    print ("Server is listening on port 4221...")


    while True:  # Allow multiple connections
        client, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")

        #Create a new thread for each client request
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

    
if __name__ == "__main__":
    main()
