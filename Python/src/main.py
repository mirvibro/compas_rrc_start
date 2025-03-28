import compas_rrc as rrc
from compas.geometry import Frame
from datetime import datetime
import json
import os
import cv2 as cv2


def read_file(file):
    f = open(file)
    data = json.load(f)

    f.close()
    return data

def take_picture(cam):
    result, image = cam.read()
    if (result):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join('imgs', f"{timestamp}.jpg")

        cv2.imwrite(filename, image)
        print(f"Image saved: {filename}")
    else: 
        print("No image detected, please try again.") 


if __name__ == '__main__':

    # Create Ros Client
    ros = rrc.RosClient()
    ros.run()

    # Create ABB Client
    abb = rrc.AbbClient(ros, '/rob1')
    print('Connected')

    # Set up robot
    abb.send(rrc.SetTool('tool1'))
    abb.send(rrc.SetWorkObject('wobj0'))

    # Set up camera
    cam_port = 0
    cam = cv2.VideoCapture(cam_port, cv2.CAP_DSHOW)
    if not os.path.exists('imgs'):
        os.makedirs('imgs')
    print('Camera set up')

    # Read target planes for scan
    data = read_file('./json/target-planes-routine.json')

    # Send target planes for scan to robot
    print('Start scanning routine')
    for target in data['TargetPlanes']['jsonTest']:
        input("Press Enter to continue to the next target plane...")  # Wait for user input
        point = target['point']
        print("point:", point, type(point))
        response = abb.send_and_wait(rrc.MoveToFrame(Frame(point, [-1, 0, 0]), 100, rrc.Zone.Z20, rrc.Motion.JOINT))
        print('Moved to ' + str(point[0]) + str(point[1]) + str(point[2]))
        take_picture(cam)
    
    # Print robot's response
    print('Response: ', response)

    # Do photogrammetry using COLMAP

    # Send mesh to folder where rhino can read it

    # Read target planes from rhino result folder

    # Send target planes for pick and place to robot

    # Wait for more input??

    # Close client
    ros.close()
    ros.terminate()
    print('Disconnected')


    
    