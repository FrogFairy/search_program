import os
import sys
import pygame
import requests
from scale import get_coord, geocode


LAT_STEP = 0.003
LON_STEP = 0.008
pygame.init()
size = width, height = 800, 560
screen = pygame.display.set_mode(size)
background = pygame.Color("white")
color = pygame.Color('#abcdef')
color2 = pygame.Color('#F84F4F')
status = ''
rect_map = pygame.Rect(605, 20, 190, 40)
rect_sat = pygame.Rect(605, 70, 190, 40)
rect_sat_skl = pygame.Rect(605, 120, 190, 40)
rect_reset = pygame.Rect(605, 410, 190, 40)
input_box = pygame.Rect(5, 460, 790, 40)
rect_postal = pygame.Rect(755, 170, 40, 40)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
input_color = color_inactive
active = False
text = ''
postal = False


class Map:
    def __init__(self):
        self.lat = 55.729738
        self.lon = 37.664777
        self.zoom = 15
        self.spn = '0.005,0.005'
        self.type = "map"
        self.pt = None
        self.postal_code = None

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
        elif event in ['map', "sat,skl", 'sat']:
            self.type = event
        elif event == 'reset':
            global status
            self.pt = None
            status = ''
            self.postal_code = None
            # self.lat = 55.729738
            # self.lon = 37.664777

    def search(self, req):
        global status
        res = get_coord(req)
        if res[0]:
            self.lon, self.lat = list(map(float, res[0].split(',')))
            self.zoom = 15
            self.spn = res[1]
            self.pt = self.ll() + ',pm2orl'
            status = res[2]["formatted"]
            if "postal_code" in res[2]:
                self.postal_code = res[2]["postal_code"]
            self.change_postal()
        else:
            status = "Адрес не найден"

    def change_postal(self):
        global status
        if postal and self.postal_code:
            status += ', ' + self.postal_code
        elif not postal and self.postal_code:
            status = ', '.join(status.split(', ')[:-1])


def load_map(mp):
    url = f"http://static-maps.yandex.ru/1.x/?ll={mp.ll()}&z={mp.zoom}&l={mp.type}&spn={mp.spn}"
    if mp.pt:
        url += f"&pt={mp.pt}"
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


def draw_buttons(txt):
    pygame.draw.rect(screen, color, rect_map)
    pygame.draw.rect(screen, color, rect_sat)
    pygame.draw.rect(screen, color, rect_sat_skl)
    pygame.draw.rect(screen, color2, rect_reset)
    pygame.draw.rect(screen, color, rect_postal, 2)
    font = pygame.font.Font(None, 30)

    text = font.render("Схема", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = rect_map.x + (rect_map.w - text_w) / 2
    text_y = rect_map.y + (rect_map.h - text_h) / 2
    screen.blit(text, (text_x, text_y))

    text = font.render("Спутник", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = rect_sat.x + (rect_sat.w - text_w) / 2
    text_y = rect_sat.y + (rect_sat.h - text_h) / 2
    screen.blit(text, (text_x, text_y))

    text = font.render("Гибрид", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = rect_sat_skl.x + (rect_sat_skl.w - text_w) / 2
    text_y = rect_sat_skl.y + (rect_sat_skl.h - text_h) / 2
    screen.blit(text, (text_x, text_y))

    font = pygame.font.Font(None, 24)
    text = font.render("Сбросить", True, background)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = rect_reset.x + (rect_reset.w - text_w) / 2
    text_y = rect_reset.y + (rect_reset.h - text_h) / 2
    screen.blit(text, (text_x, text_y))

    text = font.render("Почтовый индекс", True, color_active)
    text_w = text.get_width()
    text_h = text.get_height()
    text_x = rect_reset.x + (rect_reset.w - text_w - 40) / 2
    text_y = rect_postal.y + (rect_postal.h - text_h) / 2
    screen.blit(text, (text_x, text_y))
    if postal:
        pygame.draw.line(screen, color_active, (rect_postal.x, rect_postal.y),
                         (rect_postal.x + rect_postal.w - 1, rect_postal.y + rect_postal.h - 1), 5)
        pygame.draw.line(screen, color_active, (rect_postal.x + rect_postal.w - 1, rect_postal.y),
                         (rect_postal.x, rect_postal.y + rect_postal.h - 1), 5)

    font = pygame.font.Font(None, 30)
    txt_surface = font.render(txt, True, input_color)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, input_color, input_box, 2)
    font = pygame.font.Font(None, 24)
    txt = font.render(status, True, color_active)
    screen.blit(txt, ((width - txt.get_width()) / 2, 510 + (40 - txt.get_height()) / 2))


def main():
    global active, text, input_color, postal
    running = True
    mp = Map()
    font = pygame.font.Font(None, 30)
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
                if active:
                    if event.key == pygame.K_RETURN:
                        mp.search(text)
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rect_map.collidepoint(event.pos):
                    mp.update("map")
                elif rect_sat.collidepoint(event.pos):
                    mp.update("sat")
                elif rect_sat_skl.collidepoint(event.pos):
                    mp.update("sat,skl")
                elif rect_reset.collidepoint(event.pos):
                    text = ''
                    active = False
                    mp.update('reset')
                elif rect_postal.collidepoint(event.pos):
                    postal = not postal
                    mp.change_postal()
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                input_color = color_active if active else color_inactive
        screen.fill(background)
        draw_buttons(text)
        screen.blit(load_image(load_map(mp)), (0, 0))
        pygame.display.flip()
    os.remove(load_map(mp))

if __name__ == '__main__':
    main()