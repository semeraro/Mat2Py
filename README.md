# Mat2Py
A python package for reading specific matlab mat files from specific simulations. There is a module associated with each simulation. Python objects in the module are specific to the simulation output. 

>The contents of the package are not guaranteed to work. (Now warranty expressed or implied). The output of the simulations can and often does change over time. The python objects are not meant to be *full featured* in that some content in the matfile may not be read by the reader. Some effort will be made to keep the readers up to date as time allows. 



## Depends 

1. Pandas
2. h5py
3. numpy

## Modules

1. COVID2DataFrame - Python objects that read the output of a Matlab epidemiology code from the Meyers Lab at University of Texas.  

