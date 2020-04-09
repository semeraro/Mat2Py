""" Epidemiology Matlab output module

This module was developed to read and process the output of a matlab 
epidemiology study of the Covid-19 virus. The simulation code is not
specific to that particular virus and neither is this module. 

The matlab simulation saves output in a .mat file using hdf5. The 
classes and functions in this module process the expected output of that
simulation. 
"""

import h5py
import pandas as pd
class Epidem:
    """
    A container class for epidemiological data.

    Attrobites
    ----------
    Filepath : str
        fill path to a .mat file
    
    Methods
    -------
    Read_file(filename=None) 
        reads the file in filepath or the one passed in
    """

    _root_group = None
    _groups = {}
    _datasets = {}
    _num_scenarios = 0
    _num_school_policies = 0
    _num_social_dist_policies = 0
    def __init__(self,filepath=None):
        super().__init__()
        if filepath is None:
            pass
        else:
            _root_group = open_file(filepath,'r')

    def open_file(self,file_path):
        return = hdf5.File(file_path,'r')

    def parse_metadata(self):
        """Parses the file metadata. Collects groups and datasets in the root group

        This method parses the high level attributes in the .mat file. It populates some
        class metadata variables. The method populates two dictionaries _groups, and _datasets. 
        each element in the dict is a key value pair with the dataset name as key and the
        value of the dataset as the value. The dataset may contain a single scalar or numpy
        array reference.  

        Once populated data in key datasets needed to produce output are extracted from the
        information in the dictionaries.
        """
        for name,value in _root_group.items():
            if isinstance(value,h5py.Group):
                _groups[name] = value
            else:
                _datasets[name] = value
            # extract run counts
            _num_scenarios       = _datasets['Run_scenario_end'][()].astype('int')[0][0]
            _num_school_policies = _datasets['Run_school_end'][()].astype('int')[0][0]
            _num_social_dist_policies = _datasets['Run_social_distance_end'][()].astype('int')[0][0]
            _num_sto_times = _datasets['RunStoTimes_end'][()].astype('int')[0][0]
            # extract focus vectors - convert to python list
            _scenario_focus = (_datasets['Run_scenario_Focus'][()].T).astype('int')[0].tolist()
            _school_focus = (_datasets['Run_school_Focus'][()].T).astype('int')[0].tolist()
            _social_distance_focus = (_datasets['Run_social_distance_Focus'][()].T).astype('int')[0].tolist()
            # extract full case matrix - store as pandas dataset
            sInd2 = _datasets['strategyInd2'][()]
            cols = ['CUPi','scen','schl','sodi','stoT']
            _case_matrix_df = pd.DataFrame(sInd2.T.astype('int'),columns = cols) 
            # pull the rows of case matrix corresponding to the focus matrix
            logicv = pd.series([ False for i in range(_case_matrix_df.shape[0])])
            tempsc = logicv.copy()
            for x in _scenario_focus:
                tempsc = tempsc | (_case_matrix_df['scen'] == x)
            tempsch = logicv.copy()
            for x in _school_focus:
                tempsch = tempsch | (_case_matrix_df['schl'] == x)
            tempsdi = logicv.copy()
            for x in _social_distance_focus:
                tempsdi = tempsdi | (_case_matrix_df['sodi'] == x)
            _focus_matrix_df = _case_matrix_df[tempsc & tempsch & tempsdi]
            return len(_groups),len(_datasets)