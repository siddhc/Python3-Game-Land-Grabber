import pygame
import random
import math
from game_constants import *

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def xy(self):
        return (self.x, self.y)


class Wall:
    def __init__(self, name):
        self.name = name
        s = self.name.split('_')
        self.x1 = int(s[1])
        self.y1 = int(s[2])
        self.x2 = int(s[3])
        self.y2 = int(s[4])
        self.owner = None
        self.width = 1
        self.color = g_color_LIGHT_GREY
        self.center = Point(int((self.x1+self.x2)/2), int((self.y1+self.y2)/2))

    def draw(self, screen, mode="game_running"):
        if not self.owner:
            if mode=="tracing":
                color = g_color_BLACK
            else:
                color = self.color
        else:
            color = self.color
        pygame.draw.line(screen, color, (self.x1, self.y1), (self.x2, self.y2), self.width)

    def distance(self, p):
        return math.sqrt(math.pow(self.center.x - p.x, 2) + math.pow(self.center.y - p.y, 2))

class Player:
    def __init__(self, name, color):
        self.name = name
        self.ip_address = None
        self.color = color
        self.wall_width = 5
        self.number_of_walls = 0
        self.number_of_houses = 0