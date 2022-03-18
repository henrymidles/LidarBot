import time
import random
import struct
import serial

def send_msg(ser, msg, delay):
    ser.write(bytearray(msg))
    time.sleep(delay/1000)

if __name__ == "__main__":
    lidar_s = serial.Serial('/dev/ttyUSB0', 128000)
    send_msg(lidar_s, [0xA5, 0x00], 5)
    send_msg(lidar_s, [0xA5, 0x65], 5)
    send_msg(lidar_s, [0xA5, 0x00], 5)
    send_msg(lidar_s, [0xA5, 0x65], 5)

    send_msg(lidar_s, [0xA5, 0x92], 5)

    timer = time.time() + 0.1
    while time.time() < timer:
        if lidar_s.in_waiting > 0:
            print(lidar_s.read())

    send_msg(lidar_s, [0xA5, 0x90], 5)

    timer = time.time() + 0.1
    while time.time() < timer:
        if lidar_s.in_waiting > 0:
            print(lidar_s.read())

    send_msg(lidar_s, [0xA5, 0x60], 1)
    timer = time.time() + 10
    last_rx_time = time.time()
    buff = b''
    while time.time() < timer:
        if lidar_s.in_waiting > 0:
            newbs = list(lidar_s.read(lidar_s.in_waiting))
            #print(newbs)
            try:
                idx = newbs.index(170)
                idx2 = newbs.index(85)
                idx3 = newbs.index(1)
                if idx2 == idx+1 and idx3 == idx2+1:
                    rx_time = time.time()
                    print(rx_time - last_rx_time)
                    last_rx_time = rx_time                
                    #print(f"{idx} , {idx2} , {idx3}")
            except ValueError:
                pass

            # if newbs == b'\xaa':
            #     newb2 = lidar_s.read(1)
            #     if newb2 == b'\x55':
            #         if list(buff)[2] == 1:
            #             rx_time = time.time()
            #             print(rx_time - last_rx_time)
            #             last_rx_time = rx_time
                        
            #         #print(list(buff))
            #         buff = newb + newb2
            # else:
            #     buff += newb
                
    lidar_s.close()







# points = []
# for i in range(560):
#     points.append([round(random.random(), 5), round(random.random(), 3)])

# points_b = bytearray('L', 'utf-8')

# startTime = time.time()
# points_b += 
# #points_b += bytearray(str(points), 'utf-8')
# #bytearray
# # for p in points:
    
# #     points_b += bytearray(f';{p[0]},{p[1]}', 'UTF-8')
#     #points_b += bytes(p[0], 'UTF-8')
#     #points_b += b','
#     #points_b += bytes(p[1], 'UTF-8')

# print(time.time() - startTime)
# print(points_b)


# def wait_for_response(ser):
#     rx_data = ""
#     i = 0
#     while(i < 20):
#         if ser.in_waiting > 0:
#             rx_data += ser.read(ser.in_waiting).decode('utf-8')
#             print(rx_data)
#             if '\n' in rx_data:
#                 return rx_data
#         time.sleep(0.001)
#         i += 1
#     print("No Response")
#     return ""

# def send_message(ser, msg):
#     ser.write(msg.encode('UTF-8'))


# micro = serial.Serial(f'/dev/ttyACM0', 250000, write_timeout=3, timeout=1)
# time.sleep(6)
# send_message(micro, "ID??\n")
# ret = wait_for_response(micro)
# print(ret)
# send_message(micro, "MOV20\n")
# ret = wait_for_response(micro)
# print(ret)
# time.sleep(2)
# send_message(micro, "TRN50\n")
# ret = wait_for_response(micro)
# print(ret)
# time.sleep(3)
# send_message(micro, "MOV-20\n")
# ret = wait_for_response(micro)
# print(ret)
# time.sleep(2)
# send_message(micro, "TRN-50\n")
# ret = wait_for_response(micro)
# print(ret)
# time.sleep(3)
