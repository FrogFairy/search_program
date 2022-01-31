import os
import sys

import pygame
import requests


class Map:
    def __init__(self):
        self.lat = 55.729738
        self.lon = 37.664777
        self.zoom = 15
        self.type = "map"

    def ll(self):
        return f'{self.lon},{self.lat}'

    def update(self, event):
        if event == 'up' and self.zoom < 19:
            self.zoom += 1
        elif event == 'down' and self.zoom > 2:
            self.zoom -= 1


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


def main():
    pygame.init()
    size = width, height = 600, 450
    screen = pygame.display.set_mode(size)
    running = True
    mp = Map()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    mp.update('up')
                elif event.key == pygame.K_DOWN:
                    mp.update('down')
        screen.blit(load_image(load_map(mp)), (0, 0))
        pygame.display.flip()
    os.remove(load_map(mp))

if __name__ == '__main__':
    main()
