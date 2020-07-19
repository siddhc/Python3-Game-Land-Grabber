import pygame
import time
from game_constants import *
from game_variables import *
from game_functions import *
import game_client
import game_server
import pickle

#Initiate
screen_fill_color = g_color_WHITE

#Game variables
game_running = True
player_details_taken = False
host_join_choice_made = False
all_players_have_joined = False

def main():
    global game_running
    global host_join_choice_made
    global player_details_taken
    global all_players_have_joined

    if not host_join_choice_made:
        choice = g_get_host_or_join()
    host_join_choice_made = True

    if not player_details_taken:
        player_name = g_get_player_name()
        me = Player(player_name)
        t = threading.Thread(target=receiving_threaded, args=(me,))
        t.start()
        me.type = choice
        me.number, me.color = g_get_player_number_and_color(me)
        current_number_of_players = me.number
        print(f'me.number = {me.number}, me.color = {me.color}')
        player_details_taken = True

    if current_number_of_players == maximum_players_allowed:
        all_players_have_joined = True

    while not all_players_have_joined:
        print("Checking with Server now ...")
        time.sleep(2)
        current_number_of_players = g_number_of_players_from_game_server(me)
        print(f'ch = {choice}, cp = {current_number_of_players}, mp = {maximum_players_allowed}')
        if current_number_of_players == maximum_players_allowed:
            all_players_have_joined = True

    print("Entering game !")

    #Game settings
    pygame.init()
    g_SCREEN = pygame.display.set_mode((g_WIDTH, g_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption(g_NAME)
    g_clock = pygame.time.Clock()
    g_post_coordinates, g_wall_list, g_fonts = g_initialize_parameters(g_SCREEN, g_c_posts_number, g_r_posts_number)

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
                if all_players_have_joined:
                    g_make_player_wall(g_SCREEN, g_currently_selected_wall, me)
                else:
                    print("Game yet to start.")


        if all_players_have_joined:
            # Draw posts
            g_draw_posts(g_SCREEN, g_post_coordinates)

            # Draw walls
            g_draw_walls(g_SCREEN, g_wall_list)

            # Show wall trace
            g_currently_selected_wall = g_show_wall_trace(g_SCREEN, g_wall_list, mouse_x, mouse_y)

            # Display texts
            g_show_text(g_SCREEN, str(me.number_of_walls) + '_' + str(me.number_of_houses), g_fonts[0], 50, 25, me.color, g_color_WHITE)

            # Count houses
            g_count_houses(g_SCREEN, g_post_coordinates, g_fonts[1], g_wall_list, me)

            # Screen flip

        pygame.display.flip()

    # Quit game
    pygame.quit()


if __name__ == "__main__":
    main()