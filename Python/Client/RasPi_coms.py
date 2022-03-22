import math
import time
from queue import Queue

HOST = 'raspberrypi'    # The server's hostname or IP address
PORT = 65432            # The port used by the server

""" This thread gets data from the socket, parses it, and sends it to the queue to be displayed """
class RasPi_coms():
    def __init__(self, s):
        self.running = True
        self.state = 0 #"start"
        self.frameBuff = []
        self.mysocket = s
        self.queue = Queue(5000)
        self.status = {"left":0, "right":0, "bat":0}
        self.lastrxtime = time.time()
        self.f_idxs = []
        self.ii = 0
        self.ff_idx = 0
        self.data = []

    """This loop runs continiously getting data from teh socket and parsing it """
    def run(self):
        while self.running:
            try:
                data = self.mysocket.recv(8192)
                self.parse_data(list(data))
                time.sleep(0.1)
            except ConnectionResetError as e:
                print("Connection Closed, stopping thread")
                break

    def sync_run(self):
        #while True:
        #print(self.state)
        if self.state == 0:
            self.data = list(self.mysocket.recv(8192))
            self.f_idxs = [i for i,x in enumerate(self.data) if (x==170 and self.safe_check(self.data, i+1, 85))]
            self.state = 1

        if self.state == 1:
        
            #for i, f_idx in enumerate(self.f_idxs):
            while self.ii < len(self.f_idxs):
                f_idx = self.f_idxs[self.ii]
                if f_idx+2 < len(self.data):
                    if self.data[f_idx+2] == 1:

                        self.ii += 1
                        return self.analyse_frames()

                if self.ii +1 < len(self.f_idxs):
                    endIdx = self.f_idxs[self.ii +1]
                    self.frameBuff.append(self.data[f_idx:endIdx])
                else:
                    self.frameBuff.append(self.data[f_idx:])
                self.ii += 1
            self.state = 0
            self.ii = 0
        
        return None
    
    def safe_check(self, data, idx, val):
        if idx >= len(data):
            return False
        else:
            return (data[idx] == val)
    
    """ Parse the data into frames, 1 frame contains the data from 1 revoluion of the lidar """
    def parse_data(self, data):
        f_idxs = [i for i,x in enumerate(data) if (x==170 and self.safe_check(data, i+1, 85))]
        for i, f_idx in enumerate(f_idxs):
            if data[f_idx+2] == 1:
                #print(time.time() - self.lastrxtime)
                #self.lastrxtime = time.time()
                self.analyse_frames()

            if i+1 < len(f_idxs):
                endIdx = f_idxs[i+1]
                self.frameBuff.append(data[f_idx:endIdx])
            else:
                self.frameBuff.append(data[f_idx:])

    def analyse_frames(self):

        def correct_angle(angle, dist):
            if dist != 0:
                val = (155.3 - dist) / (155.3 * dist)
                angle_correction = math.atan(21.8 * val)
                correction = math.degrees(angle_correction)
            return correction
        
        def to_xy(angle, dist):
            x = (dist/10)*math.cos(math.radians(angle))
            y = (dist/10)*math.sin(math.radians(angle))
            return [x,y] #[angle,dist]
        
        def range_valid(range):
            if range > 20 and range < 8000:
                return True
            else:
                return False

        pt_cloud = []
        for packet in self.frameBuff:
            distances = list()
            #PH  = (packet[1] << 8) | packet[0] # Packet Header
            #CT  = packet[2] # Pcket Type
            LSN = packet[3] # Sample Count
            if LSN == 1:
                continue
            FSA = (packet[5] << 8) | packet[4] # Start Angle
            LSA = (packet[7] << 8) | packet[6] # End Angle
            #CS  = (packet[9] << 8) | packet[8] # Check Code

            a_start = (FSA >> 1)/64
            a_end   = (LSA >> 1)/64
            a_diff  = a_end - a_start
            if a_diff < 0: 
                a_diff += 360
            incriment = a_diff / (LSN-1)

            #for i = 0; i < 2 * LSN; i = i + 2) 
            i = 0
            while i < 2*LSN:
                i_MSB = 10 + i + 1
                if i_MSB < len(packet):
                    dist = packet[i_MSB] << 8 | packet[i_MSB-1]
                else:
                    dist = 0
                #check_code ^= data
                distances.append(dist / 4)
                i += 2

            # Intermediate Points
            for i in range(0, LSN):
                i_angle = (incriment * i) + a_start

                if range_valid(distances[i]):
                    i_correction = correct_angle(i_angle, distances[i])
                    pt_cloud.append(to_xy(i_angle + i_correction, distances[i]))
        self.frameBuff = []
        return pt_cloud
        

    """ This function sorts all of the data and turns it into points. These points are then queued for display """
    def queue_buffer(self):
        while True:
            try:
                i = self.buff.index(';') #find_next(buff, ';') # find the point deliminator
            except ValueError:
                break
            if i == 0: # if it is at the beginning, remove it
                del self.buff[0]
                continue
            word = ''.join(self.buff[:i])
            
            if 'S' in word: # Status word
                l, r, b = word.split(',')
                self.status['left']  = int(l)
                self.status['right'] = int(r)
                self.status['bat']   = int(b)
                print(self.status)
                for d in range(0,i): # remove it from the buffer
                    del self.buff[0]
                continue

            try:
                #a, r = ''.join(self.buff[:i]).split(',') # grab a section containing a point
                a, r = word.split(',')

                a = float(a)-1.57 # angle in radians
                r = float(r) # distance in cm
                for d in range(0,i): # remove it from the buffer
                    del self.buff[0]
            except ValueError: # Failed conversion, probably a partial point
                for d in range(0,i): # remove it from the frame
                    del self.buff[0]
                continue
            # Convert from polar to cartesian and load into queue
            # if r < 40:
            #     print(a+1.57)
            x = -r*math.cos(a)
            y =  r*math.sin(a)
            self.queue.put([x, y])


if __name__ == "__main__":
    import socket

    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.connect((HOST, PORT))

    try:
        Raspi = RasPi_coms(mysocket)
        while True:
            newPoints = Raspi.sync_run()
            if newPoints != None:
                scan_points = newPoints
                for p in scan_points:
                    print(p)
                print("\n\n\n")
                
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        Raspi.running = False
        mysocket.close()


    # try:
    #     print("Starting")
    #     Bot.main()
    # except KeyboardInterrupt:
    #     Bot.stop()