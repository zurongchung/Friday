import pyautogui
import cv2
import keyboard as kb
import numpy as np


# screen resolution of the machine
screenSize = pyautogui.size()
print(screenSize)

init_pos = {'x': 728.5, 'y': 52}

def get_init_coords():
    """
    defines the initial coordinates by clicking on screen with mouse
    """
    pass

am_width = screenSize.width - (init_pos['x'] * 2)
am_height = screenSize.height - init_pos['y']
samples_width = 405
margin_x = (am_width - samples_width) / 2
print(am_width, am_height, samples_width, margin_x)
# manually point the components' position on screen in x|y format
def get_m_pos():
    m_pos = pyautogui.position()
    print(m_pos)

hot_area = {
    'pay_btn': {'x': init_pos['x'], 'y': 978, 'w': am_width, 'h': 102},
    'pay_pwd': {'x': init_pos['x'], 'y': 325, 'w': am_width, 'h': 262},
    'pay_keypad': {'x': init_pos['x'], 'y': 825, 'w': am_width, 'h': 255},
    'pay_done': {'x': init_pos['x'], 'y':88, 'w': am_width, 'h': 88},
    'pay_failed': {'x': init_pos['x'], 'y': 160, 'w': am_width, 'h': 220},
    'pay_scan': {'x': init_pos['x'], 'y': 92, 'w': am_width, 'h': 52},
    'pay_services': {'x': init_pos['x'], 'y': 92, 'w': am_width, 'h': 52},
    'pay_scan_failed': {'x': (init_pos['x'] + 45), 'y': 477, 'w': (am_width - 45*2), 'h': 212}

}
# find clicking positions by sample image

def create_samples():
    global hot_area
    _x = hot_area['pay_scan_failed']['x']
    _y = hot_area['pay_scan_failed']['y']
    _w = hot_area['pay_scan_failed']['w']
    _h = hot_area['pay_scan_failed']['h']
    _shoot = pyautogui.screenshot(region=(_x, _y, _w, _h))
    _gray = cv2.cvtColor(np.array(_shoot), cv2.COLOR_RGB2BGR)
    cv2.imwrite('samples/pay_sample_color.png', _gray)
    print('@test: sample created.')

def init():

    kb.add_hotkey('p', get_m_pos)
    kb.add_hotkey('s', create_samples)
    kb.wait('backspace')

if __name__ == "__main__":
    init()