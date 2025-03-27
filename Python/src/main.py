import compas_rrc as rrc
from compas.geometry import Frame
import json
import cv2 as cv


def read_file(file):
    f = open(file)
    data = json.load(f)

    f.close()
    return data

def take_picture(cam):
    result, image = cam.read()
    if (result): 
        cv.imshow("Cam", image) 
        cv.imwrite("Cam.png", image)
        cv.waitKey(0) 
        cv.destroyWindow("Cam")
    else: 
        print("No image detected, please try again.") 


if __name__ == '__main__':

    # Create Ros Client
    ros = rrc.RosClient()
    ros.run()

    # Create ABB Client
    abb = rrc.AbbClient(ros, '/rob1')
    print('Connected.')

    # Set up robot
    abb.send(rrc.SetTool('tool0'))
    abb.send(rrc.SetWorkObject('wobj0'))

    # Set up camera
    cam_port = 0
    cam = cv.VideoCapture(cam_port)

    # Read target planes for scan
    data = read_file('Python\json\target-planes-scan.json')

    # Send target planes for scan to robot
    for target in data['TargetPlanes']['jsonTest']:
        point = target['point'] * 100
        response = abb.send_and_wait(rrc.MoveToFrame(Frame(point[0], point[1], point[2], [-1, 0, 0]), 100, rrc.Zone.Z20, rrc.Motion.JOINT))
        print('Moved to ' + str(point[0]) + str(point[1]) + str(point[2]))
        take_picture(cam)
    
    # Print robot's response
    print('Response: ', response)

    # Do photogrammetry

    # Send mesh to folder where rhino can read it

    # Read target planes from rhino result folder

    # Send target planes for pick and place to robot

    # Wait for more input??

    # Close client
    ros.close()
    ros.terminate()
    print('Disconnected.')


    
    