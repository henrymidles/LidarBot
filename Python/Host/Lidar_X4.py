import time
import random
import struct
import serial

class Lidar_X4():
    def __init__(self, port='/dev/ttyUSB0'):
        self.lidar = None
        self.port = port
        self.baud = 128000

    def start(self):
        self.lidar = serial.Serial(self.port, self.baud)
    
    def stop(self):
        self.lidar.close()
        self.lidar = None

    def start_scan(self):
        send_msg(lidar_s, [0xA5, 0x60], 1)

    def send_msg(self, ser, msg):
        if self.lidar != None:
            self.lidar.write(bytearray(msg))

    def get_data_list(self):
        if self.lidar != None:
            return list(lidar_s.read(lidar_s.in_waiting))
        else:
            return None

    def get_data_bytes(self):
        if self.lidar != None:
            return lidar_s.read(lidar_s.in_waiting)
        else:
            return None

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

# From: https://github.com/YDLIDAR/YDLidar-SDK/blob/master/core/common/ydlidar_protocol.h
#define LIDAR_CMD_STOP                      0x65
#define LIDAR_CMD_SCAN                      0x60
#define LIDAR_CMD_FORCE_SCAN                0x61
#define LIDAR_CMD_RESET                     0x80
#define LIDAR_CMD_FORCE_STOP                0x00
#define LIDAR_CMD_GET_EAI                   0x55
#define LIDAR_CMD_GET_DEVICE_INFO           0x90
#define LIDAR_CMD_GET_DEVICE_HEALTH         0x92
#define LIDAR_ANS_TYPE_DEVINFO              0x4
#define LIDAR_ANS_TYPE_DEVHEALTH            0x6
#define LIDAR_CMD_SYNC_BYTE                 0xA5
#define LIDAR_CMDFLAG_HAS_PAYLOAD           0x80
#define LIDAR_ANS_SYNC_BYTE1                0xA5
#define LIDAR_ANS_SYNC_BYTE2                0x5A
#define LIDAR_ANS_TYPE_MEASUREMENT          0x81
#define LIDAR_RESP_MEASUREMENT_SYNCBIT        (0x1<<0)
#define LIDAR_RESP_MEASUREMENT_QUALITY_SHIFT  2
#define LIDAR_RESP_MEASUREMENT_CHECKBIT       (0x1<<0)
#define LIDAR_RESP_MEASUREMENT_ANGLE_SHIFT    1
#define LIDAR_RESP_MEASUREMENT_DISTANCE_SHIFT  2
#define LIDAR_RESP_MEASUREMENT_ANGLE_SAMPLE_SHIFT 8

#define LIDAR_CMD_RUN_POSITIVE             0x06
#define LIDAR_CMD_RUN_INVERSION            0x07
#define LIDAR_CMD_SET_AIMSPEED_ADDMIC      0x09
#define LIDAR_CMD_SET_AIMSPEED_DISMIC      0x0A
#define LIDAR_CMD_SET_AIMSPEED_ADD         0x0B
#define LIDAR_CMD_SET_AIMSPEED_DIS         0x0C
#define LIDAR_CMD_GET_AIMSPEED             0x0D

#define LIDAR_CMD_SET_SAMPLING_RATE        0xD0
#define LIDAR_CMD_GET_SAMPLING_RATE        0xD1
#define LIDAR_STATUS_OK                    0x0
#define LIDAR_STATUS_WARNING               0x1
#define LIDAR_STATUS_ERROR                 0x2

#define LIDAR_CMD_ENABLE_LOW_POWER         0x01
#define LIDAR_CMD_DISABLE_LOW_POWER        0x02
#define LIDAR_CMD_STATE_MODEL_MOTOR        0x05
#define LIDAR_CMD_ENABLE_CONST_FREQ        0x0E
#define LIDAR_CMD_DISABLE_CONST_FREQ       0x0F

#define LIDAR_CMD_GET_OFFSET_ANGLE          0x93
#define LIDAR_CMD_SAVE_SET_EXPOSURE         0x94
#define LIDAR_CMD_SET_LOW_EXPOSURE          0x95
#define LIDAR_CMD_ADD_EXPOSURE       	    0x96
#define LIDAR_CMD_DIS_EXPOSURE       	    0x97

#define LIDAR_CMD_SET_HEART_BEAT            0xD9