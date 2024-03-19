import time
from pynput import mouse, keyboard
import csv

# initialize csv
with open('mouse_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['record timestamp', 'client timestamp', 'button', 'state', 'x', 'y'])

# global flag
listening = False

def on_move(x, y):
    if listening:
        with open('mouse_data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.time(), time.time(), 'NoButton', 'Move', x, y])

def on_click(x, y, button, pressed):
    if listening:
        with open('mouse_data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            state = 'Pressed' if pressed else 'Released'
            writer.writerow([time.time(), time.time(), button, state, x, y])

def on_scroll(x, y, dx, dy):
    if listening:
        with open('mouse_data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.time(), time.time(), 'NoButton', 'Scroll', x, y])

def on_press(key):
    global listening
    try:
        if key == keyboard.Key.f2:  # F2 to start
            listening = True
            print("listening started...")
        elif key == keyboard.Key.f3:  # F3 to stop
            listening = False
            print("listening canceled. ")
    except AttributeError:
        pass

# start listening
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()
keyboard_listener.join()
mouse_listener.join()