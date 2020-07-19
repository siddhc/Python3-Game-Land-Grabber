# Game functions

from game_constants import *
from game_variables import *
from game_classes import *
import threading
import pygame
import time
import numpy as np
import socket
import game_client
import game_server
import pickle

has_game_begun = False

received_message = None

def receiving_threaded(player, screen):
    global received_message
    global has_game_begun
    '''
    Receives messages from the server, anytime. This thread is useful when data from server is expected anytime.
    :param s: Socket object that connects to the server.
    :return: None
    '''
    with player.connector:
        while True:
            received_message = player.network_receive() # When has_game_begun == True, received message = (player_id, selected_wall)
            if not received_message:
                break
            if has_game_begun:
                g_make_player_wall(screen, received_message[1], received_message[0])

def g_initialize_parameters(screen, nc, nr):
    HOST_CLIENT = '127.0.0.1'  # The server's hostname or IP address
    PORT_CLIENT = 51232        # The port used by the server
    post_coordinates = g_get_post_coordinates(screen, nc, nr)
    wall_list = g_get_wall_list(screen, post_coordinates)
    g_draw_walls(screen, wall_list)
    # print(pygame.font.get_default_font())
    font1 = pygame.font.Font('freesansbold.ttf', 32)
    font2 = pygame.font.Font('freesansbold.ttf', 16)
    return post_coordinates, wall_list, (font1, font2)


def g_get_post_coordinates(screen, nc, nr):
    g_post_coordinates = np.zeros((nr, nc, 2), dtype=np.int)
    nc += 2
    nr += 2
    xs = np.linspace(0, g_WIDTH, nc)
    ys = np.linspace(0, g_HEIGHT, nr)
    xs, ys = np.meshgrid(xs.ravel(), ys.ravel())
    for i in range(1, nr - 1):
        for j in range(1, nc - 1):
            x, y = int(xs[i][j]), int(ys[i][j])
            g_post_coordinates[i-1][j-1][0] = x
            g_post_coordinates[i-1][j-1][1] = y
    return g_post_coordinates


def g_get_wall_list(screen, post_coordinates):
    g_wall_list = {}
    for c in range(0, post_coordinates.shape[1]-1):
        for r in range(0, post_coordinates.shape[0]):
            x1 = post_coordinates[r][c][0]
            y1 = post_coordinates[r][c][1]
            x2 = post_coordinates[r][c+1][0]
            y2 = post_coordinates[r][c+1][1]
            pygame.draw.line(screen, g_color_BLUE, (x1, y1), (x2, y2), 1)
            wall_keyname = 'w'+'_'+str(x1)+'_'+str(y1)+'_'+str(x2)+'_'+str(y2)
            if not wall_keyname in g_wall_list:
                g_wall_list.update({wall_keyname: Wall(wall_keyname)})
    for r in range(0, post_coordinates.shape[0]-1):
        for c in range(0, post_coordinates.shape[1]):
            x1 = post_coordinates[r][c][0]
            y1 = post_coordinates[r][c][1]
            x2 = post_coordinates[r+1][c][0]
            y2 = post_coordinates[r+1][c][1]
            pygame.draw.line(screen, g_color_GREEN, (x1, y1), (x2, y2), 1)
            wall_keyname = 'w'+'_'+str(x1)+'_'+str(y1)+'_'+str(x2)+'_'+str(y2)
            if not wall_keyname in g_wall_list:
                g_wall_list.update({wall_keyname: Wall(wall_keyname)})
    return g_wall_list


def g_draw_walls(screen, wall_list):
    for wall in wall_list:
        wall_list[wall].draw(screen, mode="game_running")


def g_draw_posts(screen, post_coordinates):
    '''
    Draws posts on the board. Initializes g_wall_coordinates with tuples (x, y) of posts
    :param screen: Screen on which posts are drawn
    :param nx: Number of posts in the x direction
    :param ny: Number of posts in the y direction
    :return: None
    '''
    nx = post_coordinates.shape[1] + 2
    ny = post_coordinates.shape[0] + 2
    xs = np.linspace(0, g_WIDTH, nx)
    ys = np.linspace(0, g_HEIGHT, ny)
    xs, ys = np.meshgrid(xs.ravel(), ys.ravel())
    for i in range(1, ny-1):
        for j in range(1, nx-1):
            x, y = int(xs[i][j]), int(ys[i][j])
            post_coordinates[i-1][j-1][0] = x
            post_coordinates[i-1][j-1][1] = y
            pygame.draw.circle(screen, g_color_BLACK, (x, y), g_post_radius, 1)


def g_show_wall_trace(screen, wall_list, mx, my):
    p = Point(mx, my)
    selected_wall = None
    min_distance = g_WIDTH
    for wall in wall_list:
        d = wall_list[wall].distance(p)
        if d < min_distance:
            min_distance = d
            selected_wall = wall_list[wall]
    selected_wall.draw(screen, mode="tracing")
    return selected_wall


def g_make_player_wall(screen, selected_wall, player):
    if not selected_wall.owner:
        selected_wall.owner = player
        selected_wall.color = player.color
        selected_wall.width = player.wall_width
        selected_wall.draw(screen)
        player.number_of_walls += 1
    else:
        print("Wall already owned: play 'ding' sound")


def g_show_text(screen, display_text, font, x, y, fore_color, back_color):
    text = font.render(display_text, True, fore_color, back_color)
    text_rect = text.get_rect()
    text_rect.center = (x, y)
    screen.blit(text, text_rect)


def g_count_houses(screen, post_coordinates, font1, wall_list, player):
    house_count = 0
    for r in range(post_coordinates.shape[0]-1):
        for c in range(post_coordinates.shape[1]-1):
            wall_l = wall_list['w'+'_'+str(post_coordinates[r][c][0])+'_'+str(post_coordinates[r][c][1])+'_'+str(post_coordinates[r+1][c][0])+'_'+str(post_coordinates[r+1][c][1])]
            wall_t = wall_list['w'+'_'+str(post_coordinates[r][c][0])+'_'+str(post_coordinates[r][c][1])+'_'+str(post_coordinates[r][c+1][0])+'_'+str(post_coordinates[r][c+1][1])]
            wall_r = wall_list['w'+'_'+str(post_coordinates[r][c+1][0])+'_'+str(post_coordinates[r][c+1][1])+'_'+str(post_coordinates[r+1][c+1][0])+'_'+str(post_coordinates[r+1][c+1][1])]
            wall_b = wall_list['w'+'_'+str(post_coordinates[r+1][c][0])+'_'+str(post_coordinates[r+1][c][1])+'_'+str(post_coordinates[r+1][c+1][0])+'_'+str(post_coordinates[r+1][c+1][1])]
            if wall_l.owner == wall_t.owner == wall_r.owner == wall_b.owner and wall_l.owner is not None:
                house_count += 1
                g_show_text(screen, str(wall_l.owner.name), font1, wall_t.center.x, wall_l.center.y, wall_l.owner.color, g_color_WHITE)
    player.number_of_houses = house_count


def g_get_player_details(choice):
    g_player_name = input("Enter your name: ")
    if choice == "host":
        for i, col in enumerate(list_of_colors):
            print(i+1, col)
        g_player_color = list_of_color_variables[int(input("Enter colour number: "))-1]
    else:
        # Connect to server to ger available colours.
        g_player_color = g_color_BLACK
        pass
    return g_player_name, g_player_color


def g_get_host_or_join():
    choice = input("Enter choice - '1 Host' or '2 Join': ")
    if choice == "1":
        return "host"
    else:
        return "join"


def g_get_status_from_game_server(socket_object, thread_object, choice, maximum_players=0):
    global received_message
    if choice == "host":
        network_send(socket_object, "host_"+str(maximum_players))
        time.sleep(0.01)
        data_from_server = received_message

    return data_from_server
