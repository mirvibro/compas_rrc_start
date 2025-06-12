
from datetime import datetime
import os
import cv2
import threading

class Camera:
    def __init__(self, port, dir):
        self.cam = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.output_dir = dir
        self.recording = False
        self.thread = None
        print('Camera set up')

    def take_picture(self):
        result, image = self.cam.read()
        if (result):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(self.output_dir, f"{timestamp}.jpg")

            cv2.imwrite(filename, image)
            #print(f"Image saved: {filename}")
        else: 
            print("No image detected, please try again.")

    def start_video_recording(self, fps=20.0, frame_size=(640, 480)):
        if self.recording:
            print("Already recording.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.output_dir, f"{timestamp}.mp4")

        self.recording = True
        self.thread = threading.Thread(target=self._record_video, args=(filename, fps, frame_size))
        self.thread.start()

    def _record_video(self, filename, fps, frame_size):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, frame_size)

        while self.recording:
            ret, frame = self.cam.read()
            if ret:
                out.write(frame)
        out.release()
        print(f"Video saved: {filename}")

    def stop_video_recording(self):
        if self.recording:
            self.recording = False
            self.thread.join()
            print("Recording stopped.")

    def release(self):
        self.cam.release()
        print("Camera released.")

    