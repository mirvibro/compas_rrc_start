# Welcome to (working title robot project dynamic (dis)assembly)

Working title robot project dynamic (dis)assembly does this and that.
A python script tells cobot ABB GoFa12 1500 127cm what to do using [compas_rrc](https://github.com/compas-rrc/compas_rrc).

Soon, a camera will be mounted on the robot, it will perform a scanning routine, which then gives a collection of pictures to be photogrammetrated and meshed. A pickup order is generated and executed.





# Installation guide

This guide is taken from the origin of this fork, the [compas_rrc_start repository](https://github.com/compas-rrc/compas_rrc_start).

## Requirements

* Windows 10 Pro 64-bit
* CPU 2 GHz
* Memory 8 GB
* Disk 10 GB SSD
* Screen 1920x1080

## Installation

### Anaconda

* [Anaconda 3](https://www.anaconda.com/products/individual#Downloads): Anaconda is an open source scientific Python distribution. With this tool, we can easily create a Python environment. Install Anaconda using default options.

### Docker
* [Docker Desktop](https://www.docker.com/products/docker-desktop): Docker is a virtualization platform. We use it to run Linux containers for ROS on Windows machines. 
* After installation, it is required to enable "Virtualization" on the BIOS of the computer. Usually this requires rebooting your computer and pressing a vendor-specific key (`F2`, `F4`, `Del` are typical options) to enter the BIOS.

### Visual Studio

* [Visual Studio Code](https://code.visualstudio.com/): We recommend VS Code as the Python editor because it offers an easy-to-use interface. With this tool you can develop your process code. 
* The following extensions are necessary:
  * [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python): Official extension to add support for Python programming, including debugging, auto-complete, formatting, etc.
  * [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker): Add support for Docker containers to VS Code.
  * [EditorConfig](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig): Add support for .editorconfig files to VS Code.
* The following extensions are recommended:
  * [vscode-pdf](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf): View PDF documents inside VS Code.
  * [RAPID ABB](https://marketplace.visualstudio.com/items?itemName=abed.vscode-rapid): Syntax highligher for RAPID files in VS Code.

### RobotStudio

* [ABB RobotStudio](https://new.abb.com/products/robotics/robotstudio): We use this tool to simulate the robot cells. Available for free on a 30-days trial version. Universities usually obtain free license packages, commercial users require paid subscriptions for robot simulation.
* After installation, start RobotStudio and navigate to the `Add-in` tab and make sure you add the following packages:
  * Latest RobotWare version for IRC5
  * Latest RobotWare version for OmniCore

## Start

### Get started

* Download or clone this repository to have all the required files on your computer

### Start the robot

* Unpack a `Pack&Go (.rspag)` file with a double-click. Files are in the `robotstudio-stations` folder.
* Navigate to the `Controller` tab and open `FlexPendant`
* Navigate to the `Simulation` tab and start the simulation (use the `Play` button in RobotStudio, not the one on the `FlexPendant`)

### Start ROS driver

* Make sure Docker Desktop is running (a Docker icon should appear in the Windows tray)
* Open VS Code and open this repository folder
* Navigate to the `docker\virtual_controller` folder
* Compose up the `docker-compose.yml` file with a right-click

### Start examples

* Make sure your [conda environment has `compas_rrc` installed](https://github.com/compas-rrc/compas_rrc#installation).
* Navigate to the `python` folder
* Run `compas_rrc_A_welcome.py`

# Thank you for your interest in COMPAS_RRC

> If you need further help, please go to the [forum](https://forum.compas-framework.org/c/compas-rrc) or contact us directly [`rrc@arch.ethz.ch`](mailto:rrc@arch.ethz.ch).
 
