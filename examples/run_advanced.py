import math
import os
from math import sin
import numpy as np

import matplotlib.pyplot as plt
from amipy import AmiWrapper

# for debugging
debug_native = False
if debug_native:
    print("PID: ", os.getpid(), "; continue? [y]")
    answer = input()
    if answer != 'y':
        exit(0)

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\bin\libmf6.dll"
mf6_config_file = r"d:\Data\Models\mf6\multilayer\mfsim.nam"

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)

mf6 = AmiWrapper(mf6_dll)

# run the model
mf6.initialize(mf6_config_file)

# get some 'pointers' to MF6 internal data
head = mf6.get_value_ptr("SLN_1/X")
shape = mf6.get_var_shape("FLOW15 RCH-1/BOUND")
recharge = mf6.get_value_ptr("FLOW15 RCH-1/BOUND")
storage = mf6.get_value_ptr("FLOW15 STO/SC2")
max_iter_arr = mf6.get_value_ptr("SLN_1/MXITER")

orig_storage = np.copy(storage)
storage_corr = np.copy(storage)
storage_corr[:int(storage_corr.size/2)] = 0.0
storage_corr[int(storage_corr.size/2):-1] = -0.99

# at some point we would need access to this stuff as well...
nodeuser = mf6.get_value_ptr("FLOW15 DIS/NODEUSER")


# time loop
start_time = mf6.get_start_time()
current_time = mf6.get_current_time()
end_time = mf6.get_end_time()
simulation_length = end_time - current_time

# convergence
max_iter = max_iter_arr[0]

# for plotting
fig, ax = plt.subplots()
plt.ion()


init_line, = ax.plot(head)
plt.ylim(top=10.0)
plt.ylim(bottom=6.0)
plt.show()

init_storage = storage.copy()

while current_time < end_time:
    mf6.prepare_timestep()

    # modify recharge
    recharge[:] = 0.1 #* sin(4 * math.pi * current_time / simulation_length)

    # modify storage
    frac = math.pow((current_time - start_time)/simulation_length, 0.1) # from 0 to 1
    storage[:] = (1.0 + frac*storage_corr) * orig_storage[:]

    # loop over subcomponents
    n_solutions = mf6.get_subcomponent_count()
    for sol_id in range(1,n_solutions+1):

        # convergence loop
        kiter = 0
        mf6.prepare_iteration(sol_id)
        while kiter < max_iter:
            has_converged = mf6.do_iteration(sol_id)
            kiter += 1

            if has_converged:
                print("\n\nComponent ", sol_id, " converged in ", kiter, "iterations\n")
                break

        mf6.finalize_iteration(sol_id)

        # update head in graph
        init_line.set_ydata(head)
        plt.pause(0.2)

    mf6.finalize_timestep()
    current_time = mf6.get_current_time()

mf6.finalize()

os.chdir(old_dir)
