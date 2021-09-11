from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

time.sleep(2)

steps = 270

while steps <= 38400:
    keyboard.press('s')
    time.sleep(0.8)
    keyboard.release('s')
    steps += 5
    print(steps)
    keyboard.press('w')
    time.sleep(0.8)
    keyboard.release('w')
    steps += 5
    print(steps)
