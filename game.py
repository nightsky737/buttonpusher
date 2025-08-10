import pygame
import socket
import json

pygame.init()
screen = pygame.display.set_mode((400, 300))
SERVER_IP = '127.0.0.1'
SERVER_PORT = 65432
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))  #this is the surface everything is going to be on.
board_size = 4

board = []
clicked = [False for i in range(board_size * board_size)]
for r in range(board_size):
    for c in range(board_size):
        rect = pygame.draw.rect(screen, (20, 40, 5), 
                pygame.Rect(400/board_size * r, 400/board_size * c, 60, 60)) #x, y, width height
        board.append(rect)

import threading
import json
message = None

def listen_to_server(sock):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    global message

    buffer = ""
    while True:
        data = sock.recv(1024).decode()
        if not data:
            break
        buffer += data
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            message = line


# Then start it with:
listener_thread = threading.Thread(target=listen_to_server, args=(client_socket,), daemon=True)
listener_thread.start()


running = True
while running:
    for event in pygame.event.get():
        print(message)
        if message != None:
            #in format {"event_type": , "rect_num": , "clicked"}
            message = json.loads(message)
            print(type(message))
            if message["event_type"] == "rect":
                clicked[message["rect_num"]] = message["clicked"]
                print(clicked)
            message = None
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, rect in enumerate(board):
                if rect.collidepoint(pos):
                    message = json.dumps({'event_type': "rect", "rect_num": i, "clicked" : True})
                    client_socket.sendall(message.encode())

    screen.fill((30, 30, 30))
    for rect_num in range(len(board)):
        pygame.draw.rect(screen,  (0, 0, 0) if clicked[rect_num] else (0, 128, 255), board[rect_num])
    pygame.display.flip()

pygame.quit()
client_socket.close()
