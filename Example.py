# Example code to exercise the Epidem module. 
#
import sys,os
import matplotlib.pyplot as plt
# Need to add the path to the module 
modulepath = os.getcwd() + '\..'
sys.path.append(modulepath)
from Mat2Py.Epidem import Epidem 
filespec = "..\..\DATA\Matlab\Multi_v2_Full_COVID_cpuNum_30_March_24_737874.2655.mat"
run = Epidem(filepath = filespec)
outcome = [item for item in range(run.NumberOfOutcomes)]
outcome = (1,2)
scenario = run.Scenarios[0]
school_policy = run.SchoolPolicies[-1]
social_distancing = run.SocialDistancePolicies[0]
risk = run.NumberOfRisks - 1
age_group = (3,4)
location = 35620
index = run.get_outcome(outcome,scenario,school_policy,social_distancing,risk,age_group,location)

print(f'{index}')
#index.plot()
#plt.show()
