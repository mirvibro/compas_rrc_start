import json
from camera import Camera
from robot import Robot
from gripper import Gripper
from compas.geometry import Frame, Point
from data_processing import reconstruction_realitycapture


ROB_NAME = '/rob1'
TOOL_NAME = 'tool1'
WOBJ_NAME = 'wobj0'
CAM_PORT = 0

drop_off_origin = Point(1000, 200, 30)
drop_off_offset = Point(0, 50, 0)

def read_file(file):
    f = open(file)
    data = json.load(f)

    f.close()
    return data

def scan_routine(robot, camera, data):
    for target in data['TargetPlanes']['Planes']:
        point = [target['point'][0],
                 target['point'][1],
                 target['point'][2]]
        x_axis = [target['x-axis'][0],
                  target['x-axis'][1],
                  target['x-axis'][2]]
        y_axis = [target['y-axis'][0],
                  target['y-axis'][1],
                  target['y-axis'][2]]

        robot.move_to_smooth(Frame(point, x_axis, y_axis))
        print(robot.where())

def decon_routine(robot, data):
    i = 0
    for target in data['TargetPlanes']['Planes']:
        drop_off_point = drop_off_origin + (drop_off_offset * i)
        drop_off = Frame(drop_off_point, [-1, 0, 0])

        point = [target['point'][0],
                 target['point'][1],
                 target['point'][2]]
        x_axis = [target['x-axis'][0],
                  target['x-axis'][1],
                  target['x-axis'][2]]
        y_axis = [target['y-axis'][0],
                  target['y-axis'][1],
                  target['y-axis'][2]]
        
        robot.move_and_grab(Frame(point, x_axis, y_axis))
        robot.move_and_release(drop_off)
        print(robot.where())
        i = i + 1


def recon_routine(robot, data):
    i = 8
    for target in data['TargetPlanes']['Planes']:
        pick_up_point = drop_off_origin + (drop_off_offset * i)
        pick_up = Frame(pick_up_point, [-1, 0, 0])

        point = [target['point'][0],
                 target['point'][1],
                 target['point'][2]]
        x_axis = [target['x-axis'][0],
                  target['x-axis'][1],
                  target['x-axis'][2]]
        y_axis = [target['y-axis'][0],
                  target['y-axis'][1],
                  target['y-axis'][2]]
        
        robot.move_and_grab(pick_up)
        robot.move_and_release(Frame(point, x_axis, y_axis))
        print(robot.where())
        i = i - 1


if __name__ == '__main__':

    # Set up tool
    tool = Gripper(TOOL_NAME)

    # Set up robot and move to home position
    robot = Robot(ROB_NAME, tool, WOBJ_NAME)
    robot.move_to_home()

    # Set up camera
    camera = Camera(CAM_PORT, "vids")
    camera.start_video_recording()
    
    # Read target planes for scan
    data = read_file('./json/scan-planes.json')

    # Execute scan routine
    scan_routine(robot, camera, data)

    # Stop recording
    camera.stop_video_recording()
    camera.release()
        
    # Do photogrammetry
    #reconstruction_realitycapture.reconstruct()

    # Start object recognition and partition thru rhino.compute, write to folder

    # Transform the meshes into concrete objects
    #box-fitting-hausdorff.py

    # Start reconfiguration thru rhino.compute, return result or write to folder
    decon_data = read_file('./json/decon.json')
    recon_data = read_file('./json/recon1.json')

    # Figure out how to get from current to goal configuration

    # Move robot accordingly
    decon_routine(robot, decon_data)
    recon_routine(robot, recon_data)

    # Close client
    robot.shutdown()


    
    