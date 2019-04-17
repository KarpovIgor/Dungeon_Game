from abc import ABC, abstractmethod
import pygame
import random
import math


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class AbstractObject(ABC):
    def __init__(self):
        self.sprite = None
        self.position = None


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        super().__init__()
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        super().__init__()
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.alive = True
        self._hp = self.max_hp

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        if value < 0:
            self._hp = 0
            self.alive = False
            return
        self._hp = value

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    # @property
    # def exp(self):
    #     return self._exp
    #
    # @exp.setter
    # def exp(self, value):
    #     next(self.level_up())

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp


class Enemy(Creature, Interactive):
    """
    Класс вражины поганой
    """
    def __init__(self, icon, stats, xp, position):
        """
        какой то жудкий конструктор,
        видать придёться всё добро это по атрибутам распихивать
        :param icon: картинка видать чудища заморского
        :param stats: ну тут силушка богатырская будет
        :param xp: хрюшка
        :param position: и семейное пложение из профиля VK
        """
        super().__init__(icon, stats, position)
        self.xp = xp

    def interact(self, engine, hero):
        engine.notify(f"""Battle with Hero and Enemy:""")
        while hero.hp > 0 and self.hp > 0:
            success_hero_hit = 1 - (random.random() * ((hero.stats['luck']*0.01) + 1) -
                                   0.5 - math.sqrt(self.stats['intelligence']) * 0.01)
            hero_hit = int(hero.stats['strength'] * success_hero_hit*0.5)
            self.hp -= hero_hit
            engine.notify(f"Hero hit at {hero_hit}")
            if self.hp <= 0:
                break

            success_enemy_hit = 1 - (random.random() * ((1 / self.stats['luck']) + 1) -
                                     0.5 - math.sqrt(hero.stats['intelligence']) * 0.01)
            enemy_hit = int(self.stats['strength'] * success_enemy_hit * 0.5)
            hero.hp -= enemy_hit
            engine.notify(f"Enemy hit at {enemy_hit}")

        if self.hp > 0:
            engine.notify(f"Hero wuz killed")
        else:
            engine.notify(f"Hero win and get {self.xp} exp")
            hero.exp += self.xp
            for mess in hero.level_up():
                engine.notify(mess)


class Effect(Hero):
    """
    вот и декоратор нашелся
    """
    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self._hp = self.base._hp
        self.apply_effect()

    def _calculate_stat(self, key, new_value):
        if self.stats[key] + new_value > 0:
            self.stats[key] += new_value
        else:
            self.stats[key] = 0

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @property
    def alive(self):
        return self.base.alive


    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def apply_effect(self):
        self._calculate_stat('strength', 2)
        self._calculate_stat('endurance', 2)
        self._calculate_stat('luck', 2)
        self._calculate_stat('intelligence', -5)

class Blessing(Effect):
    def apply_effect(self):
        self._calculate_stat("strength", 1)
        self._calculate_stat("endurance", 1)
        self._calculate_stat("luck", 1)
        self._calculate_stat("intelligence", 1)


class Weakness(Effect):
    def apply_effect(self):
        self._calculate_stat("strength", -5)
        self._calculate_stat("endurance", -5)
        self._calculate_stat("luck", -5)
        self._calculate_stat("intelligence", -5)


class Fuddle (Effect):
    def apply_effect(self):
        self._calculate_stat("strength", 2)
        self._calculate_stat("endurance", -2)
        self._calculate_stat("intelligence", -5)