#!/usr/bin/env python3

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import os
import random
import subprocess
from time import sleep

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

directory = os.path.dirname(__file__)
tomo_left = Image.open('%s/sprites/tomo_left.bmp' % directory).convert('1')
tomo_right = Image.open('%s/sprites/tomo_right.bmp' % directory).convert('1')

(x, y) = (50, 34)


def cpuTemp():
    command = '/opt/vc/bin/vcgencmd measure_temp'
    temp = subprocess.check_output(command, shell=True)
    temp = temp.decode()
    temp = temp[:9]
    temp = temp[5:]
    temp = temp + ' C'
    return temp


while True:
    draw.rectangle((0,0, width, height), outline=0, fill=0)
    
    # cpu temp
    temp = cpuTemp()
    draw.text((0, 7), temp, font=font, fill=255)

    dir = random.randint(0, 6)
    if dir == 0:
        pass
    elif dir % 2 == 1:
        tomo = tomo_left
        if x > 0:
            x = x - 2
    elif dir % 2 == 0:
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
