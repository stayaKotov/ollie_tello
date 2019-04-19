import numpy as np
import requests
from tracker import Tracker
import time
from djitellopy import Tello
from copter_control import CopterControl
from multiprocessing import Process, Pool, Lock
from socket import socket, AF_INET, SOCK_DGRAM

LOCAL_TARGET = None
GLOBAL_ANGLE = 0
GLOBAL_D = None
PREV_DIST = None


class Controller(object):
    def __init__(self, url, copter):
        self.url = url
        self.angles = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
        self.commands = self.create_commands()
        self.copter = copter

    def create_commands(self):
        commands = {'f': 'moveInDirectionF', 'b': 'moveInDirectionB', 's': 'stopMoving', 'v':'moveInDirectionV'}
        for ang in self.angles:
            commands[f'l_{ang}'] = f'moveInDirectionL_{ang}'
            commands[f'r_{ang}'] = f'moveInDirectionR_{ang}'
        return commands

    def action(self, typo):
        if typo in self.commands:
            requests.post(f'{self.url}{self.commands[typo]}')

    def dist(self, x1, y1, x2, y2):
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def find_min_angle(self, alpha):
        min_ang = (0, 1000)
        for ang in self.angles:
            ang_diff = np.abs(ang - alpha)
            if ang_diff < min_ang[1]:
                min_ang = (ang, ang_diff)
        return min_ang

    def calc_angle(self,a, b, c):
        return np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180 / np.pi

    def find_base_points(self, object_loc, n=5):
        """
        Поиск трех ключевых точек на траектории:
            минимальной по расстоянию до текущего центра масс объекта
            перпендикулярной к текущему центру масс
            минимальной по счету n точки по расстоянию до кущего центра масс объекта
        :param object_loc: текущее положение центра масс объекта
        :param n: n-ый минимальный элемент на кривой траектории относительно текущего центра масс объекта
        :return:
        """

        prev_distances = [
            [self.controller.dist(object_loc[0], object_loc[1], x, y), x, y]
            for x, y in zip(*self.path_points)
        ]

        prev_distances = sorted(prev_distances, key=lambda x: x[0], reverse=False)
        minimum_point = prev_distances[0]
        target = prev_distances[-1]

        scope_x = lambda x1, x2: x1 < x2 if minimum_point[1] < target[0] else lambda x1, x2: x1 >= x2

        distances = [prev_distances[0]] + [ [d, x, y] for d, x, y in prev_distances if scope_x(minimum_point[1], x) ]

        orthogonal_points = [
            [np.abs(object_loc[0] - dis[1]), dis] for dis in prev_distances if np.abs(object_loc[0] - dis[1]) < 10
        ]
        orthogonal_points = sorted(orthogonal_points, key=lambda x: x[0], reverse=False)
        orthogonal_point = orthogonal_points[0][1] if len(orthogonal_points) else minimum_point

        return [minimum_point] + [orthogonal_point] + [distances[n]]

    def dist(self, x1, y1, x2, y2):
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def find_D(self, object_loc):
        """
        D представляет собой маркер положения центра масс объекта относительно траектории снизу\сверху (-1\1)
        :param object_loc: текущее положение центра масс объекта
        :return:
        """
        xx, yy = object_loc
        # точки близкие к центру масс объекта по оси х
        orthogonal_points = [
            [np.abs(object_loc[0] - x), x, y] for x, y in zip(*self.path_points) if np.abs(object_loc[0] - x) < 10
        ]
        orthogonal_points = sorted(orthogonal_points, key=lambda x: x[0], reverse=False)
        # если ортогональная точка больше центра масс объекта по оси y, то объект сверху линии, иначе ниже
        return 1 if yy < orthogonal_points[0][2] else -1

    def control(self, target_x, target_y):
        print(target_x, target_y)
        self.copter.control(target_x, target_y)



if __name__ == "__main__":


    copter = CopterControl(length=190, width=500, heigth=375)
    controller = Controller(url='http://127.0.0.1:3000/api/robots/robot/commands/', copter=copter)


    MAX_SIZE = 4096
    PORT = 12345
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', PORT))
    while True:
        data, addr = sock.recvfrom(MAX_SIZE)
        target_x, target_y = list(map(lambda x: int(x), data.decode('utf-8').split(',')))
        print(f'target coords = {target_x}, {target_y}')

        controller.control(target_x, target_y)




