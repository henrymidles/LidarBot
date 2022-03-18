
import turtle
from util import point_distance

class UI():
    def __init__(self, click_func):
        self.buttons = {
            'Go':{
                'pos':  [400,-355],
                'size':  20,
                'color': 'green'
            }, 
            'Stop':{
                'pos':  [400,-400],
                'size':  20,
                'color': 'red'
            }
        }
        turtle.speed(0)
        turtle.tracer(0,0)
        turtle.delay(0)
        turtle.ht()
        self.wn = turtle.Screen()
        self.wn.setup(900, 900)
        turtle.onscreenclick(click_func)
    
    """ Draw the robot on the screen"""
    def draw_bot(self):
        turtle.penup()
        turtle.setpos(0,-15)
        turtle.color('blue')
        turtle.pendown()
        turtle.circle(15)
        turtle.penup()
        turtle.setpos(0, 0)
        turtle.pendown()
        turtle.setpos(0, 15)
        turtle.penup()

    """ Draw the buttons """
    def draw_buttons(self):
        for key in self.buttons:
            draw_x = self.buttons[key]['pos'][0]
            draw_y = self.buttons[key]['pos'][1] - (self.buttons[key]['size'])
            turtle.setpos(draw_x, draw_y)
            turtle.color(self.buttons[key]['color'])
            turtle.pendown()
            turtle.circle(self.buttons[key]['size'])
            turtle.penup()

    """ Draw points from numpy array in the format (2,x) """
    def draw_numpy_points(self, points, color='black'):
        turtle.penup()
        turtle.color(color)
        for p in range(points.shape[1]): #idx, point in enumerate(scan_points):
            turtle.setpos([points[0][p], points[1][p]])
            turtle.pendown()
            turtle.dot()
    
    """ Draw points from a standard python list in the format [[x1,y1],[x2,y2]...]"""
    def draw_basic_points(self, points, color='black', clustering=False):
        turtle.penup()
        turtle.color(color)
        last_p = [0,0]
        for p in points:
            if clustering:
                if point_distance(p, last_p) > 10:
                    turtle.penup()
                last_p = p
            turtle.setpos(p)
            turtle.pendown()
            turtle.dot()

    
    """ Update the screen """
    def update(self):
        self.wn.update()

    """ Clear the screen """
    def clear(self):
        turtle.clear()