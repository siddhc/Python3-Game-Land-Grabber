import pygame
import time
from game_constants import *
from game_variables import *
from game_functions import *

#Initiate
pygame.init()
screen_fill_color = g_color_WHITE

#Game settings
g_SCREEN = pygame.display.set_mode((g_WIDTH, g_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption(g_NAME)
g_clock = pygame.time.Clock()


g_post_coordinates, g_wall_list, g_fonts = g_initialize_parameters(g_SCREEN, g_c_posts_number, g_r_posts_number)

#Game variables
game_running = True
me = Player(g_player_name, g_player_color)

#Game loop
while game_running:

    # Clock management
    g_clock.tick(g_FPS)

    # Clear screen
    g_SCREEN.fill(screen_fill_color)

    # Capture events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_x = event.pos[0]
            mouse_y = event.pos[1]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            g_make_player_wall(g_SCREEN, g_currently_selected_wall, me)

    # Draw posts
    g_draw_posts(g_SCREEN, g_post_coordinates)

    # Draw walls
    g_draw_walls(g_SCREEN, g_wall_list)

    # Show wall trace
    g_currently_selected_wall = g_show_wall_trace(g_SCREEN, g_wall_list, mouse_x, mouse_y)


    # Display texts
    g_show_text(g_SCREEN, str(me.number_of_walls) + '_' + str(me.number_of_houses), g_fonts[0], 50, 25, me.color, g_color_WHITE)

    # Count houses
    print(g_count_houses(g_SCREEN, g_post_coordinates, g_fonts[1], g_wall_list, me))

    # Screen flip
    pygame.display.flip()

# Quit game
pygame.quit()