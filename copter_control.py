from djitellopy import Tello
import numpy as np

class CopterControl():
    def __init__(self, length_w, length_h, width, heigth):
        self.length_w = length_w
        self.length_h = length_h
        self.width = width
        self.heigth = heigth
        self.cur_x = 0
        self.cur_y = self.heigth
        self.is_wait = True
        self.copter = Tello()
        self.copter.set_speed(100)

    def __loop(self):
        sum([i for i in range(18000000)])

    def __update_coords(self, new_x, new_y):
        self.cur_x = new_x
        self.cur_y = new_y

    def __develop_control(self, target_x, target_y, verbose=True):
        dx = int((self.length_w) / self.width * np.abs(self.cur_x - target_x))
        dy = int((self.length_h) / self.heigth * np.abs((self.heigth - target_y) - (self.heigth - self.cur_y)))
        if verbose:
            print(f'land dx = {dx}, land dy = {dy}')

        if target_x > self.cur_x:
            self.copter.move_right(dx)
        elif target_x < self.cur_x:
            self.copter.move_left(dx)

        self.__loop()

        if target_y > self.cur_y:
            self.copter.move_back(dy)
        elif target_y < self.cur_y:
            self.copter.move_forward(dy)

        self.__update_coords(target_x, target_y)
        if verbose:
            print(f'cur_x = {self.cur_x} cur_y = {self.cur_y}')


    def control(self, target_x, target_y):
        # if target_x is not None and target_y is not None and self.is_wait:
        #     self.is_wait = False

        if target_x is not None and np.abs(target_x - self.cur_x) > 100 and np.abs(target_y - self.cur_y) > 100:
            if self.is_wait:
                self.is_wait = False
                self.copter.connect()
                self.copter.takeoff()
                self.__loop()
            print('control on')
            self.__develop_control(target_x, target_y)
        else:
            print(f'offset is small: px dx = {np.abs(target_x - self.cur_x)}, px dy = {np.abs(target_y - self.cur_y)}')


