import numpy as np
import cv2


class PathMaker(object):
    """
    Класс позволяющий задать траекторию, по которой будет двигаться олли
    """
    def __init__(self, img):
        """
        :param img: кадр
        """
        self.img = img

    def get_image(self, img):
        """
        Преобразовать кадр в ч\б + размыть гаусовым фильтром размером 3х3
        :param img: текущий кадр
        :return:
        """
        self.img = img
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.img = cv2.blur(self.img, (3, 3))

    @staticmethod
    def line_function(frm=0, to=10, count=400):
        t = np.linspace(frm, to, count)
        return 200 / (t + 0.1) * np.sin(t)

    def get_points(self):
        """
        Функция, по которой рисуется траектория
        :return:
        """
        x = 50
        y = 150

        y1 = self.line_function(0,10,400)
        return np.asarray([x + np.asarray([i for i in range(y1.shape[0])]), y1+np.int32(y)]).astype(np.int32)

    def draw_line(self):
        """
        Отрисовка линии на кадре точками красными точками
        :return:
        """
        x, y = self.get_points()
        for xx, yy in zip(x, y):
            cv2.circle(self.img, (xx, yy), 1, (0, 255, 0), 2)
