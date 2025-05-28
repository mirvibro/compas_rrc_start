import compas_rrc as rrc
from compas.geometry import Frame
from tool import Tool

class Robot:
    def __init__(self, name='/rob1', tool=None, wobj='wobj0'):
        # Create Ros Client
        self.ros_client = rrc.RosClient()
        self.ros_client.run()

        # Create ABB Client
        self.abb_client = rrc.AbbClient(self.ros_client, name)

        # Set tool
        self._tool = tool or Tool()
        self.abb_client.send(rrc.SetTool(self._tool._name))
        self.abb_client.send(self.tool.release)

        # Set work object
        self._wobj = wobj
        self.abb_client.send(rrc.SetWorkObject(wobj))

        print('Connected.')

    # Move
    def move_to_home(self):
        self.abb_client.send_and_wait(rrc.MoveToFrame(Frame([500, 500, 500], [-1, 0, 0]), 100, rrc.Zone.Z20, rrc.Motion.JOINT))

    def move_to_exact(self, frame):
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.FINE, rrc.Motion.JOINT))

    def move_to_smooth(self, frame):
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.Z200, rrc.Motion.JOINT))

    def move_and_grab(self, frame):
        point = frame.point
        frame_above = Frame([point.x, point.y, point.z + 50], [-1, 0, 0])

        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.Z200, rrc.Motion.JOINT))
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.FINE, rrc.Motion.LINEAR))
        self.grab()
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.Z200, rrc.Motion.JOINT))

    def move_and_release(self,frame):
        point = frame.point
        frame_above = Frame([point.x, point.y, point.z + 50], [-1, 0, 0])

        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.Z200, rrc.Motion.JOINT))
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.FINE, rrc.Motion.LINEAR))
        self.release()
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.Z200, rrc.Motion.JOINT))

    def where(self):
        print(self.abb_client.send_and_wait(rrc.GetFrame()))

    def shutdown(self):
        self.ros_client.close()
        self.ros_client.terminate()

        print('Disconnected.')


    # Tool stuff
    @property
    def tool(self):
        return self._tool
    
    @tool.setter
    def tool(self, tool):
        if isinstance(tool, Tool):
            self._tool = tool
            self.abb_client.send(rrc.SetTool(tool.name))
        
    def grab(self):
        self.abb_client.send(self.tool.grab)

    def release(self):
        self.abb_client.send(self.tool.release)
