import random

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

def rand_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)