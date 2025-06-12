import compas_rrc as rrc
from compas.geometry import Frame

home = [[535.372401809,150,723.429338613],[0.190808996,0,0.981627183,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]]

drop_off = [[296, 546, 179], [0, 0.707107, 0.707107, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]]

targets = [[[955.12, 157.91, 110], [0, 0.707504, 0.706709, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[850.51, 386.03, 110], [-0, 0.25748, 0.966284, -0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[737.19, 422.85, 110], [0, 0.143269, 0.989684, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[955.12, 157.91, 95], [0, 0.000562, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[737.22, 422.89, 80], [0, 0.801455, 0.598055, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[955.12, 157.91, 65], [0, 0.000562, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[850.51, 386.03, 50], [-0, 0.25748, 0.966284, -0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[955.17, 195.41, 50], [0, 0.000562, 1, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[955.09, 127.91, 50], [-0, 0.000562, 1, -0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[768.84, 112.02, 35], [0, -0.304644, 0.952466, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]],
           [[768.84, 112.02, 20], [0, -0.304644, 0.952466, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]]]



def close_gripper():
    pulse_time = 0.2
    done = abb.send_and_wait(rrc.PulseDigital('ABB_Scalable_IO_0_DO1', pulse_time))

def open_gripper():
    pulse_time = 0.2
    done = abb.send_and_wait(rrc.PulseDigital('ABB_Scalable_IO_0_DO2', pulse_time))

def move_and_lift(target, speed = 100):
    print('Targeting ')

    # Copy target and change z value
    above_target = target.copy()
    above_target.point[2] += 100

    # Move robot to pos above the gripping point
    done = abb.send_and_wait(rrc.MoveToFrame(above_target, speed, rrc.Zone.FINE, rrc.Motion.JOINT))
    open_gripper

    # Move robot to pos of gripping point
    done = abb.send_and_wait(rrc.MoveToFrame(target, speed/2, rrc.Zone.FINE, rrc.Motion.LINEAR))
    close_gripper()

    # Move up carefully
    done = abb.send_and_wait(rrc.MoveToFrame(above_target, speed/2, rrc.Zone.FINE, rrc.Motion.LINEAR))

    return done

def move_and_drop(target = Frame(drop_off[0], [-1,0,0]), speed = 100):
    print('Dropping off at' )

    # Move robot to drop off point
    done = abb.send_and_wait(rrc.MoveToFrame(target, speed, rrc.Zone.Z20, rrc.Motion.JOINT))

    # Drop
    open_gripper()

    return done


if __name__ == '__main__':

    # Create Ros Client
    ros = rrc.RosClient()
    ros.run()

    # Create ABB Client
    abb = rrc.AbbClient(ros, '/rob1')
    print('Connected.')

    # Set tool
    abb.send(rrc.SetTool('tool1'))

    # Set work object
    abb.send(rrc.SetWorkObject('wobj0'))

    for target in targets:
        done = move_and_lift(Frame(target[0], [-1,0,0]))
        done = move_and_drop(Frame(drop_off[0], [-1,0,0]))

    # Print feedback 
    print('Feedback = ', done)

    # End of Code
    print('Finished talking to Abby')

    # Close client
    ros.close()
    ros.terminate()
    