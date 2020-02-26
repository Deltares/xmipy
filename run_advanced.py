import math
import os
from math import sin

import matplotlib.pyplot as plt
from amiwrapper import AmiWrapper

# for debugging
print("PID: ", os.getpid(), "; continue? [y]")
answer = input()
if answer != 'y':
    exit(0)

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\msvs\dll\x64\Debug\mf6.dll"
mf6_config_file = r"d:\Data\Models\mf6\multilayer\mfsim.nam"

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)

mf6 = AmiWrapper(mf6_dll)

# run the model
mf6.initialize(mf6_config_file)

# time loop
current_time = mf6.get_current_time()
end_time = mf6.get_end_time()
simulation_length = end_time - current_time

# convergence
max_iter = mf6.get_value_ptr("SLN_1/MXITER")[0]

# for plotting
fig, ax = plt.subplots()
plt.ion()

head = mf6.get_value_ptr("SLN_1/X")
init_line, = ax.plot(head)
plt.ylim(top=12.0)
plt.ylim(bottom=0.0)
plt.show()


while current_time < end_time:
    mf6.prepare_timestep()

    # modify recharge rate for model FLOW15
    shape = mf6.get_var_shape("FLOW15 RCH-1/BOUND")
    recharge = mf6.get_value_ptr("FLOW15 RCH-1/BOUND")
    new_recharge = 0.05 * sin(4 * math.pi * current_time / simulation_length)
    recharge[0, :] = new_recharge

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
        head = mf6.get_value_ptr("SLN_1/X")
        init_line.set_ydata(head)
        plt.pause(0.1)

    mf6.finalize_timestep()
    current_time = mf6.get_current_time()

mf6.finalize()

os.chdir(old_dir)
