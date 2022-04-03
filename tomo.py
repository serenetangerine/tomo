#!/usr/bin/env python3

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import argparse
from datetime import datetime
import os
import random
import subprocess
from time import sleep


def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp', '-T', help='flag to display temperature', action='store_true')
    parser.add_argument('--time', '-t', help='flag to display time', action='store_true')
    parser.add_argument('--skip', '-s', help='flag to skip egg hatch into', action='store_true')

    args = parser.parse_args()
    return args


def cpuTemp(tomo):
    command = '/opt/vc/bin/vcgencmd measure_temp'
    temp = subprocess.check_output(command, shell=True)
    temp = temp.decode()
    temp = temp[:9]
    temp = temp[5:]
    if float(temp) >= 50.0:
        tomo.hot = True
    else:
        tomo.hot = False
    temp = temp + ' C'
    return temp


def checkSpotify(tomo):
    command = '/usr/bin/ps -aux | /usr/bin/grep ncspot | /usr/bin/wc -l'
    output = subprocess.check_output(command, shell=True)
    output.decode()
    if int(output) >= 3:
        tomo.dancing = True
    else:
        tomo.dancing = False
    return int(output)


class Tomo:
    def __init__(self):
        # load sprites
        directory = os.path.dirname(__file__)

        self.tomo_left = Image.open('%s/sprites/tomo/tomo.bmp' % directory).convert('1')
        self.tomo_right = self.tomo_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_sweat_left = Image.open('%s/sprites/tomo/tomo_sweat.bmp' % directory).convert('1')
        self.tomo_sweat_right = self.tomo_sweat_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_excite_left = Image.open('%s/sprites/tomo/tomo_excite.bmp' % directory).convert('1')
        self.tomo_excite_right = self.tomo_excite_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_eat_left = Image.open('%s/sprites/tomo/tomo_eat.bmp' % directory).convert('1')
        self.tomo_eat_right = self.tomo_eat_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_dance_left = Image.open('%s/sprites/tomo/tomo_dance.bmp' % directory).convert('1')
        self.tomo_dance_right = self.tomo_dance_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_sick_left = Image.open('%s/sprites/tomo/tomo_sick.bmp' % directory).convert('1')
        self.tomo_sick_right = self.tomo_sick_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_love_left = Image.open('%s/sprites/tomo/tomo_love.bmp' % directory).convert('1')
        self.tomo_love_right = self.tomo_love_left.transpose(Image.FLIP_LEFT_RIGHT)

        self.tomo_rip = Image.open('%s/sprites/tomo/tomo_rip.bmp' % directory).convert('1')

        # default sprite
        self.tomo_sprite = self.tomo_left

        # initial coordinates
        (self.x, self.y) = (50, 34)

        # set direction
        self.direction = 'left'

        # attributes
        self.food_consumed = 0
        self.hot = False
        self.dancing = False
        self.hunger = 200 
        self.sick = False
        self.deaths = 0

    def walk(self, temp):
        self.checkSick()

        # hunger depleats faster when hot
        if self.hot:
            self.hunger = self.hunger - 2
        else:
            self.hunger = self.hunger - 1

        if self.hunger <= 0:
            self.die()

        # more likely to not move if sick
        if self.sick:
            dir = random.randint(0,2)
        else:
            dir = random.randint(0, 6)
        
        # do nothing if 0
        if dir == 0:
            pass
        # walk left if odd
        elif dir % 2 == 1:
            self.direction = 'left'
            if self.sick:
                self.tomo_sprite = self.tomo_sick_left
            elif self.dancing:
                self.tomo_sprite = self.tomo_dance_left
            elif self.hot:
                self.tomo_sprite = self.tomo_sweat_left
            else:
                self.tomo_sprite = self.tomo_left
            if self.x > 0:
                self.x = self.x - 2
        # walk right if even
        elif dir % 2 == 0:
            self.direction = 'right'
            if self.sick:
                self.tomo_sprite = self.tomo_sick_right
            elif self.dancing:
                self.tomo_sprite = self.tomo_dance_right
            elif self.hot: 
                self.tomo_sprite = self.tomo_sweat_right
            else:
                self.tomo_sprite = self.tomo_right
            if self.x < 100:
                self.x = self.x + 2
        
        if self.x % 3 == 0:
            self.y = 32
        else:
            self.y = 34

    def eat(self, count):
        self.hunger = 200
        if count % 2 == 0:
            if self.direction == 'left':
                self.tomo_sprite = self.tomo_excite_left
            else:
                self.tomo_sprite = self.tomo_excite_right
        else:
            if self.direction == 'left':
                self.tomo_sprite = self.tomo_eat_left
            else:
                self.tomo_sprite = self.tomo_eat_right

    def checkSick(self):
        if self.sick:
            sick = random.randint(0,10)
            if sick == 0:
                self.sick = False
        else:
            sick = random.randint(0, 31)
            if sick == 0:
                self.sick = True
     
    def die(self):
        self.tomo_sprite = self.tomo_rip
        draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)
        draw.text((0, 7), 'tomo died :(', font=font, fill=255)
        image.paste(self.tomo_sprite, (50, 34))
        disp.image(image)
        disp.display()
        sleep(10)

        self.respawn()

    def respawn(self):
        main()

class Egg:
    def __init__(self):
        # load sprites
        directory = os.path.dirname(__file__)
        self.egg1 = Image.open('%s/sprites/egg/egg1.bmp' % directory).convert('1')
        self.egg2 = Image.open('%s/sprites/egg/egg2.bmp' % directory).convert('1')
        self.egg3 = Image.open('%s/sprites/egg/egg3.bmp' % directory).convert('1')

        # default sprite
        self.egg_sprite = self.egg1

        # initial coordinates
        (self.x, self.y) = (50, 34)

        self.count = 0

    def idle(self):
        if self.count % 2 == 0:
            self.egg_sprite = self.egg1
        else:
            self.egg_sprite = self.egg2

        self.count = self.count + 1

    def hatch(self):
        if self.count % 2 == 0:
            self.egg_sprite = self.egg1
        else:
            self.egg_sprite = self.egg3

        self.count = self.count + 1


class Food:
    def __init__(self):
        # load sprites
        directory = os.path.dirname(__file__)
        self.peach = Image.open('%s/sprites/food/peach.bmp' % directory).convert('1')
        self.pizza = Image.open('%s/sprites/food/pizza.bmp' % directory).convert('1')
        self.burger = Image.open('%s/sprites/food/burger.bmp' % directory).convert('1')

        # default sprite
        self.food_sprite = self.peach

        # initial coordinates
        (self.x, self.y) = (50, 31)

        self.spawned = False
    
    def spawn(self, x):
        # choose food item
        food = ['peach', 'pizza', 'burger']
        choice = random.choice(food)
        if choice == 'peach':
            self.food_sprite = self.peach
        elif choice == 'pizza':
            self.food_sprite = self.pizza
        elif choice == 'burger':
            self.food_sprite = self.burger

        # find available position
        pos = random.randint(0, 100)
        if pos not in range(x, x + 32) and pos + 32 not in range(x, x + 32):
            self.x = pos
            self.spawned = True
        else:
            self.spawn(x)

    def eat(self):
        self.spawned = False


## get arguments
args = getArguments()

## initialize screen
RST = None
DC = 16 
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()

## create image
image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)

## initialize font
fontsize = 13
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuS/DejaVuSans.ttf', fontsize)

def main():
    ## animate egg hatching
    if not args.skip:
        egg = Egg()
        while egg.count <= 15:
            egg.idle()
            image.paste(egg.egg_sprite, (egg.x, egg.y))
            disp.image(image)
            disp.display()
            sleep(0.5)
        
        while egg.count <= 21:
            egg.hatch()
            image.paste(egg.egg_sprite, (egg.x, egg.y))
            disp.image(image)
            disp.display()
            sleep(0.5)
    
    
    ## tomo is born!
    tomo = Tomo()
    
    ## create food object
    food = Food()
    
    ## start loop
    try:
        while True:
            draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)
           
            # cpu temp
            temp = cpuTemp(tomo)
            if args.temp:
                draw.text((0, 7), temp, font=font, fill=255)
        
            # time
            if args.time:
                time = datetime.now().strftime('%H:%M')
                draw.text((90, 7), time, font=font, fill=255)
        
            # spotify
            checkSpotify(tomo)
        
        # spawn food
            if not food.spawned:
                if random.randint(0, 20) == 0:
                    food.spawn(tomo.x)
        
            # start walk
            tomo.walk(temp)
            if food.spawned:
                if tomo.x in range(food.x, food.x + 36) or tomo.x + 36 in range(food.x, food.x + 32):
                    tomo.food_consumed = tomo.food_consumed + 1
                    if tomo.x < food.x:
                        tomo.direction = 'right'
                    else:
                        tomo.direction = 'left'
        
                    for count in range(0, 6):
                        draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)
                        draw.text((0, 7), 'food eaten: %s' % str(tomo.food_consumed), font=font, fill=255)
                        tomo.eat(count)
        
                        image.paste(food.food_sprite, (food.x, food.y))
                        image.paste(tomo.tomo_sprite, (tomo.x, tomo.y))
                        disp.image(image)
                        disp.display()
                        sleep(0.5)
                    food.eat()
        
        
            if food.spawned:
                image.paste(food.food_sprite, (food.x, food.y))
            image.paste(tomo.tomo_sprite, (tomo.x, tomo.y))
            disp.image(image)
            disp.display()
            sleep(0.5)
    except KeyboardInterrupt:
        draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)
        draw.text((0, 7), 'tomo terminated :(', font=font, fill=255)
        tomo.tomo_sprite = tomo.tomo_rip
        image.paste(tomo.tomo_sprite, (50, 34))
        disp.image(image)
        disp.display()


def test():
    pass


if __name__ == '__main__':
    main()
