#!/usr/bin/env python3

import socket
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for i in range(10):
        msg = f"{time.time()}"
        s.sendall(bytes(msg, 'UTF-8'))
        data = s.recv(1024)
        print(f'Received: {time.time()}', repr(data))
        time.sleep(1)