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

    args = parser.parse_args()
    return args


def cpuTemp():
    command = '/opt/vc/bin/vcgencmd measure_temp'
    temp = subprocess.check_output(command, shell=True)
    temp = temp.decode()
    temp = temp[:9]
    temp = temp[5:]
    return temp


class Tomo:
    def __init__(self):
        directory = os.path.dirname(__file__)
        # load sprites
        self.tomo_left = Image.open('%s/sprites/tomo.bmp' % directory).convert('1')
        self.tomo_right = self.tomo_left.transpose(Image.FLIP_LEFT_RIGHT)
        self.tomo_left_sweat = Image.open('%s/sprites/tomo_sweat.bmp' % directory).convert('1')
        self.tomo_right_sweat = self.tomo_left_sweat.transpose(Image.FLIP_LEFT_RIGHT)

        # default sprite
        self.tomo_sprite = self.tomo_left

        # initial coordinates
        self.x = 50
        self.y = 34

    def walk(self, temp):
        dir = random.randint(0, 6)
        if dir == 0:
            pass
        elif dir % 2 == 1:
            if float(temp) > 50.0:
                self.tomo_sprite = self.tomo_left_sweat
            else:
                self.tomo_sprite = self.tomo_left
            if self.x > 0:
                self.x = self.x - 2
        elif dir % 2 == 0:
            if float(temp) > 50.0:
                self.tomo_sprite = self.tomo_right_sweat
            else:
                self.tomo_sprite = self.tomo_right
            if self.x < 100:
                self.x = self.x + 2
        
        if self.x % 3 == 0:
            self.y = 32
        else:
            self.y = 34


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


## tomo is born!
tomo = Tomo()

## start loop
while True:
    draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)
   
    # cpu temp
    temp = cpuTemp()
    if args.temp:
        temp_string = temp + ' C'
        draw.text((0, 7), temp_string, font=font, fill=255)

    # time
    if args.time:
        time = datetime.now().strftime('%H:%M')
        draw.text((90, 7), time, font=font, fill=255)

    # start walk
    tomo.walk(temp)
    

    image.paste(tomo.tomo_sprite, (tomo.x, tomo.y))
    disp.image(image)
    disp.display()
    sleep(0.5)
