import pygame
import collections

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}


class ScreenHandle(pygame.Surface):
    """
    Крайний класс в цепочке обязанностей
    ДНИЩЕ, так сказать
    """
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        self.wight = args[0][0]
        self.height = args[0][1]
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def draw(self, canvas):
        """
        рисует или передаёт дальше
        :param canvas: экземпляр gameDisplay от pygame
        """
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        """
        Реализует передачу действий для отрисовки всем звеньям цепи
        :param engine: Logic.GameEngine
        """
        self.game_engine = engine
        if self.successor is not None:
            self.successor.connect_engine(engine)


class GameSurface(ScreenHandle):

    @property
    def min_x(self):
        return self.game_engine.hero.position[0] - 6

    @property
    def min_y(self):
        return self.game_engine.hero.position[1] - 4

    def draw_hero(self):
        self.blit(self.game_engine.hero.sprite,
                  (6* self.game_engine.sprite_size,
                   4* self.game_engine.sprite_size))

    def draw_dead_monitor(self):
        font = pygame.font.SysFont("comicsansms", 120)
        small_font = pygame.font.SysFont("comicsansms", 38)
        self.blit(font.render(f'WASTED', True, colors["red"]),
                  (150, 200))

        self.blit(small_font.render(f'press R to restart', True, colors["red"]),
                  (238, 295))


    def draw_map(self):
        if self.game_engine.map:
            # можно ускорить прорисовку , ограничив ещё и по max_y + max_x
            for i in range(len(self.game_engine.map[0]) - self.min_x):
                for j in range(len(self.game_engine.map) - self.min_y):
                    if (self.min_y + j < 0 or
                       self.min_x + i < 0):
                        # рисуем стену
                        self.blit(self.game_engine.map[0][0][
                                      0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
                        continue
                    self.blit(self.game_engine.map[self.min_y + j][self.min_x + i][
                              0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
        else:
            self.fill(colors["white"])

    def draw_objects(self):
        for obj in self.game_engine.objects:
            self.blit(obj.sprite[0], ((obj.position[0] - self.min_x) * self.game_engine.sprite_size,
                                      (obj.position[1] - self.min_y) * self.game_engine.sprite_size))

    def draw(self, canvas):
        if self.game_engine.hero.alive:
            self.draw_map()

            self.draw_objects()

            self.draw_hero()
        else:
            self.draw_dead_monitor()

        super().draw(canvas)
    # draw next surface in chain


class ProgressBar(ScreenHandle):
    """
    переименовал все engine в game_engine
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fill(colors["wooden"])

    def draw(self, canvas):
        if self.game_engine.hero.alive:
            self.fill((153, 92, 0, 120))
            #self.fill(colors["wooden"])
            pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
            pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

            pygame.draw.rect(self, colors[
                             "red"], (50, 30, 200 * self.game_engine.hero.hp / self.game_engine.hero.max_hp, 30))
            pygame.draw.rect(self, colors["green"], (50, 70,
                                                     200 * self.game_engine.hero.exp / (100 * (2**(self.game_engine.hero.level - 1))), 30))

            font = pygame.font.SysFont("comicsansms", 20)
            self.blit(font.render(f'Hero at {self.game_engine.hero.position}', True, colors["black"]),
                      (250, 0))

            self.blit(font.render(f'{self.game_engine.level} floor', True, colors["black"]),
                      (10, 0))

            self.blit(font.render(f'HP', True, colors["black"]),
                      (10, 30))
            self.blit(font.render(f'Exp', True, colors["black"]),
                      (10, 70))

            self.blit(font.render(f'{self.game_engine.hero.hp}/{self.game_engine.hero.max_hp}', True, colors["black"]),
                      (60, 30))
            self.blit(font.render(f'{self.game_engine.hero.exp}/{(100*(2**(self.game_engine.hero.level-1)))}', True, colors["black"]),
                      (60, 70))

            self.blit(font.render(f'Level', True, colors["black"]),
                      (300, 30))
            self.blit(font.render(f'Gold', True, colors["black"]),
                      (300, 70))

            self.blit(font.render(f'{self.game_engine.hero.level}', True, colors["black"]),
                      (360, 30))
            self.blit(font.render(f'{self.game_engine.hero.gold}', True, colors["black"]),
                      (360, 70))

            self.blit(font.render(f'Str', True, colors["black"]),
                      (420, 30))
            self.blit(font.render(f'Luck', True, colors["black"]),
                      (420, 70))

            self.blit(font.render(f'{self.game_engine.hero.stats["strength"]}', True, colors["black"]),
                      (480, 30))
            self.blit(font.render(f'{self.game_engine.hero.stats["luck"]}', True, colors["black"]),
                      (480, 70))

            self.blit(font.render(f'SCORE', True, colors["black"]),
                      (550, 30))
            self.blit(font.render(f'{self.game_engine.score:.4f}', True, colors["black"]),
                      (550, 70))

        super().draw(canvas)  # добавил, но возможно придется удалять
    # draw next surface in chain


class InfoWindow(ScreenHandle):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill((0, 0, 0, 0))
        #self.fill(colors["wooden"])

        font = pygame.font.SysFont("comicsansms", 15)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["white"]),
                      (5, 20 + 18 * i))

        super().draw(canvas)

    def connect_engine(self, engine):
        engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):
    """
    переименовал все engine в game_engine
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 25
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])

    def draw(self, canvas):
        alpha = 0
        if self.game_engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        size = self.get_size()
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.game_engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                              (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, ((128, 128, 255))),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, ((128, 128, 255))),
                          (150, 50 + 30 * i))

        super().draw(canvas)


class MiniMap(ScreenHandle):
    """
    рисовка миникарты
    """

    def draw(self, canvas):

        if self.game_engine.map:
            self.fill(colors["wooden"])

            step_wight = self.wight/len(self.game_engine.map[0])
            step_height = self.height/len(self.game_engine.map)

            # draw hero
            pygame.draw.rect(self, colors[
                "red"], (int(step_wight * self.game_engine.hero.position[0]),
                           int(step_height * self.game_engine.hero.position[1]), 2, 2))

            # draw obj
            for obj in self.game_engine.objects:
                pygame.draw.rect(self, colors[
                    "black"], (int(step_wight * obj.position[0]),
                                    int(step_height * obj.position[1]), 2, 2))


        else:
            self.fill(colors["white"])

        super().draw(canvas)