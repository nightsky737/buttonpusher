import socket
import json
import threading
HOST = '127.0.0.1'
PORT = 65432

def broadcast(message_dict):
    message = (json.dumps(message_dict) + '\n').encode()
    for client_conn in clients[:]:
        try:
            client_conn.sendall(message)
        except Exception as e:
            print("Failed to send to a client:", e)
            clients.remove(client_conn)


clients = []

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(clients)
            message = json.loads(data.decode())
            print(f"Received from client: {message}")
            broadcast(message)
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        client_thread.start()
        print(clients)
        

if __name__ == "__main__":
    main()

