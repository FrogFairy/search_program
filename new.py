import os
import sys
import pygame
import requests


LAT_STEP = 0.003
LON_STEP = 0.008
pygame.init()
size = width, height = 700, 450
screen = pygame.display.set_mode(size)
background = pygame.Color("white")
color = pygame.Color('#abcdef')


class Map:
    def __init__(self):
        self.lat = 55.729738
        self.lon = 37.664777
        self.zoom = 15
        self.type = "map"

    def ll(self):
        return f'{self.lon},{self.lat}'

    def update(self, event):
        if event == 'plus' and self.zoom < 19:
            self.zoom += 1
        elif event == 'minus' and self.zoom > 2:
            self.zoom -= 1
        elif event == 'up':
            if self.lat + LAT_STEP * 2 ** (15 - self.zoom) < 80:
                self.lat += LAT_STEP * 2 ** (15 - self.zoom)
            else:
                self.lat = 80
        elif event == 'down':
            if self.lat - LAT_STEP * 2 ** (15 - self.zoom) > -80:
                self.lat -= LAT_STEP * 2 ** (15 - self.zoom)
            else:
                self.lat = -80
        elif event == 'left':
            if self.lon - LON_STEP * 2 ** (15 - self.zoom) > -180:
                self.lon -= LON_STEP * 2 ** (15 - self.zoom)
            else:
                self.lon = -180
        elif event == 'right':
            if self.lon + LON_STEP * 2 ** (15 - self.zoom) < 180:
                self.lon += LON_STEP * 2 ** (15 - self.zoom)
            else:
                self.lon = 180
        else:
            self.type = event


def load_map(mp):
    url = f"http://static-maps.yandex.ru/1.x/?ll={mp.ll()}&z={mp.zoom}&l={mp.type}"
    response = requests.get(url)
    if not response:
        print("Ошибка выполнения запроса:")
        print(url)
        print("Http статус:", response.status_code, "(", response.reason, ")")
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
        return map_file
    except Exception as e:
        print(e)


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def draw_buttons():
    pygame.draw.rect(screen, color, ((605, 20), (90, 40)))
    pygame.draw.rect(screen, color, ((605, 70), (90, 40)))
    pygame.draw.rect(screen, color, ((605, 120), (90, 40)))
    font = pygame.font.Font(None, 30)

    text = font.render("Схема", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = 605 + (90 - text_w) / 2
    text_y = 20 + (40 - text_h) / 2
    screen.blit(text, (text_x, text_y))

    text = font.render("Спутник", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = 605 + (90 - text_w) / 2
    text_y = 70 + (40 - text_h) / 2
    screen.blit(text, (text_x, text_y))

    text = font.render("Гибрид", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = 605 + (90 - text_w) / 2
    text_y = 120 + (40 - text_h) / 2
    screen.blit(text, (text_x, text_y))


def main():
    running = True
    mp = Map()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEUP:
                    mp.update('plus')
                elif event.key == pygame.K_PAGEDOWN:
                    mp.update('minus')
                elif event.key == pygame.K_UP:
                    mp.update('up')
                elif event.key == pygame.K_DOWN:
                    mp.update('down')
                elif event.key == pygame.K_RIGHT:
                    mp.update('right')
                elif event.key == pygame.K_LEFT:
                    mp.update('left')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 605 <= event.pos[0] <= 695 and 20 <= event.pos[1] <= 60:
                    mp.update("map")
                elif 605 <= event.pos[0] <= 695 and 70 <= event.pos[1] <= 110:
                    mp.update("sat")
                elif 605 <= event.pos[0] <= 695 and 120 <= event.pos[1] <= 160:
                    mp.update("sat,skl")
        screen.fill(background)
        draw_buttons()
        screen.blit(load_image(load_map(mp)), (0, 0))
        pygame.display.flip()
    os.remove(load_map(mp))

if __name__ == '__main__':
    main()
