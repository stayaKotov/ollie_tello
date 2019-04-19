from imutils.video import VideoStream
import cv2
import time
import numpy as np
import imutils
import argparse
from path_maker import PathMaker
from socket import socket, AF_INET, SOCK_DGRAM

HEIGHT = 600
WIDHT = 760
LENGTH = 80

def arg_parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=350, help="minimum area size")
    args = vars(ap.parse_args())
    return args


class Tracker(object):
    def __init__(self, args, path_maker, sock):
        """
        :param args: аргументы видео
        :param controller: объект контроллера
        :param path_maker: объект, создающий и отрисовывающий траекторию движения на кадре
        """
        self.args = args
        self.vs = self.set_video_object(self.args)
        self.path_maker = path_maker
        self.is_path_set = False
        self.path_points = None
        self.sock = sock

    def set_video_object(self, args):
        """
        Задать объект для стриминга кадров
        :param args: аргументы видео
        :return:
        """
        if args.get("video", None) is None:
            vs = VideoStream(src=1).start()
            time.sleep(1.0)
        else:
            vs = cv2.VideoCapture(self.args["video"])
        return vs


    def get_next_frame(self):
        frame = self.vs.read()
        frame = frame if self.args.get("video", None) is None else frame[1]

        if frame is None:
            return None, None, None

        frame = imutils.resize(frame, width=500)
        self.path_maker.get_image(frame.copy())
        if not self.is_path_set:
            self.path_points = self.path_maker.get_points()
            self.is_path_set = True

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return frame, gray, "Unoccupied"

    def draw_trajectory(self, grandpaFrame, frame, gray):
        frameDelta2 = cv2.absdiff(grandpaFrame, gray)
        thresh = cv2.threshold(frameDelta2, 70, 255, cv2.THRESH_BINARY)[1]

        # for x, y in zip(*self.path_points):
        #     cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
        return frameDelta2, thresh

    def get_contours(self, thresh):
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts

    def draw_object_box(self, cnts, frame, text):
        # loop over the contours
        valid_contours = [(c, cv2.contourArea(c)) for c in cnts if cv2.contourArea(c) >= self.args["min_area"]]
        if len(valid_contours):
            sorted_valid_contours = sorted(valid_contours, key=lambda x: x[1], reverse=True)
        else:
            sorted_valid_contours = [(None, 0)]

        for c, _ in sorted_valid_contours[:]:
            if c is None:
                return frame, text, None, None
            (x, y, w, h) = cv2.boundingRect(c)
            cur_x, cur_y = x + np.int32(w / 2), y + np.int32(h / 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cur_x, cur_y), 1, (0, 0, 255), -1)
            text = "Occupied"
            break

        cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return frame, text, cur_x, cur_y


    def stream(self):
        """
        Главный цикл, в котором высвечивается кадр, а также отслеживается положение объекта при въезжании в кадр
        :return:
        """

        grandpaFrame = None
        firstFrame = None
        cur_x = None
        cur_y = None

        j = 0

        while True:
            j += 1 
            cv2.startWindowThread()

            frame, gray, text = self.get_next_frame()
            if frame is None:
                break

            if firstFrame is None:
                firstFrame = gray
                grandpaFrame = gray
                continue

            frameDelta2, thresh = self.draw_trajectory(grandpaFrame, frame, gray)
            cnts = self.get_contours(thresh)
            frame, text, cur_x, cur_y = self.draw_object_box(cnts, frame, text)

            if j % 300 == 0 and cur_x is not None:
                msg = f'{cur_x},{cur_y}'
                print(msg)
                self.sock.sendto(msg.encode(),('', PORT))

            frame = cv2.resize(frame, (WIDHT, HEIGHT))
            cv2.imshow("Security Feed", frame)

            key = cv2.waitKey(1) & 0xFF
            firstFrame = gray

            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break

        # cleanup the camera and close any open windows
        self.vs.stop() if self.args.get("video", None) is None else self.vs.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    args = arg_parse()
    path_maker = PathMaker(None)

    sock = socket(AF_INET,SOCK_DGRAM)
    MAX_SIZE = 4096
    PORT = 12345
    tracker = Tracker(args, path_maker, sock)
    tracker.stream()
