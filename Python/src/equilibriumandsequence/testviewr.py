from PySide6.QtGui import QSurfaceFormat

fmt = QSurfaceFormat()
fmt.setRenderableType(QSurfaceFormat.OpenGL)
fmt.setVersion(2, 1)  # or 3, 2
fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
QSurfaceFormat.setDefaultFormat(fmt)

from compas_viewer import Viewer
from compas.geometry import Line, Point
from compas.colors import Color

viewer = Viewer()
viewer.scene.add(Line(Point(0, 0, 0), Point(0, 0, 10)), linecolor=Color.red(), linewidth=1)
viewer.scene.add(Line(Point(1, 0, 0), Point(1, 0, 10)), linecolor=Color.green(), linewidth=5)
viewer.scene.add(Line(Point(2, 0, 0), Point(2, 0, 10)), linecolor=Color.blue(), linewidth=15)
viewer.show()




""" from OpenGL.GL import *
from OpenGL.GLUT import *

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLineWidth(40)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-0.5, 0, 0)
    glVertex3f(0.5, 0, 0)
    glEnd()
    glFlush()

glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(400, 400)
glutCreateWindow(b"Line Width Test")
glutDisplayFunc(display)
glutMainLoop() """
