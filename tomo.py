#!/usr/bin/env python3

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import argparse
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

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0, width, height), outline=0, fill=0)

fontsize = 13
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuS/DejaVuSans.ttf', fontsize)

## load images
directory = os.path.dirname(__file__)
tomo_left = Image.open('%s/sprites/tomo_left.bmp' % directory).convert('1')
tomo_right = Image.open('%s/sprites/tomo_right.bmp' % directory).convert('1')
tomo_left_sweat = Image.open('%s/sprites/tomo_left_sweat.bmp' % directory).convert('1')
tomo_right_sweat = Image.open('%s/sprites/tomo_right_sweat.bmp' % directory).convert('1')

## set initial position
(x, y) = (50, 34)

## start walk
while True:
    draw.rectangle((0,0, width, height), outline=0, fill=0)
    
    # cpu temp
    temp = cpuTemp()
    if args.temp:
        temp_string = temp + ' C'
        draw.text((0, 7), temp_string, font=font, fill=255)

    dir = random.randint(0, 6)
    if dir == 0:
        pass
    elif dir % 2 == 1:
        if float(temp) > 50.0:
            tomo = tomo_left_sweat
        else:
            tomo = tomo_left
        if x > 0:
            x = x - 2
    elif dir % 2 == 0:
        if float(temp) > 50.0:
            tomo = tomo_right_sweat
        else:
            tomo = tomo_right
        if x < 100:
            x = x + 2
    
    if x % 3 == 0:
        y = 32
    else:
        y = 34

    image.paste(tomo, (x, y))
    disp.image(image)
    disp.display()
    sleep(0.5)
