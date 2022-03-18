import math
from queue import Queue

""" This thread gets data from the socket, parses it, and sends it to the queue to be displayed """
class RasPi_coms():
    def __init__(self, s):
        self.running = True
        self.state = "start"
        self.buff = []
        self.mysocket = s
        self.queue = Queue(1000)
        self.status = {"left":0, "right":0, "bat":0}

    """This loop runs continiously getting data from teh socket and parsing it """
    def run(self):
        while self.running:
            try:
                data = self.mysocket.recv(8192).decode('UTF-8')
                self.parse_data(data)
            except ConnectionResetError as e:
                print("Connection Closed, stopping thread")
                break
            
    """ Parse the data into frames, 1 frame contains the data from 1 revoluion of the lidar """
    def parse_data(self, data):
        startpos = 0
        while True:
            if self.state == 'start':
                startpos = data.find('L', startpos)
                if startpos == -1: # no start byte, end
                    return
                self.state = "end" # found start byte, continue looking for end
            else:
                endpos = data.find('X', startpos)
                if endpos == -1: # no end byte in this frame
                    self.buff += list(data[startpos:]) # buffer remaining bytes
                    return
                else:
                    # found end byte, buffer from start byte to end byte
                    # Start byte could be 0 if the frame started normally, but
                    # could be some other number of the frame came in pieces
                    self.buff += list(data[startpos:endpos])
                    self.queue_buffer()
                    startpos = endpos + 1
                    # Continueing searching the rest of the frame
                    self.state = 'start'

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








