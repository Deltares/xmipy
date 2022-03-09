import os

import matplotlib.pyplot as plt

from xmipy import XmiWrapper

# for debugging
debug_native = True
if debug_native:
    print("PID: ", os.getpid(), "; continue? [y]")
    answer = input()
    if answer != "y":
        exit(0)

# defaults
mf6_dll = r"d:\checkouts\modflow6-mjr\bin\libmf6.dll"
mf6_config_file = r"d:\Data\Models\mf6\multilayer\mfsim.nam"

# load the wrapper and cd to model dir
old_dir = os.getcwd()
model_dir = os.path.dirname(mf6_config_file)
print("\n", "Change to model directory: ", model_dir, "\n")
os.chdir(model_dir)

mf6 = XmiWrapper(mf6_dll)

# run the model
mf6.initialize(mf6_config_file)

# get some 'pointers' to MF6 internal data
head_tag = mf6.get_var_address("X", "SLN_1")
head = mf6.get_value_ptr(head_tag)
rch_tag = mf6.get_var_address("BOUND", "FLOW15", "RCH-1")
shape = mf6.get_var_shape(rch_tag)
recharge = mf6.get_value_ptr(rch_tag)
sc2_tag = mf6.get_var_address("SC2", "FLOW15", "STO")
sc2 = mf6.get_value_ptr(sc2_tag)
N_sc2 = mf6.get_var_shape(sc2_tag)
sc2reset_tag = mf6.get_var_address("IRESETSC2", "FLOW15", "STO")
update_sc2 = mf6.get_value_ptr(sc2reset_tag)
mxit_tag = mf6.get_var_address("MXITER", "SLN_1")
max_iter_arr = mf6.get_value_ptr(mxit_tag)

# at some point we would need access to this stuff as well...
nodeuser_tag = mf6.get_var_address("NODEUSER", "FLOW15", "DIS")
nodeuser = mf6.get_value_ptr(nodeuser_tag)

# time loopy
start_time = mf6.get_start_time()
current_time = mf6.get_current_time()
end_time = mf6.get_end_time()
simulation_length = end_time - current_time

# convergence
max_iter = max_iter_arr[0]

# for plotting
fig, ax = plt.subplots()
plt.ion()


(init_line,) = ax.plot(head)
plt.ylim(top=13.0)
plt.ylim(bottom=6.0)
plt.show()

while current_time < end_time:

    # modify storage
    # this is done before prepare_timestep because the conversions are done in sto_rp()
    frac = (current_time - start_time) / simulation_length
    halfway = int(N_sc2[0] / 2)
    sc2[:halfway] = 0.2
    sc2[halfway:] = (1.0 - 0.99 * frac) * 0.2
    update_sc2[0] = 1

    dt = mf6.get_time_step()
    mf6.prepare_time_step(dt)

    # modify recharge after prepare_time_step!!
    recharge[:] = 0.2

    # loop over subcomponents
    n_solutions = mf6.get_subcomponent_count()
    for sol_id in range(1, n_solutions + 1):

        # convergence loop
        kiter = 0
        mf6.prepare_solve(sol_id)
        while kiter < max_iter:
            has_converged = mf6.solve(sol_id)
            kiter += 1

            if has_converged:
                print("\n\nComponent ", sol_id, " converged in ", kiter, "iterations\n")
                break

        mf6.finalize_solve(sol_id)

        # update head in graph
        init_line.set_ydata(head)
        plt.pause(0.2)

    mf6.finalize_time_step()
    current_time = mf6.get_current_time()

mf6.finalize()

os.chdir(old_dir)
