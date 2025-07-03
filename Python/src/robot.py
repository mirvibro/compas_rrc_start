import compas_rrc as rrc
from compas.geometry import Frame, Projection, Plane, Transformation
from tool import Tool
from compas_rrc import PulseDigital
import time

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
        self.tool.release()

        # Set work object
        self._wobj = wobj
        self.abb_client.send(rrc.SetWorkObject(wobj))

        print('Connected.')


    #------------HRI-----------#

    def enableLeadThrough(self):
        self.abb_client.send_and_wait(rrc.SetDigital('ABB_Scalable_IO_0_DO3', 0))
        self.abb_client.send_and_wait(rrc.CustomInstruction("r_USER_enableLeadThrough"))

    def disableLeadThrough(self):
        self.abb_client.send_and_wait(rrc.SetDigital('ABB_Scalable_IO_0_DO3', 1))
        self.abb_client.send_and_wait(rrc.CustomInstruction("r_USER_disableLeadThrough"))


    # Move
    def move_to_home(self):
        if(self.where() != Frame([500, 500, 500], [-1, 0, 0])):
            self.abb_client.send_and_wait(rrc.MoveToFrame(Frame([500, 500, 500], [-1, 0, 0]), 100, rrc.Zone.Z20, rrc.Motion.JOINT))

    def move_to_exact(self, frame):
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.FINE, rrc.Motion.JOINT))

    def move_to_smooth(self, frame):
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.Z200, rrc.Motion.JOINT))

    def move_and_grab(self, frame):
        point = frame.point
        xaxis = frame.xaxis
        yaxis = frame.yaxis
        frame_above = Frame([point.x, point.y, point.z + 100], xaxis, yaxis)

        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.FINE, rrc.Motion.JOINT))
        self.abb_client.send_and_wait(rrc.WaitTime(1))
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.FINE, rrc.Motion.LINEAR))
        self.grab()
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.Z200, rrc.Motion.LINEAR))

    def move_confirm_grab(self, frame, offset, get_transformation=False):

        """ pick-up movement with user-confirmation before each block """

        point = frame.point
        xaxis = frame.xaxis
        yaxis = frame.yaxis
        frame_above = Frame([point.x, point.y, point.z + offset], xaxis, yaxis)

        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.FINE, rrc.Motion.JOINT))
        self.enableLeadThrough() # enables hand-guiding with lead-through mode
        input("Press any Button to confirm position correction and disable hand-guiding")
        print("Correction confirmed. Disabling hand-guiding!")

        corrected_frame = self.abb_client.send_and_wait(rrc.GetFrame()) # gets the hand-adjusted frame

        # projects frame to xy-plane to level it horizontally:
        plane = Plane([0, 0, 0], [0, 0, 1])
        P = Projection.from_plane(plane)

        x_proj = corrected_frame.xaxis.copy()
        x_proj.transform(P)
        x_proj.unitize()

        y_proj = corrected_frame.yaxis.copy()
        y_proj.transform(P)
        y_proj.unitize()

        new_frame_above = Frame(corrected_frame.point, x_proj, y_proj) # horizontal frame above pick-up location after hand adjustment
        new_frame = Frame([new_frame_above.point.x, new_frame_above.point.y, new_frame_above.point.z - offset], x_proj, y_proj) # pick-up frame after hand-adjustment

        time.sleep(0.5)
        self.disableLeadThrough() # disables lead-through
        self.abb_client.send_and_wait(rrc.MoveToFrame(new_frame, 100, rrc.Zone.FINE, rrc.Motion.LINEAR))
        self.grab()
        self.abb_client.send_and_wait(rrc.MoveToFrame(new_frame_above, 100, rrc.Zone.Z200, rrc.Motion.LINEAR))

        initial_transformation = Transformation.from_frame_to_frame(frame, new_frame) #getting the transformation for adjustment of subsequent targets
        
        if get_transformation:
            return initial_transformation

    def move_and_release(self,frame):
        point = frame.point
        xaxis = frame.xaxis
        yaxis = frame.yaxis
        frame_above = Frame([point.x, point.y, point.z + 100], xaxis, yaxis)

        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.FINE, rrc.Motion.JOINT))
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame, 100, rrc.Zone.FINE, rrc.Motion.LINEAR))
        self.release()
        self.abb_client.send_and_wait(rrc.MoveToFrame(frame_above, 100, rrc.Zone.Z200, rrc.Motion.LINEAR))

    def where(self):
        return self.abb_client.send_and_wait(rrc.GetFrame())

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
        self.abb_client.send(self.tool.grab())

    def release(self):
        self.abb_client.send(self.tool.release())
