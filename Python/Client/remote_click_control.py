#!/usr/bin/env python3

import socket
import time
import math
import threading
import numpy as np
from util import point_direction, point_distance
from queue import Queue
#from PythonRobotics.SLAM.ICP.iterative_closest_point import icp_matching
from RasPi_coms import RasPi_coms
from Turtle_UI import UI
import sys

HOST = 'raspberrypi'    # The server's hostname or IP address
PORT = 65432            # The port used by the server

""" """
class LidarBot():
    def __init__(self):
        self.button_queue = Queue(32)
        self.running = True
        self.moving = False
        self.path_points = [[0,0], [0,0]]
        self.scan_points = [] #np.zeros(shape=(2,500))
        self.travel_points = [[0,0]]
        self.bot_actions = Queue()
        self.last_scan_points = np.zeros(shape=(2,500))

        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mysocket.connect((HOST, PORT))

        #self.exe_thread = threading.Thread(target=self.thread_execute_actions, args=())
        #self.exe_thread.start()

        self.t_ui = UI(self.get_click_point)

        self.Raspi = RasPi_coms(self.mysocket)
        #self.lidar_thread = threading.Thread(target=self.Raspi.run, args=())



    """ Runs when the screen is clicked, adds click position to a queue """
    def get_click_point(self, x, y):
        # check if click is in a button
        for key in self.t_ui.buttons:
            if point_distance(self.t_ui.buttons[key]['pos'], [x,y]) < self.t_ui.buttons[key]['size']:
                self.button_queue.put(key)
                return
        # otherwise add it to path
        self.path_points[1] = [x,y]

    """ Run the ICP algorithm to calculate new position, this doesn't work quite right, yet """
    def ICP_tracking(self, curpos):
        newsize = self.scan_points.shape[1]
        lastsize = self.last_scan_points.shape[1]
        if newsize > lastsize:
            pass
            #rot, trans = icp_matching(self.last_scan_points, self.scan_points[:lastsize, :lastsize])
        elif newsize < lastsize:
            pass
            #rot, trans = icp_matching(self.last_scan_points[:newsize, :newsize], self.scan_points)
        else:
            pass
            #rot, trans = icp_matching(self.last_scan_points, self.scan_points)
        #print(time.time() - startTime)
        if startPos == True:
            curpos[0] += trans[0]
            curpos[1] += trans[1]
            self.travel_points.append([curpos[0], curpos[1]])
        else:
            curpos[0] = trans[0]
            curpos[1] = trans[1]
            startPos = True
        #print(f"{pos[0]} , {pos[1]}")
        return curpos

    """ Check for new lidar data, this data is put in a queue """
    def check_lidar_queue(self):
        if not self.Raspi.queue.empty():
            self.scan_points.clear()
            while not self.Raspi.queue.empty():
                self.scan_points.append(self.Raspi.queue.get())

            # self.last_scan_points = self.scan_points.copy()
            # self.scan_points = np.zeros(shape=(2, self.Lidar.queue.qsize()))
            # idx = 0
            # while not self.Lidar.queue.empty():
            #     p = self.Lidar.queue.get()
            #     self.scan_points[0][idx] = p[0]
            #     self.scan_points[1][idx] = p[1]
            #     idx += 1

    """ """
    def thread_execute_actions(self):
        while self.running:
            if not self.bot_actions.empty():
                self.moving = True
                act = self.bot_actions.get()

                # First, turn to correct direction
                self.mysocket.sendall(bytes(act['turn_msg'], 'UTF-8'))
                timer = round(act['turn_time'], 1)
                percentLeft = 1.0
                while timer >= 0:
                    print(f"{round(timer, 1)}", end='\r')

                    curDir = percentLeft * act['turn']
                    curx   = act['dist'] * math.sin(math.radians(curDir))
                    cury   = act['dist'] * math.cos(math.radians(curDir))
                    self.path_points[1] = [curx, cury]
                    time.sleep(0.1)
                    timer -= 0.1
                    percentLeft = timer / act['turn_time']

                time.sleep(0.5)

                # Then, move correct distance
                self.mysocket.sendall(bytes(act['dist_msg'], 'UTF-8'))
                timer = round(act['dist_time'], 1)
                percentLeft = 1.0
                while timer >= 0:
                    print(f"{round(timer, 1)}", end='\r')

                    curDist = percentLeft * act['dist']
                    self.path_points[1] = [0, curDist]

                    time.sleep(0.1)
                    timer -= 0.1
                    percentLeft = timer / act['dist_time']

                print("")
                self.moving = False
                self.mysocket.sendall(bytes('Done\n', 'UTF-8'))

            #time.sleep(0.5)

    """ """
    def estimate_action_time(self, distance=None, heading=None):
        if distance != None:
            steps = abs(distance) * 97 # 97 steps / cm
        elif heading != None:
            steps = abs(heading) *17 # 17 steps / degree
        else:
            return 0
        if steps > 3570:
            acceltime = 1.43
            constVtime = (steps - 3570) / 5000
        else:
            acceltime = math.sqrt(steps/7000)
            constVtime = 0.2 # The math is a little off for short movements, so add a buffer
        return acceltime + constVtime
        
    
    """ Check what buttons were pressed, and executes the appropriate function"""
    def check_button_queue(self):
        while not self.button_queue.empty():
            key = self.button_queue.get()
            if key == 'Go' and self.moving == False:
                dist = round(point_distance(self.path_points[0], self.path_points[1]))
                dir  = round(math.degrees(point_direction(self.path_points[1]))) - 90
                print(f"X: {self.path_points[1][0]} , Y: {self.path_points[1][1]} , Distance: {round(dist, 1)} , Direction: {round(dir, 1)}")
                if dir > 180:
                    dir -= 360
                dir = -dir
                
                action = {
                    "turn": dir,
                    "dist": dist,
                    "turn_msg": f"TRN {dir}\n",
                    "dist_msg": f"MOV {dist}\n",
                    "turn_time": self.estimate_action_time(heading=dir),
                    "dist_time": self.estimate_action_time(distance=dist)
                }
                self.bot_actions.put(action)

            elif key == 'Stop':
                print("STOP")
                msg = f"STP0\n"
                self.mysocket.sendall(bytes(msg, 'UTF-8'))

    """ Main loop, run continiously """
    def main(self):
        #self.lidar_thread.start()
        lastDataTime = 0
        while self.running:
            
            #self.check_lidar_queue()
            
            newPoints = self.Raspi.sync_run()
            if newPoints != None:
                self.scan_points = newPoints
                print(f"{round(time.time() - lastDataTime, 2)}", end='\r')
                lastDataTime = time.time()
            #self.check_button_queue()

            self.t_ui.clear()
            self.t_ui.draw_bot()
            self.t_ui.draw_buttons()
            if self.moving == False: self.t_ui.draw_basic_points(self.path_points, color='red')
            else:                    self.t_ui.draw_basic_points(self.path_points, color='green')


            self.t_ui.draw_basic_points(self.scan_points, color='black')
            self.t_ui.update()
            


    """" Stop the program """
    def stop(self):
        self.running = False
        self.Raspi.running = False
        #self.lidar_thread.join()
        print("Closing")
        time.sleep(1)
        self.mysocket.shutdown(0)
        time.sleep(1)
        self.mysocket.close()

if __name__ == "__main__":

    Bot = LidarBot()

    try:
        print("Starting")
        Bot.main()
    except KeyboardInterrupt:
        Bot.stop()





            # con.update()
            # msg = "[,"
            # for a in range(len(con.axis)):
            #     msg += f"{round(con.axis[a]*255)},"
            # msg += ']'
            # s.sendall(bytes(msg, 'UTF-8'))

            # data = s.recv(8192).decode('UTF-8')
            # if data[0] != 'L':
            #     print("No Start Byte")
            #     #print(data)
            #     continue
            # points = data.split(';')
            # del points[0] # first item contains start byte, so remove it
            # turtle.penup()
            # turtle.clear()
            # wn.tracer(0) # This turns off screen updates 
            # turtle.color('red')

            # for idx, point in enumerate(path):
            #     turtle.setpos(point)
            #     turtle.pendown()
            #     turtle.dot()
            
            # turtle.penup()
            # turtle.color('black')
            # startTime = time.time()
            # try:
            #     for idx, point in enumerate(points):
            #         a, r = point.split(',')
            #         a = float(a)/57.3
            #         r = float(r)
            #         x = -r*math.cos(a)
            #         y = r*math.sin(a)
            #         turtle.setpos(x,y)
            #         turtle.pendown()
            #         turtle.dot()
            # except ValueError as e:
            #     print(f"Error at :{idx}/{len(points)}, {point}", )
            # wn.update()
            # print(f"\r{time.time() - startTime}", end='')