import compas_rrc as rrc

if __name__ == '__main__':

    # Create Ros Client
    ros = rrc.RosClient()
    ros.run()

    # Create ABB Client
    abb = rrc.AbbClient(ros, '/rob1')
    print('Connected to Abby.')

    # Print text on FlexPenant
    done = abb.send_and_wait(rrc.PrintText('Welcome to COMPAS_RRC on Abby'))

    # Set start values
    robot_joints, external_axes =[0, 0, 0, 0, 30, 0],  []

    # Move robot to start position
    done = abb.send_and_wait(rrc.MoveToJoints(robot_joints, external_axes, 1000, rrc.Zone.FINE))

    # Read value of joints
    robot_joints, external_axes = abb.send_and_wait(rrc.GetJoints())

    # Print received values
    print(robot_joints, external_axes)

    # Change a joint value [°]
    robot_joints.rax_1 -= 15 

    # Set speed [mm/s]
    speed = 100
    
    # Open Gripper virtual
    abb.send_and_wait(rrc.PulseDigital('gripper_open', 0.2))
    
    # Move robot the new pos
    done = abb.send_and_wait(rrc.MoveToJoints(robot_joints, external_axes, speed, rrc.Zone.FINE))

    # Print feedback 
    print('Feedback = ', done)

    # Close Gripper virtual
    abb.send_and_wait(rrc.PulseDigital('gripper_close', 0.2))

    # Print feedback 
    print('Feedback = ', done)

    # End of Code
    print('Finished talking to Abby')

    # Close client
    ros.close()
    ros.terminate()
