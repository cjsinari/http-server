import socket  # noqa: F401
import threading
import argparse
import os

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

        #Extracting file path from OS and reading Content-Length:
        elif request_path.startswith("/files/"):
            filename = request_path[len("/files/"):]
            filepath = os.path.join(FILES_DIRECTORY, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "rb") as f:
                        content = f.read()
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(content)}\r\n"
                        "\r\n"
                    )  
                    client.sendall(response_headers.encode() + content)  

                except Exception as e:
                    print(f"Error reading file:{e}")
                    client.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")     

            else:
              client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

        else:
            client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")     
    
    except Exception as e:
        print(f"Error handling client: {e}")      
    finally:
        client.close()    


def main():
    global FILES_DIRECTORY

    print("Logs from your program will appear here!")
    
    #Parsing arguments to file directory to extract file
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, help="Absolute path to the file directory")
    args = parser.parse_args()
    FILES_DIRECTORY = args.directory

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
