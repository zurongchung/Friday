import pyautogui
import keyboard as kb

# screen resolution of the machine
screenSize = pyautogui.size()
print(screenSize)

# manually point the components' position on screen in x|y format
def get_m_pos():
    m_pos = pyautogui.position()
    print(m_pos)

def create_samples():
    pyautogui.click(x=918, y=126)
    for i in '123456':
        pyautogui.press(i, interval=0.001)

def init():

    kb.add_hotkey('p', get_m_pos)
    kb.add_hotkey('s', create_samples)
    kb.wait('backspace')

if __name__ == "__main__":
    init()