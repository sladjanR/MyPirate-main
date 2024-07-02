from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join    # Gives relative paths to specific os

from support import *
from data import Data
from debug import debug
from ui import UI 
import json
import webbrowser
from app import *
import threading
import os
import time


okidac = False
def save_score(score):
    currentdir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(currentdir,'scores.json')
    with open(data_file, 'r+') as f:
        scores = json.load(f)
        scores.append(score)
        f.seek(0)
        json.dump(scores, f, indent=4)

def get_player_name():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WIDNDOW_HEIGHT))
    font = pygame.font.Font(None, 50)
    label = font.render("Unesite ime:", False, 'lightskyblue3')
    label_rect = label.get_rect()
    label_rect.midtop = (WINDOW_WIDTH // 2, WIDNDOW_HEIGHT // 2 - 100)
    input_box = pygame.Rect(WINDOW_WIDTH // 2 - 95, WIDNDOW_HEIGHT // 2, WINDOW_WIDTH // 2, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        screen.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        background_image = pygame.image.load('data/wallpaper.jpg').convert()
        background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WIDNDOW_HEIGHT))
        screen.blit(background_image,(0,0))
        screen.blit(label,label_rect)
        screen.blit(txt_surface,(input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

    return text

class Game:
    def __init__(self):
        self.player_name = get_player_name()
        self.player_score = {"player": self.player_name, "score": 0}
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WIDNDOW_HEIGHT))
        pygame.display.set_caption("My Pirate World")
        # Cap fps (not to go 1000, and not to be too low for slow PC-s)
        self.clock = pygame.time.Clock()
        self.import_assets()

        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui) 
        
        self.tmx_maps = {0: load_pygame(join('data','levels','LEVEL1_PROJEKAT.tmx')),
                         1: load_pygame(join('data','levels','LEVEL2_PROJEKAT.tmx'))}
        self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.audio_files, self.data)
        self.bg_music.play(-1)

    def import_assets(self):
       self.level_frames = {
			'flag': import_folder( 'graphics', 'level', 'flag'),
			'saw': import_folder( 'graphics', 'enemies', 'saw', 'animation'),
			'floor_spike': import_folder( 'graphics','enemies', 'floor_spikes'),
			'palms': import_sub_folders('graphics', 'level', 'palms'),
			'candle': import_folder('graphics','level', 'candle'),
			'window': import_folder('graphics','level', 'window'),
			'big_chain': import_folder('graphics','level', 'big_chains'),
			'small_chain': import_folder('graphics','level', 'small_chains'),
			'candle_light': import_folder( 'graphics','level', 'candle light'),
            'player': import_sub_folders('graphics','player'),
            'saw' : import_folder('graphics', 'enemies', 'saw', 'animation'),
            'saw_chain' : import_image('graphics', 'enemies', 'saw', 'saw_chain'),
            'helicopter' : import_folder('graphics', 'level', 'helicopter'),
            'boat' : import_folder('graphics', 'objects', 'boat'), 
            'spike': import_image('graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
            'spike_chain' : import_image('graphics', 'enemies', 'spike_ball', 'spiked_chain'),
            'tooth': import_folder('graphics', 'enemies','tooth','run'),
            'shell' : import_sub_folders('graphics', 'enemies', 'shell'),
            'pearl' : import_image('graphics', 'enemies', 'bullets', 'pearl'),
            'items' : import_sub_folders('graphics', 'items'),
            'particle': import_folder('graphics', 'effects', 'particle'),  
            'water_top': import_folder('graphics', 'level', 'water', 'top'),
            'water_body': import_image('graphics', 'level', 'water', 'body'),   # Simple an transparent image
            'bg_tiles': import_folder_dict('graphics', 'level', 'bg', 'tiles'), 
            'cloud_small': import_folder('graphics', 'level', 'clouds', 'small'),
            'cloud_large': import_image('graphics', 'level', 'clouds', 'large_cloud'),
        }
       
       
       self.font = pygame.font.Font(join('graphics','ui','runescape_uf.ttf'), 35)
       self.ui_frames = {
           'heart': import_folder('graphics', 'ui', 'heart'),
           'coin': import_image('graphics', 'ui', 'coin')
       }

       self.audio_files = {
           'coin' : pygame.mixer.Sound(join('audio', 'coin.wav')),
           'jump' : pygame.mixer.Sound(join('audio', 'jump.wav')),
           'damage' : pygame.mixer.Sound(join('audio', 'damage.wav')),
           'pearl' : pygame.mixer.Sound(join('audio', 'pearl.wav'))
       }
       self.bg_music = pygame.mixer.Sound(join('audio', 'background.mp3'))
       self.bg_music.set_volume(0.1)


    def change_level(self):
        global okidac
                                                                                                                                                                                                                        
        if self.data.next_level:
            if self.data.level_number == 2:
                self.player_score['score'] = self.data.coins
                save_score(self.player_score)
                
                
                webbrowser.open('http://127.0.0.1:5000/scoreboard')  # All in one html
                # webbrowser.open('http://127.0.0.1:5000/api/scores/mapped/100')  # Map example
                # webbrowser.open('http://127.0.0.1:5000/api/scores/reduced')     # Reduce example
                # webbrowser.open('http://127.0.0.1:5000/api/scores/filtered/100')  # Filter example
                self.data.level_number = 0
                okidac = True
            self.current_stage = Level(self.tmx_maps[self.data.level_number], self.level_frames, self.audio_files, self.data)
            self.data.next_level = False


    def run(self):
        while True:
            # Divsion  with 1000 seconds
            # in a .tick() method we pass how much fps we want, if are no arguments there it's maximum frame rate for us
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            
            self.change_level()
            if okidac:
                pygame.quit()
                time.sleep(3)
                sys.exit()
            
            self.current_stage.run(dt)
            self.ui.update(dt)
            # debug(self.data.coins)
            pygame.display.update()

        

if __name__ == "__main__":
    th1 = threading.Thread(args=(), target=app.run)
    th1.daemon = True
    th1.start()
    
    game = Game()
    game.run()
    
    # th1 = threading.Thread(args=(), target=game.run)
    