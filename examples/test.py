import os
import sys
from xmipy import XmiWrapper
import getopt
import numpy as np


# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\bin\libmf6d.dll"
mf6_config_file = r"d:\Data\Models\mf6\small_models\ex_10x10\mfsim.nam"

# parse arguments
try:
    opts, args = getopt.getopt(sys.argv[1:], "i:s:")
except getopt.GetoptError as err:
    print(err)
    print("usage: run.py -i <configuration_file> -s <shared_library>")
    sys.exit(1)

for o, a in opts:
    if o == "-i":
        mf6_config_file = a
    elif o == "-s":
        mf6_dll = a

# for debugging
debug_native = True
if debug_native:
    print("PID: ", os.getpid(), "; continue? [y]")
    answer = input()
    if answer != "y":
        exit(0)

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)
mf6 = XmiWrapper(mf6_dll)

# write output to screen:
mf6.set_int("ISTDOUTTOFILE", 1)

mf6.initialize(mf6_config_file)
gtype = mf6.get_grid_type(1)
try:
    gtype = mf6.get_grid_type(2)
except Exception as e:
    print(e)

grank = mf6.get_grid_rank(1)
gshape = np.zeros(grank, dtype=np.int32)
mf6.get_grid_shape(1, gshape)
print(gshape)

gx = np.ones(gshape[-1] + 1, dtype=np.double)
mf6.get_grid_x(1, gx)
print(gx)

gy = np.ones(gshape[-2] + 1, dtype=np.double)
mf6.get_grid_y(1, gy)
print(gy)

mf6.update()
mf6.finalize()

# return
os.chdir(old_dir)
