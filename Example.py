# Example code to exercise the Epidem module. 
#
import sys,os
import matplotlib.pyplot as plt
# Need to add the path to the module 
modulepath = os.getcwd() + '\..'
sys.path.append(modulepath)
from Mat2Py.Epidem import Epidem 
filespec = "..\..\DATA\Matlab\Multi_v2_Full_COVID_cpuNum_30_March_24_737874.2655.mat"
thing = Epidem(filepath = filespec)
thing.parse_metadata()
outcome =0
scenario = 6
school_policy = 10
social_distancing = 2
risk = 0
age_group = 3
location = 35620
index = thing.get_outcome(outcome,scenario,school_policy,social_distancing,risk,age_group,location)
index.plot()
plt.show()
