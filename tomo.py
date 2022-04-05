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


def render(object):
    draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)
    if tomo.message:
        draw.text((0, 7), tomo.message, font=font, fill=255)
    else:
        # cpu temp
        if args.temp:
            draw.text((0, 7), tomo.temp, font=font, fill=255)
        
        # time
        if args.time:
            time = datetime.now().strftime('%H:%M')
            draw.text((90, 7), time, font=font, fill=255)

    if food.spawned:
        image.paste(food.sprite, (food.x, food.y))
    image.paste(object.sprite, (object.x, object.y))
    disp.image(image)
    disp.display()
    sleep(0.5)



class Tomo:
    def __init__(self):
        # load sprites
        directory = os.path.dirname(__file__)

        self.tomo = Image.open('%s/sprites/tomo/tomo.bmp' % directory).convert('1')
        self.tomo_sweat = Image.open('%s/sprites/tomo/tomo_sweat.bmp' % directory).convert('1')
        self.tomo_excite = Image.open('%s/sprites/tomo/tomo_excite.bmp' % directory).convert('1')
        self.tomo_eat = Image.open('%s/sprites/tomo/tomo_eat.bmp' % directory).convert('1')
        self.tomo_dance = Image.open('%s/sprites/tomo/tomo_dance.bmp' % directory).convert('1')
        self.tomo_sick = Image.open('%s/sprites/tomo/tomo_sick.bmp' % directory).convert('1')
        self.tomo_love = Image.open('%s/sprites/tomo/tomo_love.bmp' % directory).convert('1')
        self.tomo_rip = Image.open('%s/sprites/tomo/tomo_rip.bmp' % directory).convert('1')

        # default sprite
        self.sprite = self.tomo

        # initial coordinates
        (self.x, self.y) = (50, 34)

        # set direction
        self.direction = 'left'

        # attributes
        self.hot = False
        self.dancing = False
        self.sick = False
        self.hunger = 100
        self.food_consumed = 0
        self.deaths = 0
        self.temp = ''
        self.message = False

    def walk(self):
        self.message = False
        self.checkSick()

        # hunger depleats faster when hot
        if self.hot:
            self.hunger = self.hunger - 2
        else:
            self.hunger = self.hunger - 1

        if self.hunger <= 0:
            self.die()

        # more likely to not move if sick
        # bee lines to food when starving
        if self.hunger > 20:
            if self.sick:
                dir = random.randint(0, 2)
            else:
                dir = random.randint(0, 6)
        elif food.spawned:
            if food.x > self.x:
                dir = 1
            else:
                dir = 2
            if self.sick and random.randint(0,1) == 0:
                dir = 0
        else:
            dir = 0
            
        # do nothing if 0
        if dir == 0:
            pass
        elif dir % 2 == 0:
            self.direction = 'left'
            if self.x > 0:
                self.x = self.x - 2
        else:
            self.direction = 'right'
            if self.x < 98:
                self.x = self.x + 2
        
        if self.hunger < 20:
            self.sprite = self.tomo_excite
        elif self.sick:
            self.sprite = self.tomo_sick
        elif self.dancing:
            self.sprite = self.tomo_dance
        elif self.hot:
            self.sprite = self.tomo_sweat
        else:
            self.sprite = self.tomo

        if self.direction == 'right':
            tomo.sprite = tomo.sprite.transpose(Image.FLIP_LEFT_RIGHT)

        if self.x % 3 == 0:
            self.y = 32
        else:
            self.y = 34

        render(self)

    def eat(self):
        self.hunger = 200
        self.food_consumed = self.food_consumed + 1
        self.message = 'food eaten: %s' % (str(self.food_consumed))
        for count in range(0, 6):
            if count % 2 == 0:
                self.sprite = self.tomo_excite
            else:
                self.sprite = self.tomo_eat
            if self.direction == 'right':
                self.sprite = self.sprite.transpose(Image.FLIP_LEFT_RIGHT)
            render(self)

    def checkSick(self):
        if self.sick:
            sick = random.randint(0,10)
            if sick == 0:
                self.sick = False
        else:
            sick = random.randint(0, 31)
            if sick == 0:
                self.sick = True

    def checkTemp(self):
        command = '/opt/vc/bin/vcgencmd measure_temp'
        temp = subprocess.check_output(command, shell=True)
        temp = temp.decode()
        temp = temp[:9]
        temp = temp[5:]
        if float(temp) >= 50.0:
            self.hot = True
        else:
            self.hot = False
        self.temp = temp + ' C'

    def checkMusic(self):
        command = '/usr/bin/ps -aux | /usr/bin/grep ncspot | /usr/bin/wc -l'
        output = subprocess.check_output(command, shell=True)
        output.decode()
        if int(output) >= 3:
            self.dancing = True
        else:
            self.dancing = False
     
    def die(self):
        self.deaths = self.deaths + 1
        self.sprite = self.tomo_rip
        food.spawned = False

        self.message = 'times died: %s' % str(self.deaths)

        render(self)
        sleep(10)
        self.respawn()

        sleep(10)

        self.respawn()

    def respawn(self):
        self.hunger = 100
        self.food_consumed = 0
        main()


class Egg:
    def __init__(self):
        # load sprites
        directory = os.path.dirname(__file__)
        self.egg1 = Image.open('%s/sprites/egg/egg1.bmp' % directory).convert('1')
        self.egg2 = Image.open('%s/sprites/egg/egg2.bmp' % directory).convert('1')
        self.egg3 = Image.open('%s/sprites/egg/egg3.bmp' % directory).convert('1')

        # default sprite
        self.sprite = self.egg1

        # initial coordinates
        (self.x, self.y) = (50, 34)

        self.count = 0

    def hatch(self):
        while self.count <= 15:
            if self.count % 2 == 0:
                self.sprite = self.egg1
            else:
                self.sprite = self.egg2
            
            self.count = self.count + 1
            render(self)
        
        while self.count <= 21:
            if self.count % 2 == 0:
                self.sprite = self.egg1
            else:
                self.sprite = self.egg3
            
            self.count = self.count + 1
            render(self)


class Food:
    def __init__(self):
        # load sprites
        directory = os.path.dirname(__file__)
        self.peach = Image.open('%s/sprites/food/peach.bmp' % directory).convert('1')
        self.pizza = Image.open('%s/sprites/food/pizza.bmp' % directory).convert('1')
        self.burger = Image.open('%s/sprites/food/burger.bmp' % directory).convert('1')
        self.mush = Image.open('%s/sprites/food/mush.bmp' % directory).convert('1')

        # default sprite
        self.sprite = self.peach

        # initial coordinates
        (self.x, self.y) = (50, 31)

        self.spawned = False
    
    def spawn(self, x):
        # choose food item
        food = ['peach', 'pizza', 'burger', 'mush']
        choice = random.choice(food)
        if choice == 'peach':
            self.sprite = self.peach
        elif choice == 'pizza':
            self.sprite = self.pizza
        elif choice == 'burger':
            self.sprite = self.burger
        elif choice == 'mush':
            self.sprite = self.mush

        # find available position
        pos = random.randint(0, 100)
        if pos not in range(tomo.x, tomo.x + 32) and pos + 32 not in range(tomo.x, tomo.x + 32):
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

tomo = Tomo()
food = Food()
def main():
    ## animate egg hatching
    if not args.skip:
        egg = Egg()
        egg.hatch()

    ## start loop
    while True:
        tomo.checkMusic()
        tomo.checkSick()
        tomo.checkTemp()

        # spawn food
        if not food.spawned:
            if random.randint(0, 50) == 0:
                food.spawn(tomo.x)
    
        # start walk
        tomo.walk()
        if food.spawned:
            if tomo.x in range(food.x, food.x + 36) or tomo.x + 36 in range(food.x, food.x + 32):
                if tomo.x < food.x:
                    tomo.direction = 'right'
                else:
                    tomo.direction = 'left'
    
                tomo.eat()
                food.eat()


if __name__ == '__main__':
    main()
