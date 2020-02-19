import os
import sys
import getopt

from amiwrapper import AmiWrapper

# print("PID: ", os.getpid(), "; continue? [y]")
# answer = input()
# if answer != 'y':
#     exit(0)

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\msvs\dll\x64\Debug\mf6.dll"
mf6_config_file = r"d:\checkouts\modflow6-examples\mf6\test012_WaterTable\mfsim.nam"
max_iter = 1000

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

# time loop
while current_time < end_time:
    mf6.prepare_timestep()

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

    mf6.finalize_timestep()
    current_time = mf6.get_current_time()

mf6.finalize()

os.chdir(old_dir)
