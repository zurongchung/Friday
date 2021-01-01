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
import json
import copy
from pynput.mouse import Button, Listener

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

# config
config_dict = dict()
config_json = 'samples_config.json'


# ideal_marker = config_dict['main']['marker']
ideal_marker = {}
current_marker =  {}
hot_area = {}
mouse_pos = {}
delta = {'x': 0, 'y': 0}

def get_marker(x, y, button, pressed):
    global current_marker
    if button == Button.left and pressed:
        current_marker = {'x': x, 'y': y}
        print('current marker: %s' % current_marker)
        return False

def mount_marker_listener():
    _listener = Listener(on_click=get_marker)
    _listener.start()
    print('marker listener started.')
    print('click on the top left corner of the app.')
    kb.wait('p')

def cal_delta():
    global ideal_marker, current_marker, delta
    mount_marker_listener()

    _dx = current_marker['x'] - ideal_marker['x']
    _dy = current_marker['y'] - ideal_marker['y']
    delta = {'x': _dx, 'y': _dy}
    print('delta: ',  delta)

def init_coords():
    global hot_area, mouse_pos, config_dict, delta

    hot_area = {
        'pay_btn': {'x': (config_dict['main']['pay_btn']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_btn']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_btn']['region']['w'], 'h': config_dict['main']['pay_btn']['region']['h']},
        'pay_pwd': {'x': (config_dict['main']['pay_pwd']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_pwd']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_pwd']['region']['w'], 'h': config_dict['main']['pay_pwd']['region']['h']},
        # 'pay_keypad': {'x': (config_dict['main']['pay_keypad']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_keypad']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_keypad']['region']['w'], 'h': config_dict['main']['pay_keypad']['region']['h']},
        'pay_done': {'x': (config_dict['main']['pay_done']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_done']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_done']['region']['w'], 'h': config_dict['main']['pay_done']['region']['h']},
        'pay_failed': {'x': (config_dict['main']['pay_failed']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_failed']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_failed']['region']['w'], 'h': config_dict['main']['pay_failed']['region']['h']},
        'pay_services': {'x': (config_dict['main']['pay_services']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_services']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_services']['region']['w'], 'h': config_dict['main']['pay_services']['region']['h']},
        'pay_scan': {'x': (config_dict['main']['pay_scan']['region']['x'] + delta['x']), 'y': (config_dict['main']['pay_scan']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_scan']['region']['w'], 'h': config_dict['main']['pay_scan']['region']['h']},
        # 'pay_scan_failed': {'x': (config_dict['main']['pay_scan_failed']['region']['x'], 'y': (config_dict['main']['pay_scan_failed']['region']['y'] + delta['y']), 'w': config_dict['main']['pay_scan_failed']['region']['w'], 'h': config_dict['main']['pay_scan_failed']['region']['h']}

    }

    print('original: %s' % config_dict['main']['pay_scan']['region']['x'])
    _dlt = config_dict['main']['pay_scan']['region']['x'] + delta['x']
    print('has been moved: %s' % _dlt)

    mouse_pos = {
        'pay': {'x': (config_dict['main']['pay_btn']['zoom']['x'] + delta['x']), 'y': (config_dict['main']['pay_btn']['zoom']['y'] + delta['y'])},
        'payment_done': {'x': (config_dict['main']['pay_done']['zoom']['x'] + delta['x']), 'y': (config_dict['main']['pay_done']['zoom']['y'] + delta['y'])},
        'payment_failed': {'x': (config_dict['main']['pay_failed']['zoom']['x'] + delta['x']), 'y': (config_dict['main']['pay_failed']['zoom']['y'] + delta['y'])},
        'scan': {'x': (config_dict['main']['pay_scan']['zoom']['x'] + delta['x']), 'y': (config_dict['main']['pay_scan']['zoom']['y'] + delta['y'])},
        # 'scan_failed': {'x': (config_dict['main']['pay_scan_failed']['zoom']['x'] + delta['x']), 'y': (config_dict['main']['pay_scan_failed']['zoom']['y'] + delta['y'])}
        'pay_services': {'x': (config_dict['main']['pay_services']['zoom']['x'] + delta['x']), 'y': (config_dict['main']['pay_services']['zoom']['y'] + delta['y'])}
    }

def load_samples():
    global sample_pay_btn, sample_scan_btn, sample_done_btn, sample_failed_symble, sample_services_page, sample_pwd_page, sample_keypad_page, sample_scan_failed_btn 
    # load the samples into memory
    print('@test: loading samples into memory...')

    sample_pay_btn =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_btn']['img']), cv2.COLOR_BGR2GRAY) 
    sample_scan_btn =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_scan']['img']), cv2.COLOR_BGR2GRAY) 
    # sample_scan_failed_btn =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_scan_failed']['img']), cv2.COLOR_BGR2GRAY) 
    sample_done_btn =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_done']['img']), cv2.COLOR_BGR2GRAY) 
    sample_pwd_page =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_pwd']['img']), cv2.COLOR_BGR2GRAY) 
    # sample_keypad_page =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_keypad']['img']), cv2.COLOR_BGR2GRAY) 
    sample_failed_symble =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_failed']['img']), cv2.COLOR_BGR2GRAY) 
    sample_services_page =  cv2.cvtColor(cv2.imread(config_dict['main']['pay_services']['img']), cv2.COLOR_BGR2GRAY) 


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
    global data, config_dict, ideal_marker, current_marker, d_index, secert_pwd, sample_pay_btn, sample_scan_btn, sample_done_btn, sample_failed_symble, sample_services_page, sample_pwd_page, sample_scan_failed_btn
    
    with open(config_json, 'r') as file:
        config_dict = json.load(file)
    
    # ideal_marker = config_dict['main']['marker']
    # # default to equal if we skip the get marker stage
    # current_marker = ideal_marker

    # cal_delta()

    init_coords()
    init_data()
    load_samples()

    # manually actions
    kb.add_hotkey('m', end_thread)
    kb.add_hotkey('r', reload_data)

    secert_pwd = input('please provide your password for the payment...\n>>> ')
    # print('@test: password is: %s' % secert_pwd)

    _thread_pool = create_monitor_threads()
    t9 = threading.Thread(target= prepare_qrcodes)
    t9.start()
    _thread_pool.append(t9)
    # print('@test: application now functioning!')
    # exit the program
    kb.wait('backspace')
    # end all the threads
    for _t in _thread_pool:
        _t.join()

def create_monitor_threads():
    # creating a list of threads that constantly monitoring
    # the changes of defined area in order to find a match
    _thread_pool = []
    _thread_args = [
        (sample_scan_btn, 'pay_scan', scan, 'watching scan button'),
        (sample_pay_btn, 'pay_btn', press_pay_btn, 'watching pay button'),
        (sample_done_btn, 'pay_done', close, 'watching done pay activity'),
        (sample_failed_symble, 'pay_failed', common_close_action, 'watching failed activity'),
        (sample_services_page, 'pay_services', common_close_action, 'watching services activity'),
        (sample_pwd_page, 'pay_pwd', enter_sec_keys, 'watching password activity')

    ]
    for _args in _thread_args:
        _t = threading.Thread(target= vision_autobot, args=(_args[0], hot_area[_args[1]], _args[2], _args[3]))
        _t.start()
        _thread_pool.append(_t)
    return _thread_pool
    

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
    print('@test: thread paused. press [backspace] to end and exit')

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
    _freq = copy.deepcopy(frequency)
    _sample_gray = target
    while signal:
        _target = pyautogui.screenshot(region=(_x, _y, _w, _h))
        _target_gray = cv2.cvtColor(np.array(_target), cv2.COLOR_BGR2GRAY)
        _m = cmp_img(_sample_gray, _target_gray)

        if _m > _accuracy:
            # print('@test: similarity: %0.2f' % _m)
            callback()
            # sleep 1 second when matched
            _freq = 0.3

        time.sleep(_freq)
        # reset
        _freq = copy.deepcopy(frequency)
    print('@test: vision thread %s ended.' % msg)

def qr_get_ready():
    global qr_gen_status
    # telling the thread to prepare the new qr code for scanning
    qr_gen_status = True
    print('@test next qr code is ready')

def prepare_qrcodes():
    global data, d_index, qr_gen_status, signal

    while signal:
        if qr_gen_status:
            if d_index < 0:
                # No more Jobs entering hibernation mode
                qr_gen_status = False
                print('@test: No more data!!')
                # terminate
                end_thread()
            else:
                # get a new link
                _link = data[d_index]
                if not _link or _link.isspace():
                    pass
                else:
                    # print('ling: %s' % _link)
                    print('@test: preparing QRcode number %i' % d_index)
                    img = gen_qr(_link)
                    img.show()
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
    # wait for a bit in case passwords input activity haven't showup
    # time.sleep(0.1)

def enter_sec_keys():
    global secert_pwd

    # print('@test: Entering secret keys for payment')
    _sec_key = secert_pwd
    # input passwords
    # print('@test: entering password %s' % _sec_key)
    for _key in _sec_key:
        # Entering the keys
        pyautogui.press(_key)
        # print(_key)

def scan():
    pyautogui.moveTo(x=mouse_pos['scan']['x'], y=mouse_pos['scan']['y'])
    pyautogui.click()
    # print('@test: start scanning')

def scan_failed():
    pyautogui.moveTo(x=mouse_pos['scan_failed']['x'], y=mouse_pos['scan_failed']['y'])
    pyautogui.click()
    collapse_photo()
    print('@test: dismiss failed scan result')

def close():
    qr_get_ready()
    pyautogui.moveTo(x=mouse_pos['payment_done']['x'], y=mouse_pos['payment_done']['y'])
    pyautogui.click()
    # print('@test: close done page')
    time.sleep(0.2)
    common_close_action()

def common_close_action():
    qr_get_ready()
    pyautogui.moveTo(x=mouse_pos['payment_failed']['x'], y=mouse_pos['payment_failed']['y'])
    pyautogui.click()
    # collapse_photo()
    # print('@test: press on common close button')

def collapse_photo():
    # close the previous qrcode window
    pyautogui.moveTo(x=529, y=78)
    pyautogui.click()

# -----------------------------------------------------------------

if __name__ == "__main__":
    init()
