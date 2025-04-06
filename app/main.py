import socket  # noqa: F401
import threading
import argparse
import os
import gzip
from io import BytesIO

def handle_client(client):
    #Handles a single client request in a separate thread
    try:
        request_data = client.recv(4096).decode()
        client_msg = request_data.split(" ")
        print(f"Received request: {client_msg}")  # Debugging output

         
        if len(client_msg) < 2:
            client.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return

        method = client_msg[0]
        request_path = client_msg[1]
        headers = request_data.split("\r\n")

        #Extract Accept-Encoding header if present
        accept_encoding = ""
        for header in headers:
            if header.lower().startswith("accept-encoding"):
                accept_encoding = header.split(":", 1)[1].strip()
                break

             
        if request_path == "/":
            client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")

        elif request_path.startswith("/echo/"):
            value = request_path[6:]  # Extract text after "/echo/"
            
            #Searching for gzip in compression header
            if "gzip" in accept_encoding:
                out = BytesIO()
                with gzip.GzipFile(fileobj=out, mode="wb") as f:
                    f.write(value.encode())
                compressed = out.getvalue()    
                response =( 
                 "HTTP/1.1 200 OK\r\n"
                 "Content-Type: text/plain\r\n"
                 f"Content-Encoding: gzip\r\n"
                 f"Content-Length: {len(compressed)}\r\n"
                 "\r\n"
                ).encode() + compressed               
                client.sendall(response)
            
            else:
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
                )
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

            if method == "GET":
              print(f"Looking for file: {filepath}")
              if os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        content = f.read()
                    response_headers = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(content)}\r\n"
                        "\r\n"
                    )  
                    client.sendall(response_headers.encode() + content) 
                
              else:
                   client.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


            elif method == "POST":
                # Split request manually to get body after \r\n\r\n
                try:
                    header_part, body = request_data.split("\r\n\r\n", 1)
                    body_bytes = body.encode()
                    with open(filepath, "wb") as f:
                        f.write(body_bytes)

                    client.sendall(b"HTTP/1.1 201 Created\r\n\r\n")
                except Exception as e:
                    print(f"Error writing file:{e}")
                    client.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")     

            else:
              client.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")

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
    parser.add_argument("--directory", required=False, default=".", help="Directory to serve files from")
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
