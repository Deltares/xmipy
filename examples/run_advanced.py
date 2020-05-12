import os
import matplotlib.pyplot as plt

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
sc2 = mf6.get_value_ptr("FLOW15 STO/SC2")
N_sc2 = mf6.get_var_shape("FLOW15 STO/SC2")
update_sc2 = mf6.get_value_ptr("FLOW15 STO/IRESETSC2")
max_iter_arr = mf6.get_value_ptr("SLN_1/MXITER")


# at some point we would need access to this stuff as well...
nodeuser = mf6.get_value_ptr("FLOW15 DIS/NODEUSER")


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


init_line, = ax.plot(head)
plt.ylim(top=13.0)
plt.ylim(bottom=6.0)
plt.show()

while current_time < end_time:

    # modify recharge
    recharge[:] = 0.2

    # modify storage (before prepare_timestep because the conversions are done in sto_rp()
    frac = (current_time - start_time)/simulation_length
    halfway = int(N_sc2[0]/2)
    sc2[:halfway] = 0.2
    sc2[halfway:] = (1.0 - 0.99*frac) * 0.2
    update_sc2[0] = 1

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

        # update head in graph
        init_line.set_ydata(head)
        plt.pause(0.2)

    mf6.finalize_timestep()
    current_time = mf6.get_current_time()

mf6.finalize()

os.chdir(old_dir)
