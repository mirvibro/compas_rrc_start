
from datetime import datetime
import os
import cv2

class Camera:
    def __init__(self, port, dir):
        self.cam = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        if not os.path.exists(dir):
            os.makedirs(dir)
        print('Camera set up')

    def take_picture(self):
        result, image = self.cam.read()
        if (result):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join('imgs', f"{timestamp}.jpg")

            cv2.imwrite(filename, image)
            #print(f"Image saved: {filename}")
        else: 
            print("No image detected, please try again.")