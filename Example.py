# Example code to exercise the Epidem module. 
#
import sys,os
# Need to add the path to the module 
modulepath = os.getcwd() + '\..'
sys.path.append(modulepath)
from Mat2Py.Epidem import Epidem 
filespec = "..\..\DATA\Matlab\Multi_v2_Full_COVID_cpuNum_30_March_24_737874.2655.mat"
thing = Epidem(filepath = filespec)
thing.parse_metadata()