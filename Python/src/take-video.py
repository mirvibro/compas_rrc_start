import os
import cv2
import json
from datetime import datetime


# Setup
if not os.path.exists("vids"):
    os.makedirs("vids")

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("Failed to open camera")
    exit()

print("Camera set up")

# Video settings
frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20.0

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
video_filename = os.path.join("vids", f"{timestamp}.mp4")

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MP4v')
out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))

print("Recording... Press 'q' to stop.")

while True:
    ret, frame = camera.read()
    if not ret:
        break

    out.write(frame)          # Write the frame to the video file
    cv2.imshow('Recording', frame)  # Optional: show the video as it's recording

    # Press 'q' to quit recording
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
camera.release()
out.release()
cv2.destroyAllWindows()

print("Video saved:", video_filename)