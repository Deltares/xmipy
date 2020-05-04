import os
from amipy import AmiWrapper

# for debugging
debug_native = True
if debug_native:
    print("PID: ", os.getpid(), "; continue? [y]")
    answer = input()
    if answer != 'y':
        exit(0)

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\bin\libmf6d.dll"
mf6_config_file = r"d:\Data\Models\mf6\small_models\ex_10x10\mfsim.nam"

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)

mf6 = AmiWrapper(mf6_dll)

# write output to screen:
mf6.set_int("ISTDOUTTOFILE", 1)

mf6.initialize(mf6_config_file)
gtype = mf6.get_grid_type(1)
try:
    gtype = mf6.get_grid_type(2)
except:
    print("exception")

mf6.update()
mf6.finalize()

# return
os.chdir(old_dir)
