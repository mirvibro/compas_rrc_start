# Info
disassembly sequence routine based on input meshes from photogrammetry scan and static solver.
Utilizing compas_cra (https://github.com/blockresearchgroup/compas_cra)
Creating connectivity graph, disassembly sequence


## installation:

https://blockresearchgroup.github.io/compas_cra/latest/installation.html

**conda environment** 
working with these packages/libraries:

pythyon: 3.10.16

compas: 2.10.0

compas-assembly: 0.7.1

compas-cra: 0.50

compas-viewer: 1.4.0

compas_robots: 0.6.0

ipopt: 3.14.9

numpy: 1.24.3

pyomo: 6.4.2

shapely: 2.1.0

notes: numpy has to be uninstalled and reinstalled as python installs numpy 2.x+ as default

### ipopt solver installation:
https://github.com/coin-or/Ipopt/releases/download/releases%2F3.14.9/Ipopt-3.14.9-win64-msvs2019-md.zip
copy the complete folder structure (bin, include, lib, share) into your path\to\condaenvironment\cra\Library, for the already existing folders (like bin), copy the contents in there. restart machine.

If the ipopt solver isn't installed properly, you will get either "ipopt didn't exit normally" with error code (3221226505) in the log, or "ipopt executable not found"
