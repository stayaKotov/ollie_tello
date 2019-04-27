import numpy as np
import requests
from tracker import Tracker
import time
from djitellopy import Tello
from copter_control import CopterControl
from multiprocessing import Process, Pool, Lock
from socket import socket, AF_INET, SOCK_DGRAM

PORT = 12345


class Controller(object):
    def __init__(self, copter):
        self.copter = copter

    def control(self, target_x, target_y):
        print(target_x, target_y)
        self.copter.control(target_x, target_y)


if __name__ == "__main__":
    W = 150
    H = 100
    copter = CopterControl(length_w=W, length_h=H, width=500, heigth=375)
    controller = Controller(copter=copter)


    MAX_SIZE = 4096
    PORT = PORT
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', PORT))
    while True:
        data, addr = sock.recvfrom(MAX_SIZE)
        target_x, target_y = list(map(lambda x: int(x), data.decode('utf-8').split(',')))
        print(f'target coords = {target_x}, {target_y}')

        controller.control(target_x, target_y)
