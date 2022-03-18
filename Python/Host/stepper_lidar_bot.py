
from glob import glob
from tracemalloc import start
import ydlidar
import serial
import serial.tools.list_ports    
import time
import socket
import threading
from queue import Queue
import math

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

def thread_encode_data():
    global running
    global moving
    while running:
        points_b = b'L'
        if not scan_data_q.empty():
            startTime = time.time()
            scanPoints = scan_data_q.get()

            for p in scanPoints:
                pass
                #print(p)
            #object_methods = [method_name for method_name in dir(scanPoints)]
    
            #print(object_methods)

            #points_b = bytearray(str(scanPoints[:]), 'utf-8')
            #print(points_b)
            # for p in scanPoints:
            #     print(p)
                #points_b += bytearray(f';{p.angle},{p.range}', 'UTF-8')
            #    points_b += f';{point.angle},{point.range}'.encode('UTF-8')
            #     if point.range > 0.01:
            #         a = round(point.angle, 5)
            #         r = round(point.range*100, 2)
            #         points_b += f';{a},{r}'.encode('UTF-8')
            #         if moving and r < 40 and abs(a) > 2.35:
            #             curx = r * math.sin(a)
            #             cury = r * math.cos(a)
            #             if abs(curx) < 16 and cury < 40:
            #                 micro.write('STP0\n'.encode('UTF-8'))
            #                 print(f"Stopped: {a*57.3} rad, {r} cm, {curx}, {cury}")
            #                 moving = False
            points_b += b'X'
            print(f"{round(time.time() - startTime, 3)}")

def get_lidar(laser, micro):
    global moving
    
    ret = laser.doProcessSimple(scan)
    
    if not ret:
        print("Failed to get Lidar Data")
        return

    scan_data_q.put(scan.points)
    time.sleep(1)
        #points_b += f';{point.angle},{point.range}'.encode('UTF-8')
    #     if point.range > 0.01:
    #         a = round(point.angle, 5)
    #         r = round(point.range*100, 2)
    #         points_b += f';{a},{r}'.encode('UTF-8')
    #         if moving and r < 40 and abs(a) > 2.35:
    #             curx = r * math.sin(a)
    #             cury = r * math.cos(a)
    #             if abs(curx) < 16 and cury < 40:
    #                 micro.write('STP0\n'.encode('UTF-8'))
    #                 print(f"Stopped: {a*57.3} rad, {r} cm, {curx}, {cury}")
    #                 moving = False
    # points_b += b'X'
    #return points_b

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

    # Setup lidar
    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = "/dev/ydlidar"
    for key, value in ports.items():
        port = value
    print(f"Port Found: {port}")
    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 128000)
    laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    laser.setlidaropt(ydlidar.LidarPropScanFrequency,  10.0)
    laser.setlidaropt(ydlidar.LidarPropSampleRate, 9)
    laser.setlidaropt(ydlidar.LidarPropSingleChannel, False)
    scan = ydlidar.LaserScan()

    # Check lidar is working
    init = laser.initialize()
    if not init:
        print("Error connecting to device")
        exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, PORT))
        s.listen()
        print("Server Started.")
        print("Press CTRL+C to exit.\n")

        #micro_thread = threading.Thread(target=thread_micro, args=(micro,))
        #micro_thread.start()

        while True:
            try:
                # print("Waiting for connection...")
                # newConnection, addr = s.accept()
                # with newConnection:
                #     print(f'{addr} Connected!')
                #     running = True

                #     rcv_thread = threading.Thread(target=thread_get_client_msg, args=(newConnection, micro,))
                #     rcv_thread.start()

                encode_thread = threading.Thread(target=thread_encode_data, args=())
                encode_thread.start()
                    
                laserOn = laser.turnOn()
                # while running:
                t = time.time()+10 # start time
                while time.time() < t:
                    #startTime = time.time()
                    get_lidar(laser, micro)# Get lidar data
                    #print(time.time() - startTime)

                    #newConnection.sendall(points)# Pipe it over to the client
                    
            except (ConnectionResetError, BrokenPipeError) as e:
                running = False
                rcv_thread.join()
                # needed if we break while sending data
                print("\nConnection Reset by Peer\n")
                laser.turnOff()

    except KeyboardInterrupt:
        micro_running = False
        running = False
        micro_thread.join()
        time.sleep(0.5)
        micro.close()
        time.sleep(0.5)
        print('Turning off lidar...')
        laser.turnOff()
        time.sleep(0.5)
        laser.disconnecting()
        time.sleep(0.5)
        print('Closing server...')
        s.shutdown(0)
        s.close()


        
