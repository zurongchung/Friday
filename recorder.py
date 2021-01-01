from pynput.mouse import Button, Listener
import pyautogui
import keyboard as kb
import copy
import json

config_json = 'samples_config.json'

class Recorder:

    def __init__(self):
        self.path = 'samples\\mdpi\\'
        self.sufix = '.png'
        self.name = 'void'
        self.fp = ''
        self.cid = 0
        self.ipos = {'x': 0, 'y': 0}
        self.epos = {'x': 0, 'y': 0}
        self.zoom = {'x': 0, 'y': 0}
        # self.region = {'x': 0, 'y': 0, 'w': 0, 'h': 0}
        self.ready = False
        self.listener = None
        self.json_partial = {}
    
    def reset(self):
        self.name = 'void'
        self.fp = ''
        self.cid = 0
        self.ipos = {'x': 0, 'y': 0}
        self.epos = {'x': 0, 'y': 0}
        self.zoom = {'x': 0, 'y': 0}
        # self.region = {'x': 0, 'y': 0, 'w': 0, 'h': 0}
        self.ready = False
        self.listener = None

    def load_config(self):
        # load the config file
        print('loading config file')
        with open(config_json, 'r') as file:
            self.json_partial = json.load(file)
        
        print(self.json_partial)

    def write_config(self, key, value):
        # !!MUST
        # read the contents and make changes then saveO
        self.load_config()

        # region = dict({'x': x_y_w_h[0], 'y': x_y_w_h[1], 'w': x_y_w_h[2], 'h': x_y_w_h[3]})
        self.json_partial['main'][key] = value
        # write to config file
        with open(config_json, 'w') as file:
            json.dump(self.json_partial, file)
        print(self.json_partial)
        
        print('Writing to config file DONE!')

    def start(self):
        # TODO add input validation

        label = input('Provide a name for the sample image \n')
        self.name = 'pay_{0}'.format(label)
        self.fp = self.path + self.name + self.sufix

        self.mount_listener()
    
    def restart(self):
        self.reset()
        self.start()

    def get_marker(self, x, y, button, pressed):
        if button == Button.left and pressed:
            self.write_config('marker', {'x': x, 'y': y})
            print('marker created.')
            return False

    def on_click(self, x, y, button, pressed):
        cnt = None
        _cid = self.cid
        if button == Button.left and pressed:
            if _cid == 0:
                cnt = self.ipos
                print('start define the ending point.')
            if _cid == 1:
                cnt = self.epos
                print('finally define the interacting point.')
            if _cid == 2:
                cnt = self.zoom
                self.ready = True
            cnt['x'] = x
            cnt['y'] = y
            _cid += 1
            self.cid = _cid
            print(cnt)
            if self.ready:
                x_y_w_h = self.procssing_coords()
                region = dict({'x': x_y_w_h[0], 'y': x_y_w_h[1], 'w': x_y_w_h[2], 'h': x_y_w_h[3]})
                _value = {'img': self.fp, 'zoom': self.zoom, 'region': region}
                # save to configuration file
                self.write_config(self.name, _value)
                self.create_sample_image(x_y_w_h)
                print('press + to create another sample | press 0 to exit.')
                # end the thread listener
                return False
    
    def mount_listener(self):
        self.cid = 0
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()
        print('mouse listener is online.')
        print('start define starting point.')

    def mount_marker_listener(self):
        _listener = Listener(on_click=self.get_marker)
        _listener.start()
        print('marker listener started.')
        print('click on the top left corner of the app.')

    def procssing_coords(self):
        # print('original: ix: {0}, iy: {1}, ex: {2}, ey: {3}'.format(self.ipos['x'], self.ipos['y'], self.epos['x'], self.epos['y']))
        self.swap_pos(self.ipos, self.epos)
        x = self.ipos['x']
        y = self.ipos['y']
        # calculate the screen shot area
        # and create the sample image
        _w = abs(self.epos['x'] - self.ipos['x'])
        _h = abs(self.epos['y'] - self.ipos['y'])
        # print('x: {0}, y: {1}, w: {2}, h: {3}'.format(self.ipos['x'], self.ipos['y'], _w, _h))
        return (x, y, _w, _h)

    def create_sample_image(self, x_y_w_h):
        print('creating sample image...')
        x, y, _w, _h = x_y_w_h
        # _fp = self.path + self.name + self.sufix
        _shoot = pyautogui.screenshot(self.fp, region=(x, y, _w, _h))
        _shoot.show()
        print('sample created.')
    
    def swap_pos(self, ipos, epos):
        
        # screen shot can only be taken from top-left to bottom-right
        tmp_cnt = copy.deepcopy(self.epos)
        # print('tmp {}'.format(tmp_cnt))
        self.epos['x'] = self.epos['x'] if self.epos['x'] > self.ipos['x'] else self.ipos['x']
        self.epos['y'] = self.epos['y'] if self.epos['y'] > self.ipos['y'] else self.ipos['y']
        # print('half: ix: {0}, iy: {1}, ex: {2}, ey: {3}'.format(self.ipos['x'], self.ipos['y'], self.epos['x'], self.epos['y']))
        
        self.ipos['x'] = self.ipos['x'] if self.ipos['x'] < tmp_cnt['x'] else tmp_cnt['x']
        self.ipos['y'] = self.ipos['y'] if self.ipos['y'] < tmp_cnt['y'] else tmp_cnt['y']
        # print('swaped: ix: {0}, iy: {1}, ex: {2}, ey: {3}'.format(self.ipos['x'], self.ipos['y'], self.epos['x'], self.epos['y']))

if __name__ == "__main__":
    r = Recorder()
    # r.start()
    print('create sample -> press 1 \ncreate marker -> press 2 \nexit -> press 0')
    kb.add_hotkey('1', r.start)
    kb.add_hotkey('plus', r.restart)
    kb.add_hotkey('2', r.mount_marker_listener)
    kb.wait('0')