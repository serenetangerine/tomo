from machine import ADC, Pin, I2C
from ssd1306 import SSD1306_I2C
from framebuf import FrameBuffer, MONO_HLSB

from random import randint
from time import sleep

try:
    from battery import Battery
    bat = Battery(1)
except Exception as e:
    print('could not find battery module, skipping...')



def load_sprite(file, size):
    with open(file, 'rb') as f:
        # skip over metadata
        for i in range(3):
            f.readline()
        data = bytearray(f.read())
        return FrameBuffer(data, size, size, MONO_HLSB)

def debug():
    import gc
    gc.collect()
    mem = 1 - (gc.mem_free() / 270336)
    print(str(mem))


class Tomo:
    def __init__(self):
        # default tick rate for basic movements
        self.tick_rate = 0.1

        # load sprites
        # TODO: figure out the matrix operation to mirror a matrix accross the vertical axis to avoid extra sprites
        self.tomoR = load_sprite('sprites/tomor.pbm', 32)
        self.tomoL = load_sprite('sprites/tomol.pbm', 32)
        
        self.heartFull = load_sprite('sprites/heart-full.pbm', 16)
        self.heartHalf = load_sprite('sprites/heart-half.pbm', 16)
        self.heartEmpty = load_sprite('sprites/heart-empty.pbm', 16)

        self.dead = load_sprite('sprites/dead.pbm', 32)

        self.egg1 = load_sprite('sprites/egg1.pbm', 32)
        self.egg2 = load_sprite('sprites/egg2.pbm', 32)
        self.egg3 = load_sprite('sprites/egg3.pbm', 32)
        
        # set default position
        self.x = randint(0,96) 
        self.y = 32

        self.high_score = 0
        self.health = -1
        self.spawn()

    def spawn(self):
        self.dir = 1
        self.food_spawned = False
        self.score = 0

        # egg spawn animation
        for i in range(9):
            self.health = self.health + 1
            if i % 2 == 0:
                self.sprite = self.egg1
            else:
                self.sprite = self.egg2
            self.render()
        # flash forimminent hatching
        for i in range(7):
            if i % 2 == 0:
                self.sprite = self.egg3
            else:
                self.sprite = self.egg1
            self.render()
        
        # tomo is born!!
        self.sprite = self.tomoR

    def walk(self):
        # food motivation
        # tomo will always move towards food if it exists
        if self.food_spawned:
            if self.food_x > self.x:
                self.dir = 0
                if self.food_x <= self.x + 32:
                    self.eat()
            else:
                self.dir = 1
                if self.x - 17 <= self.food_x:
                    self.eat()
        else:
            # if no food, choose a random direction
            self.dir = randint(0, 1)
        
        if self.dir == 0:
            # make sure tomo doesn't get stuck trying to walk into a wall
            # this way he will potentially dance back and forth at walls tho
            if self.x <= 96:
                self.sprite = self.tomoL
                self.x = self.x + 2
        else:
            # same wall detection but for the other direction
            if self.x >= 0:
                self.sprite = self.tomoR
                self.x = self.x - 2
        # give tomo the appearance of little hops
        if self.x % 3 == 0:
            self.y = 30
        else:
            self.y = 32 
        
        # check if tomo loses health, if food spawns, then render the tick
        self.roll_health(15)
        self.roll_food(12)
        self.render()

    def eat(self):
        self.food_spawned = False
        self.score = self.score + 1
        if self.health <= 6:
            self.health = self.health + 2
        else:
            # cap at full health so tomo doesn't have the potential to be immortal
            self.health = 8

    def roll_health(self, max):
        if randint(0, max) == 0:
            self.health = self.health - 1

    def roll_food(self, max):
        if not self.food_spawned:
            if randint(0, max) == 0:
                self.food_x = randint(0, 112)
                if self.food_x not in range(self.x, self.x + 32) and self.food_x + 16 not in range(self.x, self.x + 32):
                    self.food_spawned = True
                else:
                    print('could not spawn food')

    def render_food(self):
        if self.food_spawned:
            oled.blit(self.heartFull, self.food_x, 42)

    def render_hearts(self):
        for i in range(4):
            if self.health >= (i + 1) * 2:
                sprite = self.heartFull
            elif self.health >= i * 2 and self.health % 2 == 1:
                sprite = self.heartHalf
            else:
                sprite = self.heartEmpty
            oled.blit(sprite, 64 + (i * 13), 0)

    def render(self):
        oled.fill(0)

        # render tomo
        oled.blit(self.sprite, self.x, self.y)
        
        # render top row of the HUD
        self.render_hearts()
        self.render_food()

        # write score and highscore if it exists
        oled.text(str(self.score), 0, 3)
        if self.high_score > 0:
            oled.text(str(self.high_score), 23, 3)
        
        # write second row of the HUD if there is a battery
        if bat:
            oled.text('%.2f' % float(bat.uptime / (60 * 60)), 0 , 18)
            oled.text('%s%%' % str(int(bat.percentage)), 84, 18)
        
        oled.show()
        sleep(self.tick_rate)



# turn on LED so we know the pico is powered on
#led = Pin(25, Pin.OUT)
#led.on()

# initialize screen
width = 128
height = 64

i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
oled = SSD1306_I2C(width, height, i2c)

# initialize Tomo and start loop
tomo = Tomo()
while True:
    # TODO: have this logic check as part of the class for cleanliness
    #
    # will need to refactor some code to get the game down to a basic tick logic
    # and just trigger the walk sequence and rendering to the screen at a tick level
    #
    # this would allow the class Tomo to be imported into other scripts directly and
    # control a screen if not used by the other script (used for custom keyboards?)
    #
    # this would also allow for the potential to daemonize the game ticks to allow for
    # easy button input loops for furture content updates

    debug()

    if tomo.health > 0:
        tomo.walk()
    else:
        tomo.sprite = tomo.dead
        if tomo.score > tomo.high_score:
            tomo.high_score = tomo.score
        tomo.render()
        sleep(tomo.tick_rate * 6)
        tomo.spawn()
        
