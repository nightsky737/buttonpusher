import pygame
import socket
import json
import time
from queue import Queue
message_queue = Queue()
pygame.font.init()
font = pygame.font.SysFont("Arial", 24)

pygame.init()
screen = pygame.display.set_mode((400, 300))
# SERVER_IP = '37.27.51.34' #http://37.27.51.34:65432/
SERVER_IP = '127.0.0.1' #http://37.27.51.34:65432/

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

def listen_to_server(sock):
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    buffer = ""
    while True:
        data = sock.recv(1024).decode()
        if not data:
            break
        buffer += data
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            message_queue.put(json.loads(line))



# Then start it with:
listener_thread = threading.Thread(target=listen_to_server, args=(client_socket,), daemon=True)
listener_thread.start()

holding_num = None
running = True
to_win = None
won = False

restart_button = pygame.draw.rect(screen, (100, 40, 105), 
        pygame.Rect(450, 200, 100, 60)) #x, y, width height

time_A = 0

while running:
    while not message_queue.empty():
        message = message_queue.get()
        #in format {"event_type": , "rect_num": , "clicked"}
        # message = json.loads(message)
        if message["event_type"] == "rect":
            clicked[message["rect_num"]] = message["clicked"]
            # print(clicked)
        elif message["event_type"] == "win":
            won = True
        elif message["event_type"] == "setup":
            to_win = message["need_press"]
            time_A = time.time()

        message = None
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, rect in enumerate(board):
                if rect.collidepoint(pos) and holding_num == None:
                    print(f"holding {i}")
                    holding_num = i
                    message = json.dumps({'event_type': "rect", "rect_num": i, "clicked" : True})
                    client_socket.sendall(message.encode())
            if restart_button.collidepoint(pos):
                message = json.dumps({'event_type': "restart"})
                client_socket.sendall(message.encode())

        elif event.type == pygame.MOUSEBUTTONUP:
            if holding_num != None:
                print("Released hold!")
                message = json.dumps({'event_type': "rect", "rect_num": holding_num, "clicked" : False})
                client_socket.sendall(message.encode())
                holding_num = None
                
    screen.fill((30, 30, 30))
    for rect_num in range(len(board)):
        pygame.draw.rect(screen,  (0, 0, 0) if clicked[rect_num] else (0, 128, 255), board[rect_num])
        text_surface = font.render(str(rect_num), True, (255, 255, 255))  # white text
        text_rect = text_surface.get_rect(center=board[rect_num].center)
        screen.blit(text_surface, text_rect)

    text_surface = font.render(str(to_win), True, (255, 255, 255))  # white text
    text_rect = text_surface.get_rect(center=(410, 50))
    screen.blit(text_surface, text_rect)
    
    pygame.draw.rect(screen, (100, 100, 105), restart_button)
    text_surface = font.render("Reset button", True, (255, 255, 255))  # white text
    text_rect = text_surface.get_rect(center=restart_button.center)
    screen.blit(text_surface, text_rect)

    time_left = max(0,15 - (time.time() - time_A))
    formatted_time = f"Time left {time_left:.1f}"
    text_surface = font.render(str(formatted_time), True, (255, 255, 255))  # white text
    text_rect = text_surface.get_rect(center=(410, 100))
    screen.blit(text_surface, text_rect)

    if time_left == 0 and not won:
        text_surface = font.render("You lose, times up!", True, (255, 255, 255))  # white text
        text_rect = text_surface.get_rect(center=(400, 100))
        screen.blit(text_surface, text_rect)
    if won:
        text_surface = font.render("You've won!", True, (255, 255, 255))  # white text
        text_rect = text_surface.get_rect(center=(410, 100))
        screen.blit(text_surface, text_rect)


    pygame.display.flip()

pygame.quit()
client_socket.close()
