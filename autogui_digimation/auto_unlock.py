import pyautogui
import time

# The position that will always be the newest object after pressing 'down', get that by "pyautogui.position()" at that position
magic_pos_x     = 517
magic_pos_y     = 389

# Change of position for unlocking after right click
delta_x         = 5
delta_y         = 5

def unlock_next():
    pyautogui.moveTo(magic_pos_x, magic_pos_y)
    pyautogui.rightClick()
    pyautogui.moveTo(magic_pos_x +5, magic_pos_y +5)
    pyautogui.click()
    pyautogui.press('down')

# Some time to prepare, change to the window needed
time.sleep(5)

do_times    = 1000
for indx in xrange(do_times):
    unlock_next()
