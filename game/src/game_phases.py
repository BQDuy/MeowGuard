from ast import Continue, Global
from src.config import Config
import sys
import time
from turtle import width

import pygame

from src.components.game_status import GameStatus
from src.components.hand import Hand
from src.components.hand_side import HandSide
from src.components.player import Player
from src.components.scoreboard import Scoreboard
from src.global_state import GlobalState
from src.services.music_service import MusicService
from src.services.visualization_service import VisualizationService
from src.utils.tools import update_background_using_scroll, update_press_key, is_close_app_event

GlobalState.load_main_screen()
VisualizationService.load_main_game_displays()

scoreboard = Scoreboard()

# Sprite Setup
P1 = Player()
H1 = Hand(HandSide.RIGHT)
H2 = Hand(HandSide.LEFT)
screen = pygame.display.set_mode([Config.WIDTH, Config.HEIGHT])
pauseDraw = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
pygame.init()
font = pygame.font.SysFont("arialblack", 14)

# Sprite Groups
hands = pygame.sprite.Group()
hands.add(H1)
hands.add(H2)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(H1)
all_sprites.add(H2)

paused = False

#Main menu
def main_menu_phase():
    scoreboard.reset_current_score()
    events = pygame.event.get()

    for event in events:
        if is_close_app_event(event):
            GlobalState.GAME_STATE = GameStatus.GAME_END
            return

        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            GlobalState.GAME_STATE = GameStatus.GAMEPLAY

    GlobalState.SCROLL = update_background_using_scroll(GlobalState.SCROLL)
    VisualizationService.draw_background_with_scroll(GlobalState.SCREEN, GlobalState.SCROLL)
    GlobalState.PRESS_Y = update_press_key(GlobalState.PRESS_Y)
    VisualizationService.draw_main_menu(GlobalState.SCREEN, scoreboard.get_max_score(), GlobalState.PRESS_Y)



#Game play
def gameplay_phase():
    events = pygame.event.get()
    global paused
    paused = False
    for event in events:
        if is_close_app_event(event):
            game_over()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.KSCAN_F1: 
                if paused:
                    paused = False
            else:
                paused = True
                GlobalState.GAME_STATE = GameStatus.PAUSE
                return
               
    if not paused:
        P1.update()
        H1.move(scoreboard, P1.player_position)
        H2.move(scoreboard, P1.player_position)
        H1.move(scoreboard, P1.player_position)
        H2.move(scoreboard, P1.player_position)

        GlobalState.SCROLL = update_background_using_scroll(GlobalState.SCROLL)
        VisualizationService.draw_background_with_scroll(GlobalState.SCREEN, GlobalState.SCROLL)

        P1.draw(GlobalState.SCREEN)
        H1.draw(GlobalState.SCREEN)
        H2.draw(GlobalState.SCREEN)
        scoreboard.draw(GlobalState.SCREEN)

        if pygame.sprite.spritecollide(P1, hands, False, pygame.sprite.collide_mask):
            scoreboard.update_max_score()
            MusicService.play_slap_sound()
            time.sleep(0.5)
            game_over()
            

# def gameplay_pause():

def exit_game_phase():
    pygame.quit()
    sys.exit()

def gameplay_pause():
    pygame.draw.rect(pauseDraw, (128, 128, 128, 150), [0, 0, Config.WIDTH, Config.HEIGHT])
    pygame.draw.rect(pauseDraw, 'light gray', [200, 150, 600, 50], 0, 10)
    VisualizationService.draw_paused_menu(GlobalState.SCREEN, GlobalState.SCROLL, GlobalState.PRESS_Y)
    draw_text("Press any key to continues", font, (30, 120, 160), Config.WIDTH/4, Config.HEIGHT/4)
    global paused
    events = pygame.event.get()
    for event in events:
        if is_close_app_event(event):
            game_over()
            return
        if event.type == pygame.KEYDOWN:    
            paused = False
            GlobalState.GAME_STATE = GameStatus.GAMEPLAY
                
def draw_text(text, font, text_col,x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))
    
def game_over():
    P1.reset()
    H1.reset()
    H2.reset()
    GlobalState.GAME_STATE = GameStatus.MAIN_MENU
    time.sleep(0.5)
