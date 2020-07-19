import pygame
import random
import math
from game_constants import *
import socket
import threading
import pickle

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
            if mode == "tracing":
                color = g_color_BLACK
            else:
                color = self.color
        else:
            color = self.color
        pygame.draw.line(screen, color, (self.x1, self.y1), (self.x2, self.y2), self.width)

    def distance(self, p):
        return math.sqrt(math.pow(self.center.x - p.x, 2) + math.pow(self.center.y - p.y, 2))


class Player:
    def __init__(self, name):
        self.name = name
        self.ip_address = None
        self.color = g_color_BLACK
        self.wall_width = 5
        self.number_of_walls = 0
        self.number_of_houses = 0
        self.id = None
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector.connect((HOST_SERVER, PORT_SERVER))
        self.number = None
        self.type = None  # "host" or "join"

    def network_receive(self, size=1024):
        '''
        Receives message_object from network.
        :param socket_object: Socket that receives the data_object.
        :param size: Size of message_object. Defaults to 1024 bytes.
        :return: message_object that is obtained after loading the received pickle from the network.
        '''
        try:
            message_object = pickle.loads(self.connector.recv(size))
        except EOFError as e:
            print("EOFError. Program will continue.")
            return b''
        return message_object

    def network_send(self, message_object):
        '''
        Sends message_object to the network.
        :param socket_object: Socket object through message_object is sent.
        :param message_object: The object that is pickled and sent to the network.
        :return: None
        '''
        self.connector.sendall(pickle.dumps(message_object))

