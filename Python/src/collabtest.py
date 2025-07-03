import json
from robot import Robot
from gripper import Gripper
from compas.geometry import Frame, Point
from compas.data import json_dump
import time


ROB_NAME = '/rob1'
TOOL_NAME = 'tool1'
WOBJ_NAME = 'wobj0'

drop_off_origin = Point(1000, 200, 35)
drop_off_offset = Point(0, 50, 0)

def read_file(file):
    f = open(file)
    data = json.load(f)

    f.close()
    return data


def decon_leadThrough(robot, data, transform_all_after_first=False, save_transformation=False): 

    """
    disassembly routine with hand-adjustment before each block 
    
    --->  set transform_all_after_first=True to transfrom all subsequent target frames with the first hand-adjustment transformation

    --->  set save_transformation=True to save all transformation (right now, visualization purposes)
    """

    offset = 50 # offset above pick-up point
    T_initial = [] # saving transformation after first hand-adjustment
    T_individual = [] # saving transformation after each individual subsequent adjustment

    for i, target in enumerate(data['TargetPlanes']['Planes']):

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
        
        og_frame = Frame(point, x_axis, y_axis) # original target frame
        
        if transform_all_after_first:
            if i == 0:
                T = robot.move_confirm_grab(og_frame, offset, get_transformation=True) # gets the first transformation after hand-adjustment
                T_initial.append(T)

            else:
                og_frame = Frame(point, x_axis, y_axis)
                tr_frame = og_frame.transformed(T) # applying transformation of the initial hand-adjustment
                T_i = robot.move_confirm_grab(tr_frame, offset, get_transformation=True)
                T_individual.append(T_i)

        else:
            robot.move_confirm_grab(og_frame, offset, get_transformation=False)

        robot.move_and_release(drop_off)
        i += 1
    
    if save_transformation:
        json_dump(T_initial, "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\json_leadThrough\\T_initial_1.json")
        json_dump(T_individual, "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\json_leadThrough\\T_individual_1.json")



if __name__ == '__main__':

    # Set up tool
    tool = Gripper(TOOL_NAME)

    # Set up robot and move to home position
    robot = Robot(ROB_NAME, tool, WOBJ_NAME)
    robot.move_to_home()

    # reading target frames

    decon_data = read_file('compas_rrc_start\\json\\decon.json')

    time.sleep(1)

    # disassembly routine with hand-adjustment before each block 

    decon_leadThrough(robot, decon_data, transform_all_after_first=True, save_transformation=False)

    robot.shutdown()


