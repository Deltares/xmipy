from mf6 import Mf6
import sys
import getopt

# parse arguments
mf6_dll = ""
mf6_config_file = ""
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

# load and run the model from here:
mf6 = Mf6(mf6_dll)
mf6.initialize(mf6_config_file)

current_time = mf6.get_current_time()
end_time = mf6.get_start_time()

while current_time < end_time:
    mf6.update()

mf6.finalize()


