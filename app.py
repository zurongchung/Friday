import os
import sys
import time
import cv2
import keyboard as kb
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import qrcode
import tkinter
from PIL import ImageTk, Image
from skimage.metrics import structural_similarity as ssim
import threading
import subprocess

# print(kb.key_to_scan_codes('1'))
# home_for_scan = cv2.imread('samples/home.png')
# home_for_scan = cv2.cvtColor(home_for_scan, cv2.COLOR_BGR2GRAY)

# !!current not using it!!
# @var budget: 
#   > end program when ran out of budget
#   > assigned through terminal argument
budget = 10
# @var stock:
#   > end program when there is no more links
stock = 0
def set_stock(_data):
    """
    @param _data: []
    return the length of the list
    """
    return len(_data)
# @var on_hold_links:
#   > stores a list of payment links that took too long to respond
#   > for try again later
on_hold_links = []
# @var tracker_id:
#   > keep tracking of which payment is in progress
tracker_id = 0
# @var signal:
#   > controls the state (running | ending) of this program
signal = True
# password for payment
secert_pwd = ''
# stores the initial position return to it when the job is finished
data = []
quantity = 0
d_index = 0
# controls the thread that generating qr codes
qr_gen_status = True
# samples in the samples folder
sample_pay_btn = None
sample_scan_btn = None
sample_scan_failed_btn = None
sample_done_btn = None
sample_services_page = None
sample_failed_symble = None
sample_pwd_page = None
sample_keypad_page  = None


# screen resolution of the machine
screenSize = pyautogui.size()
# print(screenSize)

init_pos = {'x': 728.5, 'y': 52}

def get_init_coords():
    """
    defines the initial coordinates by clicking on screen with mouse
    """
    pass

am_width = screenSize.width - (init_pos['x'] * 2)
am_height = screenSize.height - init_pos['y']
# samples_width = 405
margin_x = 22

hot_area = {
    'pay_btn': {'x': init_pos['x'], 'y': 978, 'w': am_width, 'h': 102},
    'pay_pwd': {'x': init_pos['x'], 'y': 325, 'w': am_width, 'h': 262},
    'pay_keypad': {'x': init_pos['x'], 'y': 825, 'w': am_width, 'h': 255},
    'pay_done': {'x': init_pos['x'], 'y':88, 'w': am_width, 'h': 88},
    'pay_failed': {'x': init_pos['x'], 'y': 160, 'w': am_width, 'h': 220},
    'pay_services': {'x': init_pos['x'], 'y': 92, 'w': am_width, 'h': 52},
    'pay_scan': {'x': init_pos['x'], 'y': 92, 'w': am_width, 'h': 52},
    'pay_scan_failed': {'x': (init_pos['x'] + 45), 'y': 477, 'w': (am_width - 45*2), 'h': 212}

}

mouse_pos = {
    'pay': {'x': (init_pos['x'] + am_width / 2), 'y': 982},
    'payment_done': {'x':(init_pos['x'] + am_width - margin_x), 'y': (88 + 88 /2)},
    'payment_failed': {'x': 1118, 'y': 114},
    'scan': {'x': (init_pos['x'] + am_width - margin_x), 'y': 114},
    'scan_failed': {'x': (hot_area['pay_scan_failed']['x'] + hot_area['pay_scan_failed']['w'] / 2),
    'y': (hot_area['pay_scan_failed']['y'] + hot_area['pay_scan_failed']['h'] * 3/4)}
}

def mse(imgA, imgB):
    err = np.sum((imgA.astype('float') - imgB.astype('float')) ** 2)
    err /= float(imgA.shape[0] * imgB.shape[1])
    return err

def cmp_img(imgA, imgB):
    s = ssim(imgA, imgB)
    return s

# s = mse(home_for_scan, g_obj_img)

# -----------------------------------------------------------------

def init():
    global data, d_index, secert_pwd, sample_pay_btn, sample_scan_btn, sample_done_btn, sample_failed_symble, sample_services_page, sample_pwd_page, sample_scan_failed_btn

    secert_pwd = input('please provide your password for the payment...\n>>> ')
    print('@test: password is: %s' % secert_pwd)
    init_data()
    load_samples()
    # manually actions
    kb.add_hotkey('right', prepare_qrcodes)
    kb.add_hotkey('q', scan)
    kb.add_hotkey('space', press_pay_btn)
    kb.add_hotkey('w', close)
    kb.add_hotkey('e', common_close_action)
    kb.add_hotkey('m', end_thread)
    kb.add_hotkey('r', reload_data)
    t0 = threading.Thread(target= vision_autobot, 
        args=(sample_scan_btn, hot_area['pay_scan'], scan, 'watching scan button'))
    # t1 = threading.Thread(target= vision_autobot, 
    #     args=(sample_pay_btn, hot_area['pay_btn'], press_pay_btn, 'watching pay button'))
    # t2 = threading.Thread(target= vision_autobot, 
    #     args=(sample_done_btn, hot_area['pay_done'], close, 'watching done pay activity'))
    t3 = threading.Thread(target= vision_autobot, 
        args=(sample_failed_symble, hot_area['pay_failed'], common_close_action, 'watching failed activity'))
    t4 = threading.Thread(target= prepare_qrcodes)
    t5 = threading.Thread(target= vision_autobot, 
        args=(sample_services_page, hot_area['pay_services'], common_close_action, 'watching services activity'))
    # t6 = threading.Thread(target= vision_autobot, 
    #     args=(sample_pwd_page, hot_area['pay_pwd'], enter_sec_keys, 'watching password activity'))
    t7 = threading.Thread(target= vision_autobot, 
        args=(sample_scan_failed_btn, hot_area['pay_scan_failed'], scan_failed, 'watching scan failed result'))

    t0.start()
    # t1.start()
    # t2.start()
    t3.start()
    t4.start()
    t5.start()
    # t6.start()
    t7.start()

    print('@test: application now functioning!')
    kb.wait('backspace')
    t0.join()
    # t1.join()
    # t2.join()
    t3.join()
    t4.join()
    t5.join()
    # t6.join()
    t7.join()

def reload_data():
    init_data()
    print('@test: data reload successfully.')

def init_data():
    global data, d_index, quantity
    data = read_data()
    quantity = len(data)
    d_index = quantity -1
    print("@test: finished loading data. Total of || %i || " % quantity)

def read_data():
    url = []
    print('@test: Fetching data...')
    with open('db/data.txt', 'r') as _data:
        url = _data.readlines()
    return url

def end_thread():
    global signal
    signal = False

def load_samples():
    global sample_pay_btn, sample_scan_btn, sample_done_btn, sample_failed_symble, sample_services_page, sample_pwd_page, sample_keypad_page, sample_scan_failed_btn 
    # load the samples into memory
    print('@test: loading samples into memory...')
    sample_pay_btn =  cv2.cvtColor(cv2.imread('samples/type2/pay_btn_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_scan_btn =  cv2.cvtColor(cv2.imread('samples/type2/pay_scan_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_scan_failed_btn =  cv2.cvtColor(cv2.imread('samples/type2/pay_scan_failed_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_done_btn =  cv2.cvtColor(cv2.imread('samples/type2/pay_done_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_pwd_page =  cv2.cvtColor(cv2.imread('samples/type2/pay_pwd_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_keypad_page =  cv2.cvtColor(cv2.imread('samples/type2/pay_keypad_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_failed_symble =  cv2.cvtColor(cv2.imread('samples/type2/pay_failed_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_services_page =  cv2.cvtColor(cv2.imread('samples/type2/pay_services_color.png'), cv2.COLOR_BGR2GRAY) 

# @todo when [frequency is too fast clicking wrong position will happen]
def vision_autobot(target, area, callback, msg, accuracy=0.94, frequency=0.1):
    """
    constantly take screenshot on defined area and take that to
    matching the sample image.
    when the matching result is higher than the accuracy then
    call the callback function to take some actions
    @param target:
        the sample images provided for the matching
    @param area:
        defined spot for the thread to watching
    @param callback:
        called when the matching is found
    @parm msg:
        some message to display when the founction called
    @param accuracy:
        define how accurate the matching result should be
        in order to become a positive match
    """
    global signal
    print('@test: vision thread %s started!!' % msg)
    _x = area['x']
    _y = area['y']
    _w = area['w']
    _h = area['h']

    _accuracy = accuracy
    _freq = frequency
    _sample_gray = target
    while signal:
        _target = pyautogui.screenshot(region=(_x, _y, _w, _h))
        _target_gray = cv2.cvtColor(np.array(_target), cv2.COLOR_BGR2GRAY)
        _m = cmp_img(_sample_gray, _target_gray)

        if _m > _accuracy:
            print('@test: similarity: %0.2f' % _m)
            callback()
            # sleep 1 second when matched
            _freq = 1

        time.sleep(_freq)
        # reset
        _freq = frequency
    print('@test: vision thread %s ended.' % msg)

def prepare_qrcodes():
    global data, d_index, qr_gen_status, signal
    _link = data[d_index]

    while signal:
        if qr_gen_status:
            if d_index < 0:
                # No more Jobs entering hibernation mode
                qr_gen_status = False
                print('@test: No more data!!')
            else:
                if not _link or _link.isspace():
                    pass
                else:
                    # scan()
                    img = gen_qr(_link)
                    img.show()
                    print('@test: preparing QRcode number %i' % d_index)
                    d_index -= 1
                    qr_gen_status = False
        time.sleep(1)

def gen_qr(url):
    """ 
    @param url: data for the qr code
    generating qr code for the provided url
    """
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=3,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def press_pay_btn():
    global qr_gen_status

    print('@test: pressing the pay button')
    # when it sees the pay button
    # then click on it
    pyautogui.moveTo(mouse_pos["pay"]["x"], mouse_pos["pay"]['y'])
    pyautogui.click()
    # the old qr code has been used dismiss it
    collapse_photo()
    # telling the thread to prepare the new qr code for scanning
    qr_gen_status = True
    # wait for a bit in case passwords input activity haven't showup
    # time.sleep(0.1)

def enter_sec_keys():
    global secert_pwd

    print('@test: Entering secret keys for payment')
    _sec_key = secert_pwd
    # input passwords
    print('@test: entering password %s' % _sec_key)
    # for _mos_p in _sec_key:
        # Entering the keys
        # pyautogui.press(_mos_p)
        # print(_mos_p)

def scan():
    pyautogui.moveTo(x=mouse_pos['scan']['x'], y=mouse_pos['scan']['y'])
    pyautogui.click()
    print('@test: start scanning')

def scan_failed():
    pyautogui.moveTo(x=mouse_pos['scan_failed']['x'], y=mouse_pos['scan_failed']['y'])
    pyautogui.click()
    print('@test: dismiss failed scan result')

def close():
    pyautogui.moveTo(x=mouse_pos['payment_done']['x'], y=mouse_pos['payment_done']['y'])
    pyautogui.click()
    print('@test: close done page')
    time.sleep(0.2)
    common_close_action()

def common_close_action():
    pyautogui.moveTo(x=mouse_pos['payment_failed']['x'], y=mouse_pos['payment_failed']['y'])
    pyautogui.click()
    print('@test: press on common close button')

def collapse_photo():
    # close the previous qrcode window
    # pyautogui.moveTo(x=645, y=69)
    # pyautogui.click()
    try:
        subprocess.call(['taskkill', '/F', '/IM', 'Microsoft.Photos.exe'])
    except Exception as err:
        pass

# -----------------------------------------------------------------

if __name__ == "__main__":
    init()