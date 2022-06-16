# A simple driver client for the car simulation

import json, pygame, socket, sys, threading

screen = pygame.display.set_mode((640, 480))
pygame.display.flip()

keys = {}
keys[pygame.K_w] = False
keys[pygame.K_a] = False
keys[pygame.K_s] = False
keys[pygame.K_d] = False

steeringAngle = 0
targetVelocity = 0

def connectionFunc():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8081)
    sock.connect(server_address)
    while True:
        data = json.loads(str(sock.recv(2048), 'ascii'))
        # print(data)

        if keys[pygame.K_w]:
            targetVelocity = 1
        elif keys[pygame.K_s]:
            targetVelocity = -1
        else:
            targetVelocity = 0

        if keys[pygame.K_a]:
            steeringAngle = 45
        elif keys[pygame.K_d]:
            steeringAngle = -45
        else:
            steeringAngle = 0

        message = {
            'steeringAngle': steeringAngle,
            'targetVelocity': targetVelocity
        }
        sock.sendall(bytes(json.dumps(message), 'ascii'))

connectionThread = threading.Thread(target=connectionFunc)
connectionThread.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            keys[event.key] = True
            print(keys)
        if event.type == pygame.KEYUP:
            keys[event.key] = False
            print(keys)
        if event.type == pygame.QUIT:
            running = False
