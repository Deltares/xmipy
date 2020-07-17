import os
import numpy as np

import matplotlib.pyplot as plt
from xmipy import XmiWrapper

# for debugging
print("PID: ", os.getpid(), "; continue? [y]")
answer = input()
if answer != "y":
    exit(0)

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\bin\libmf6.dll"
mf6_config_file = r"d:\Data\Models\mf6\small_models\ex_10x10_ani\mfsim.nam"

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)

mf6 = XmiWrapper(mf6_dll)

# run the model
mf6.initialize(mf6_config_file)

# get some 'pointers' to MF6 internal data
head = mf6.get_value_ptr("TESTJE/X")
spdis = mf6.get_value_ptr("TESTJE NPF/SPDIS")
init_head = mf6.get_value_ptr("TESTJE IC/STRT")
rndm_head = 1.0 + np.random.rand(10, 10)
init_head = rndm_head


xorig = np.linspace(0.5, 9.5, 10) - 0.5
yorig = np.linspace(0.5, 9.5, 10) - 0.5
origin = np.meshgrid(xorig, yorig)

head_r = np.reshape(head, (10, 10))

mf6.update()

# plot stuff here:
spdis_r = 0.2 * np.reshape(spdis, (10, 10, 3))
plt.quiver(*origin, spdis_r[:, :, 0], spdis_r[:, :, 1])
plt.imshow(head_r, cmap="Blues", interpolation="nearest")
plt.show()

mf6.finalize()

os.chdir(old_dir)
