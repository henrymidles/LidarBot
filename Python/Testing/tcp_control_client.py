#!/usr/bin/env python3

import socket
import time
import pygame
import turtle
import math

#pygame.init()

HOST = 'raspberrypi' #'192.168.50.243'  # The server's hostname or IP address
PORT = 65432            # The port used by the server

BLACK = pygame.Color("black")
WHITE = pygame.Color("white")

class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, BLACK)
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

class Controller():
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Joystick example")
        self.clock = pygame.time.Clock()
        self.tp = TextPrint()
        self.joysticks = {}
        self.done = False
        self.axis = [0,0,0,0,0,0]
        self.butt = [0,0,0,0,0,0,0,0,0,0]

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True 
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    joystick = self.joysticks[event.instance_id]
            if event.type == pygame.JOYDEVICEADDED: 
                joy = pygame.joystick.Joystick(event.device_index)
                self.joysticks[joy.get_instance_id()] = joy
                print("Joystick {} connencted".format(joy.get_instance_id()))

    def update(self):
        self.check_events()

        # Drawing step
        self.screen.fill(WHITE)
        self.tp.reset()
        self.tp.tprint(self.screen, "Number of joysticks: {}".format(len(self.joysticks)))
        self.tp.indent()

        for joystick in self.joysticks.values():
            jid = joystick.get_instance_id()
            self.tp.tprint(self.screen, "Joystick {}".format(jid))
            self.tp.indent()

            name = joystick.get_name()
            self.tp.tprint(self.screen, "Joystick name: {}".format(name))

            axes = joystick.get_numaxes()
            self.tp.tprint(self.screen, "Number of axes: {}".format(axes))
            self.tp.indent()

            for i in range(6):
                self.axis[i] = joystick.get_axis(i)
                self.tp.tprint(self.screen, "Axis {} value: {:>6.3f}".format(i, self.axis[i]))
            self.tp.unindent()

            buttons = joystick.get_numbuttons()
            self.tp.tprint(self.screen, "Number of buttons: {}".format(buttons))
            self.tp.indent()

            for i in range(10):
                self.butt[i] = joystick.get_button(i)
                self.tp.tprint(self.screen, "Button {:>2} value: {}".format(i, self.butt[i]))
            self.tp.unindent()

            hats = joystick.get_numhats()
            self.tp.tprint(self.screen, "Number of hats: {}".format(hats))
            self.tp.indent()

            # Hat position. All or nothing for direction, not a float like
            # get_axis(). Position is a tuple of int values (x, y).
            for i in range(hats):
                hat = joystick.get_hat(i)
                self.tp.tprint(self.screen, "Hat {} value: {}".format(i, str(hat)))
            self.tp.unindent()
            self.tp.unindent()

        pygame.display.flip()   # update the screen with what we've drawn.
        self.clock.tick(30)     # Limit to 30 frames per second.


def main():
    print("Starting")
    #con = Controller()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    turtle.speed(0)
    wn = turtle.Screen()
    turtle.penup()
    try:
        while True:
            # con.update()

            # msg = "[,"
            # for a in range(len(con.axis)):
            #     msg += f"{round(con.axis[a]*255)},"
            # msg += ']'
            # s.sendall(bytes(msg, 'UTF-8'))
            wn.tracer(0) # This turns off screen updates 
            data = s.recv(8192).decode('UTF-8')
            points = data.split('][')    
            points[0] = points[0].replace('[', '')
            points[-1] = points[0].replace(']', '')
            for p in points:
                x = p[1]*math.cos(p[0]/57.3)
                y = p[1]*math.sin(p[0]/57.3)
                turtle.setpos(x,y)
                turtle.pendown()
                turtle.dot()
            wn.update() 

            time.sleep(1)
    except KeyboardInterrupt:
        s.shutdown(0)
        s.close()

if __name__ == "__main__":
    main()