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
    _scenario_focus = None
    _school_focus = None
    _social_distance_focus = None
    _case_matrix_df = None
    _focus_matrix_df = None

    def __init__(self,filepath=None):
        super().__init__()
        if filepath is None:
            pass
        else:
            self._root_group = self.open_file(filepath)

    def open_file(self,file_path):
        return  h5py.File(file_path,'r')

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
        for name,value in self._root_group.items():
            if isinstance(value,h5py.Group):
               self._groups[name] = value
            else:
                self._datasets[name] = value
        print(f'{self._datasets.keys()}')
        # extract run counts
        self._num_scenarios       = self._datasets['Run_scenario_end'][()].astype('int')[0][0]
        self._num_school_policies = self._datasets['Run_school_end'][()].astype('int')[0][0]
        self._num_social_dist_policies = self._datasets['Run_social_distance_end'][()].astype('int')[0][0]
        self._num_sto_times = self._datasets['RunStoTimes_end'][()].astype('int')[0][0]
        # extract focus vectors - convert to python list
        self._scenario_focus = (self._datasets['Run_scenario_Focus'][()].T).astype('int')[0].tolist()
        self._school_focus = (self._datasets['Run_school_Focus'][()].T).astype('int')[0].tolist()
        self._social_distance_focus = (self._datasets['Run_social_distance_Focus'][()].T).astype('int')[0].tolist()
        # extract full case matrix - store as pandas dataset
        sInd2 = self._datasets['strategyInd2'][()]
        cols = ['CUPi','scen','schl','sodi','stoT']
        self._case_matrix_df = pd.DataFrame(sInd2.T.astype('int'),columns = cols) 
        # pull the rows of case matrix corresponding to the focus matrix
        logicv = pd.Series([ False for i in range(self._case_matrix_df.shape[0])])
        tempsc = logicv.copy()
        for x in self._scenario_focus:
            tempsc = tempsc | (self._case_matrix_df['scen'] == x)
        tempsch = logicv.copy()
        for x in self._school_focus:
            tempsch = tempsch | (self._case_matrix_df['schl'] == x)
        tempsdi = logicv.copy()
        for x in self._social_distance_focus:
            tempsdi = tempsdi | (self._case_matrix_df['sodi'] == x)
        self._focus_matrix_df = self._case_matrix_df[tempsc & tempsch & tempsdi]
        # Get a handle on the actual data
        self._Fitness = self._root_group['FitnessEs3']
        #parse out the focus matrix data. Examine parts of Fitness that
        #match the rows of the focus matrix. Build an outcomes dataframe
        #append the output columns to the focus matrix dataframe.
        outrow = []
        outcomes = []
        for CUPi in (self._focus_matrix_df['CUPi'].values - 1):
            CUPidataset = self._root_group[self._Fitness[CUPi][0]]
            for item in CUPidataset[()].tolist():
                for i in item:
                    outrow.append(self._root_group[i][()])
                outcomes.append(outrow) 
        outcomedf = pd.DataFrame(outcomes)
        print(f'{outcomedf} thing')
        return len(self._groups),len(self._datasets)