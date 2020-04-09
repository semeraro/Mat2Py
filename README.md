# Mat2Py
A collection of python code for reading specific matlab mat files from specific simulations. There is a class per simulation that
reads the mat file specific to that simulation. (List of sims below). The package supports .mat files written with hdf5. It uses the
h5py library to import the data. 

## Depends 

1. Pandas
2. h5py
3. numpy

## Classes

1. COVID2DataFrame - Reads the output of a matlab based epidemiology simulation of the COVID-19 virus.

