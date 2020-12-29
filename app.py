import os
import sys
import time
import cv2
import keyboard as kb
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import qrcode
from qrcode.image.pure import PymagingImage
import tkinter
from PIL import ImageTk, Image
from skimage.metrics import structural_similarity as ssim
import threading

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
sample_done_btn = None
sample_services_page = None
sample_failed_symble = None

mouse_pos = {
    'scan': {'x': 1893, 'y': 114},
    'pay': {'x': 1752, 'y': 944},
    'payment_done': {'x': 1878, 'y': 119},
    'payment_failed': {'x': 1842, 'y': 114},
    'order_list': {'x': 1842, 'y': 114}
}

hot_area = {
    'pay_btn': {'x': 1502, 'y': 922, 'w': 405, 'h': 50},
    'pay_done': {'x': 1502, 'y': 115, 'w': 405, 'h': 88},
    'pay_failed': {'x': 1502, 'y': 160, 'w': 405, 'h': 180},
    'pay_scan': {'x': 1502, 'y': 90, 'w': 405, 'h': 52},
    'pay_services': {'x': 1502, 'y': 90, 'w': 405, 'h': 52}

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
    global data, d_index, secert_pwd, sample_pay_btn, sample_scan_btn,\
         sample_done_btn, sample_failed_symble, sample_services_page

    secert_pwd = input('please provide your password for the payment...\n>>> ')
    print('@test: password is: %s' % secert_pwd)
    init_data()
    load_samples()
    # manually actions
    kb.add_hotkey('right', prepare_qrcodes)
    kb.add_hotkey('q', scan)
    kb.add_hotkey('space', press_pay_btn)
    kb.add_hotkey('w', close)
    kb.add_hotkey('e', failed)
    kb.add_hotkey('m', end_thread)
    kb.add_hotkey('r', reload_data)
    t0 = threading.Thread(target= vision_autobot, 
        args=(sample_scan_btn, hot_area['pay_scan'], scan, 'press scan button'))
    t1 = threading.Thread(target= vision_autobot, 
        args=(sample_pay_btn, hot_area['pay_btn'], press_pay_btn, 'press pay button'))
    t2 = threading.Thread(target= vision_autobot, 
        args=(sample_done_btn, hot_area['pay_done'], close, 'auto done pay page'))
    t3 = threading.Thread(target= vision_autobot, 
        args=(sample_failed_symble, hot_area['pay_failed'], failed, 'auto close failed page'))
    t4 = threading.Thread(target= prepare_qrcodes)
    t5 = threading.Thread(target= vision_autobot, 
        args=(sample_services_page, hot_area['pay_services'], close_service_page, 'auto close services page'))

    t0.start()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    print('@test: application now functioning!')
    kb.wait('backspace')
    t0.join()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()

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
    global sample_pay_btn, sample_scan_btn, sample_done_btn, sample_failed_symble, sample_services_page 
    # load the samples into memory
    print('@test: loading samples into memory...')
    sample_pay_btn =  cv2.cvtColor(cv2.imread('samples/pay_btn_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_scan_btn =  cv2.cvtColor(cv2.imread('samples/pay_scan_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_done_btn =  cv2.cvtColor(cv2.imread('samples/pay_done_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_failed_symble =  cv2.cvtColor(cv2.imread('samples/pay_failed_color.png'), cv2.COLOR_BGR2GRAY) 
    sample_services_page =  cv2.cvtColor(cv2.imread('samples/pay_services_color.png'), cv2.COLOR_BGR2GRAY) 

# @todo when [frequency is too fast clicking wrong position will happen]
def vision_autobot(target, area, callback, msg, accuracy=0.96, frequency=0.1):
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
    # read the sample image from sample folder
    # _sample = cv2.imread(target)
    # _sample_gray = cv2.cvtColor(_sample, cv2.COLOR_BGR2GRAY)
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

def fill_sec_keys():
    global secert_pwd

    print('@test: Entering secret keys for payment')
    _sec_key = secert_pwd
    # input passwords
    for _mos_p in _sec_key:
        # Entering the keys
        pyautogui.press(_mos_p)
        # print(_mos_p)

def scan():
    pyautogui.moveTo(x=1892, y=120)
    pyautogui.click()
    print('@test: start scanning')

def close():
    pyautogui.moveTo(x=1880, y=119)
    pyautogui.click()
    time.sleep(0.2)
    pyautogui.moveTo(x=1845, y=114)
    pyautogui.click()
    print('@test: close done page')

def failed():
    pyautogui.moveTo(x=1845, y=114)
    pyautogui.click()
    print('@test: close failed page')

def close_service_page():
    pyautogui.moveTo(x=1852, y=117)
    pyautogui.click()
    print('@test: close services page')

def collapse_photo():
    # close the previous qrcode window
    pyautogui.moveTo(x=645, y=69)
    pyautogui.click()

# -----------------------------------------------------------------

if __name__ == "__main__":
    init()