import socket
import json
import threading
import random

HOST = '37.27.51.34'
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
clicked = [False for i in range(16)]
needs_clicked = []
for i in range(3):
    needs_clicked.append(random.randint(0, 15))
print(f"click {needs_clicked}")


def handle_client(conn, addr):
    print(f"New connection from {addr}")
    with conn:
        #sends the initial stuff
        initial_stuff ={"event_type" : "setup", "need_press" : needs_clicked}
        message = (json.dumps(initial_stuff) + '\n').encode()
        conn.sendall(message)
        
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                # print(clients)
                message = json.loads(data.decode())
                #in format {"event_type": , "rect_num": , "clicked"}

                if message["event_type"] == "rect":
                    clicked[message["rect_num"]] = message["clicked"]

                broadcast(message)
                #checks for win condition
                all_clicked = True
                for idx in needs_clicked:
                    if(not clicked[idx]):
                        all_clicked = False
                if all_clicked:
                    end ={"event_type" : "win"}
                    broadcast(end)
            except:
                conn.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        clients.append(conn)
        client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        client_thread.start()



if __name__ == "__main__":
    main()

