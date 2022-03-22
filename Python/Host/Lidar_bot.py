import serial
import serial.tools.list_ports    
import time
import socket
import threading
from queue import Queue
import math
import easy_lidar

HOST = ''
PORT = 65432 
running = True
micro_running = True
moving = False

shortest_d = 5000
shortest_a = 0
MaxDiff = 5
turn_p = 1.5
spd_p = 1
spd = 0
rx_msg = ""
micro_tx_queue = Queue()
micro_rx_queue = Queue()
scan_data_q = Queue(10)

# Send message to microcontroller
# def send_message(ser, msg):
#     ser.write(msg.encode('ascii'))

# def wait_for_response(ser):
#     rx_data = ""
#     i = 0
#     while(i < 10):
#         if ser.in_waiting > 0:
#             rx_data += ser.read(ser.in_waiting).decode('utf-8')
#             if '\n' in rx_data:
#                 return rx_data
#         i = 30
#         time.sleep(0.01)
#         i += 1
#     print("No Response")
#     return ""

# def check_messages(ser):
#     global rx_msg
#     if ser.in_waiting > 0:
#         rx_msg += ser.read(ser.in_waiting).decode('utf-8')
#         if '\n' in rx_msg:
#             ret = rx_msg
#             rx_msg = ""
#             return ret
#     return None


def thread_get_client_msg(client, micro):
    global moving
    while running:
        try:
            data = client.recv(1024).decode('UTF-8')
            splitmsgs = data.split('\n')
            for msg in splitmsgs:
                if 'Done' in msg:
                    moving = False
                if len(msg) <= 3:
                    continue
                msg += '\n'
                micro_tx_queue.put(msg)
                #micro.write(msg.encode('UTF-8'))
        except ConnectionResetError as e:
            return

def thread_micro(micro):
    global moving
    global micro_running
    rx_buff = ""
    while micro_running:
        if not micro_tx_queue.empty():
            msg = micro_tx_queue.get()
            moving = True
            micro.write(msg.encode('UTF-8'))
        if micro.in_waiting > 0:
            rx_buff += micro.read().decode('UTF-8')
            if rx_buff[-1] == '\n':
                micro_rx_queue.put(rx_buff)
                rx_buff = ""
        time.sleep(0.05)
    print('Stopping Microcontroller...')
    micro.write('STP0\n'.encode('UTF-8'))

if __name__ == "__main__":
    micro = serial.Serial('/dev/ttyACM0', 250000, timeout=1)
    lidar = easy_lidar.Lidar('/dev/ttyUSB0')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, PORT))
        s.listen()
        print("Server Started.")
        print("Press CTRL+C to exit.\n")

        micro_thread = threading.Thread(target=thread_micro, args=(micro,))
        micro_thread.start()

        while True:
            try:
                print("Waiting for connection...")
                newConnection, addr = s.accept()
                with newConnection:
                    print(f'{addr} Connected!')
                    running = True

                    rcv_thread = threading.Thread(target=thread_get_client_msg, args=(newConnection, micro,))
                    rcv_thread.start()
                        
                    lidar.start()
                    lidar.start_scan()

                    while True:
                        # Pipe data over to the client
                        newConnection.sendall(lidar.get_data_bytes())
                    
            except (ConnectionResetError, BrokenPipeError) as e:
                running = False
                rcv_thread.join()
                # needed if we break while sending data
                print("\nConnection Reset by Peer\n")
                lidar.stop()

    except KeyboardInterrupt:
        micro_running = False
        running = False
        micro_thread.join()
        time.sleep(0.5)
        micro.close()
        time.sleep(0.5)
        print('Turning off lidar...')
        lidar.stop()
        time.sleep(0.5)
        print('Closing server...')
        s.shutdown(0)
        s.close()
