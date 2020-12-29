import pyautogui
import cv2
import keyboard as kb
import numpy as np


# screen resolution of the machine
screenSize = pyautogui.size()
# print(screenSize)

# manually point the components' position on screen in x|y format
def get_m_pos():
    m_pos = pyautogui.position()
    print(m_pos)

hot_area = {
    'pay_btn': {'x': 1502, 'y': 922, 'w': 405, 'h': 50},
    'pay_done': {'x': 1502, 'y': 115, 'w': 405, 'h': 88},
    'pay_failed': {'x': 1502, 'y': 160, 'w': 405, 'h': 180},
    'pay_order': {'x': 1502, 'y': 90, 'w': 405, 'h': 52}

}
# find clicking positions by sample image

def create_samples():
    global hot_area
    _x = hot_area['pay_order']['x']
    _y = hot_area['pay_order']['y']
    _w = hot_area['pay_order']['w']
    _h = hot_area['pay_order']['h']
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