import color
import math
import os
import pygame


LEFT_NORM = -1 / math.sqrt(2), -1 / math.sqrt(2)
RIGHT_NORM = 1 / math.sqrt(2), -1 / math.sqrt(2)
UP_NORM = 0, -1
BALL_OUT = 25

class Configuration(object):

    def __init__(self):
        self.screen_height = 800
        self.screen_width = 800

        self.player_width = 100
        self.player_height = 10
        self.player_speed = 320
        self.player_start_height = .95
        self.player_deblink = 10

        self.ball_length = 10
        self.ball_speed = 400

        self.strike_zone_divisor = 3

    @property
    def ball_size(self):
        return self.ball_length, self.ball_length

    @property
    def player_resolution(self):
        return self.player_width, self.player_height

    @property
    def screen_resolution(self):
        return self.screen_width, self.screen_height


class Paddle(pygame.sprite.Sprite):

    def __init__(self, screen_rect, config, *groups):
        super(Paddle, self).__init__(*groups)
        self.image = pygame.Surface(config.player_resolution)
        self.image.fill(color.white)
        self.rect = self.image.get_rect()
        self.rect.midbottom = int(config.screen_width / 2), int(config.screen_height * config.player_start_height)
        self.x = self.rect.centerx
        self.direction = 0
        self.speed = config.player_speed
        self.deblink = config.player_deblink
        self.screen = screen_rect

    def update(self, td):
        pos_x = pygame.mouse.get_pos()[0]
        if pos_x - self.x > self.deblink:
            self.direction = 1
        elif pos_x - self.x < self.deblink * -1:
            self.direction = -1
        else:
            self.direction = 0

        self.x += self.direction * self.speed * td
        self.rect.centerx = int(self.x)
        if self.rect.left < self.screen.left:
            self.rect.left = self.screen.left
        elif self.rect.right > self.screen.right:
            self.rect.right = self.screen.right

class Ball(pygame.sprite.Sprite):

    def __init__(self, paddle_rect, screen_rect, config, *groups):
        super(Ball, self).__init__(*groups)
        self.image = pygame.Surface(config.ball_size).convert()
        self.image.set_colorkey(color.black)
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, color.white, self.rect.center, self.rect.right / 2)
        self.rect.midbottom = paddle_rect.midbottom
        self.x = self.rect.x
        self.y = self.rect.y
        self.screen = screen_rect
        self.paddle = paddle_rect

        self.facing = RIGHT_NORM
        self.speed = config.ball_speed
        self.strike_zone = self.paddle.width / config.strike_zone_divisor

    def update(self, td):
        self.x, self.y = self.x + self.velocity[0] * td, self.y + self.velocity[1] * td
        self.rect.topleft = self.x, self.y
        if self.rect.left < self.screen.left or self.rect.right > self.screen.right:
            self.facing = self.facing[0] * -1, self.facing[1]
            if self.rect.left < self.screen.left:
                self.rect.left = self.screen.left
            elif self.rect.right > self.screen.right:
                self.rect.right = self.screen.right
        if self.rect.top < self.screen.top:
            self.facing = self.facing[0], self.facing[1] * -1
        if self.facing[1] > 0 and self.rect.colliderect(self.paddle):
            if self.rect.right < self.paddle.left + self.strike_zone:
                self.facing = normalize(reflection(LEFT_NORM, self.facing))
            elif self.rect.left < self.paddle.left + self.strike_zone:
                surface_norm = LEFT_NORM[0] + UP_NORM[0], LEFT_NORM[1] + UP_NORM[1]
                self.facing = normalize(reflection(surface_norm, self.facing))
            elif self.rect.left > self.paddle.left + self.strike_zone and self.rect.right < self.paddle.right - self.strike_zone:
                self.facing = normalize(reflection(UP_NORM, self.facing))
            elif self.rect.right > self.paddle.right - self.strike_zone:
                surface_norm = RIGHT_NORM[0] + UP_NORM[0], RIGHT_NORM[1] + UP_NORM[1]
                self.facing = normalize(reflection(surface_norm, self.facing))
            else:
                self.facing = normalize(reflection(RIGHT_NORM, self.facing))
        if self.rect.top > self.screen.bottom:
            # OMFG YOU LOST
            pygame.event.post(pygame.event.Event(BALL_OUT))  # TODO: What if multiple balls? Fix later.

    @property
    def velocity(self):
        return self.facing[0] * self.speed, self.facing[1] * self.speed


def reflection(surface_norm, facing):
    """
    r = f - 2(f dot n)surface_norm
    :param surface_norm: iterable x, y Normalized Vector
    :param facing: iterable x, y
    :return: (x, y)
    """

    dot = dot_product(surface_norm, facing)
    multiplier = 2 * dot
    norm = multiplier * surface_norm[0], multiplier * surface_norm[1]
    return facing[0] - norm[0], facing[1] - norm[1]


def dot_product(vector1, vector2):
    """

    :param vector1: iterable x, y
    :param vector2: iterable x, y
    :return: (x, y)
    """
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]


def normalize(vector):
    """

    :param vector: iterable x, y
    :return: x, y
    """
    length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return vector[0] / length, vector[1] / length


def main(config, screen):
    running = True

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.QUIT, BALL_OUT])

    clock = pygame.time.Clock()
    player = pygame.sprite.GroupSingle()
    ball = pygame.sprite.GroupSingle()

    screen_rect = screen.get_rect()
    Paddle(screen_rect, config, player)
    Ball(player.sprite.rect, screen_rect, config, ball)
    while running:
        td = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == BALL_OUT:
                Ball(player.sprite.rect, screen_rect, config, ball)

        player.update(td)
        ball.update(td)

        screen.fill(color.black)
        player.draw(screen)
        ball.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    configuration = Configuration()
    pygame.init()
    game_screen = pygame.display.set_mode(configuration.screen_resolution)
    main(configuration, game_screen)
    pygame.quit()