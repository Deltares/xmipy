import os
import sys
import getopt

from amipy import AmiWrapper

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\msvs\dll\x64\Debug\mf6.dll"
mf6_config_file = r"d:\checkouts\modflow6-examples\mf6\test001e_UZF_3lay\mfsim.nam"

# parse arguments
try:
    opts, args = getopt.getopt(sys.argv[1:],"i:s:")
except getopt.GetoptError as err:
    print(err)
    print('usage: run.py -i <configuration_file> -s <shared_library>')
    sys.exit(1)

for o, a in opts:
    if o == "-i":
        mf6_config_file = a
    elif o == "-s":
        mf6_dll = a

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)

mf6 = AmiWrapper(mf6_dll)


# run the model
mf6.initialize(mf6_config_file)

current_time = mf6.get_current_time()
end_time = mf6.get_end_time()

while current_time < end_time:
    mf6.update()
    current_time = mf6.get_current_time()

mf6.finalize()

os.chdir(old_dir)
