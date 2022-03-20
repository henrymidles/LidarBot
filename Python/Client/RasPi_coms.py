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
                if self.data[f_idx+2] == 1:
                    #print(time.time() - self.lastrxtime)
                    #self.lastrxtime = time.time()
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
        if idx > len(data):
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

                # if frameStart != None:
                #     self.state = "end"
                # if frameStart != 0:
                #     frameBuff += data[:frameStart]
                #     self.analyse_data(frameBuff)

                    #print(f"{idx} , {idx2} , {idx3}")

        # startpos = 0
        # while True:
        #     if self.state == 'start':
        #         startpos = data.find('L', startpos)
        #         if startpos == -1: # no start byte, end
        #             return
        #         self.state = "end" # found start byte, continue looking for end
        #     else:
        #         endpos = data.find('X', startpos)
        #         if endpos == -1: # no end byte in this frame
        #             self.buff += list(data[startpos:]) # buffer remaining bytes
        #             return
        #         else:
        #             # found end byte, buffer from start byte to end byte
        #             # Start byte could be 0 if the frame started normally, but
        #             # could be some other number of the frame came in pieces
        #             self.buff += list(data[startpos:endpos])
        #             self.queue_buffer()
        #             startpos = endpos + 1
        #             # Continueing searching the rest of the frame
        #             self.state = 'start'

    def analyse_frames(self):
        pt_cloud = []
        for packet in self.frameBuff:
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

            # First Point
            i_angle = a_start
            i_dist  = (packet[11] << 8) | packet[10]
            i_dist  = i_dist /4  # Convert to mm
            if i_dist != 0:
                val = (155.3 - i_dist) / (155.3 * i_dist)
                angle_correction = math.atan(21.8 * val)
                i_angle += math.degrees(angle_correction)
            if i_dist > 20:
                x = -(i_dist/10)*math.cos(math.radians(i_angle))
                y =  (i_dist/10)*math.sin(math.radians(i_angle))
                pt_cloud.append([x, y])
                #self.queue.put([x, y])

            # Intermediate Points
            for i in range(2, LSN-1):
                d_idx = 10+(2*i)
                if d_idx > len(packet)-1:
                    continue
                i_angle = (incriment * i-1) + a_start
                i_dist  = (packet[d_idx] << 8) | packet[d_idx-1]
                i_dist  = i_dist /4  # Convert to mm
                
                if i_dist != 0:
                    val = (155.3 - i_dist) / (155.3 * i_dist)
                    angle_correction = math.atan(21.8 * val)
                    i_angle += math.degrees(angle_correction)
                else:
                    continue
                if i_dist > 20:
                    x = -(i_dist/10)*math.cos(math.radians(i_angle))
                    y =  (i_dist/10)*math.sin(math.radians(i_angle))
                    pt_cloud.append([x, y])
                    #self.queue.put([x, y])

            # Last point
            i_angle = a_end
            i_dist  = (packet[-1] << 8) | packet[-2]
            i_dist  = i_dist /4  # Convert to mm
            if i_dist != 0:
                val = (155.3 - i_dist) / (155.3 * i_dist)
                angle_correction = math.atan(21.8 * val)
                i_angle += math.degrees(angle_correction)
            if i_dist > 20:
                x = -(i_dist/500)*math.cos(math.radians(i_angle))
                y =  (i_dist/500)*math.sin(math.radians(i_angle))
                pt_cloud.append([x, y])
                #self.queue.put([x, y])
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
                print("NEW!")
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        Raspi.running = False
        mysocket.close()


    # try:
    #     print("Starting")
    #     Bot.main()
    # except KeyboardInterrupt:
    #     Bot.stop()