import compas_rrc as rrc
from compas.geometry import Frame
import json


def read_file(file):
    f = open(file)
    data = json.load(f)

    f.close()
    return data


if __name__ == '__main__':

    # Create Ros Client
    ros = rrc.RosClient()
    ros.run()

    # Create ABB Client
    abb = rrc.AbbClient(ros, '/rob1')
    print('Connected.')

    # Set tool
    abb.send(rrc.SetTool('tool0'))

    # Set work object
    abb.send(rrc.SetWorkObject('wobj0'))

    # Read file
    data = read_file('Python\json\jsonTest.json')

    for target in data['OrbitingPlanes']:
        done = abb.send_and_wait(rrc.MoveToFrame(Frame([target['x']*100, target['y']*100, target['z']*100], [-1, 0, 0]), 100, rrc.Zone.Z20, rrc.Motion.JOINT))
        print('Moved to ' + str(target['x']*100) + str(target['y']*100) + str(target['z']*100))
    
    # Print feedback 
    print('Feedback = ', done)

    # End of Code
    print('Finished talking to Abby')

    # Close client
    ros.close()
    ros.terminate()
    