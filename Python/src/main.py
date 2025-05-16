import json
from camera import Camera
from robot import Robot
from gripper import Gripper
from compas.geometry import Frame
import reconstruction_realitycapture

ROB_NAME = '/rob1'
TOOL_NAME = 'tool1'
WOBJ_NAME = 'wobj0'
CAM_PORT = 0

def read_file(file):
    f = open(file)
    data = json.load(f)

    f.close()
    return data

def scan_routine(robot, camera, data):
    for target in data['TargetPlanes']['Planes']:
        # Uncomment this to wait for user input before each step
        #input("Press Enter to continue to the next target plane...")

        point = [target['point'][0],
                 target['point'][1],
                 target['point'][2]]
        x_axis = [target['x-axis'][0],
                  target['x-axis'][1],
                  target['x-axis'][2]]
        y_axis = [target['y-axis'][0],
                  target['y-axis'][1],
                  target['y-axis'][2]]

        robot.move_to(Frame(point, x_axis, y_axis))
        camera.take_picture()
        robot.where()


if __name__ == '__main__':

    # Set up tool
    tool = Gripper(TOOL_NAME)

    # Set up robot and move to home position
    robot = Robot(ROB_NAME, tool, WOBJ_NAME)
    robot.move_to_home()

    # Set up camera
    camera = Camera(CAM_PORT, "imgs")
    
    # Read target planes for scan
    data = read_file('./json/scan-planes-05-16.json')

    # Execute scan routine
    scan_routine(robot, camera, data)
        
    # Do photogrammetry
    reconstruction_realitycapture.reconstruct()

    # Start object recognition and partition thru rhino.compute, return result or write to folder

    # Transform the meshes into concrete objects
    #box-fitting-hausdorff.py

    # Start reconfiguration thru rhino.compute, return result or write to folder

    # Figure out how to get from current to goal configuration (all same parts or different?)

    # Move robot accordingly
    

    # Close client
    robot.shutdown()


    
    