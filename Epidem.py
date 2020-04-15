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
import numpy as np
class Epidem:
    """
    A container class for epidemiological data.

    Attributes
    ----------
    Filepath : str
        fill path to a .mat file
    
    Methods
    -------
    Read_file(filename=None) 
        reads the file in filepath or the one passed in
    """


    def __init__(self,filepath=None):
        super().__init__()
        self._root_group = None
        self._groups = {}
        self._datasets = {}
        self._num_scenarios = 0
        self._num_school_policies = 0
        self._num_social_dist_policies = 0
        self._scenario_focus = None
        self._school_focus = None
        self._social_distance_focus = None
        self._case_matrix_df = None
        self._focus_matrix_df = None
        self._outcome_df = None
        self._outcome_points = 0
        self._outcome_locations = 0
        self._outcome_risks = 0
        self._outcome_ages = 0
        self._number_of_outcomes = 0
        if filepath is None:
            pass
        else:
            self._root_group = self.open_file(filepath)
            self.parse_metadata()
    
    @property
    def NumberOfOutcomes(self):
        return self._number_of_outcomes
    
    @property
    def NumberOfAgegroups(self):
        return self._outcome_ages

    @property
    def NumberOfRisks(self):
        return self._outcome_risks

    @property
    def NumberOfLocations(self):
        return self._outcome_locations
    
    @property
    def NumberOfDataPoints(self):
        return self._outcome_points
        
    
    @property
    def NumberOfScenarios(self):
        return self._num_scenarios

    @property
    def NumberOfSchoolPolicies(self):
        return self._num_school_policies

    @property
    def NumberOfSocDistPolicies(self):
        return self._num_social_dist_policies

    @property
    def NumberOfFocusScenarios(self):
        if self._scenario_focus is none:
            return 0
        else:
            return len(self._scenario_focus)

    @property
    def NumberOfFocusSchoolPolicies(self):
        if self._school_focus is None:
            return 0
        else:
            return len(self._school_focus)

    @property
    def NumberOfFocusSocDistPolicies(self):
        if self._social_distance_focus is None:
            return 0
        else:
            return len(self._social_distance_focus)


    def open_file(self,file_path):
        return  h5py.File(file_path,'r')

    def parse_metadata(self):
        """Parses the file metadata. Collects groups and datasets in the root group

        There is no metadata. The metadata stored in the class is derived from the contents
        of the file. This method parses the high level attributes in the .mat file. It populates some
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
        outrow = [] # row of subdataset names of dataset associated with CUPi
        outcomes = {} # dictionary of rows of names
        for CUPi in (self._focus_matrix_df['CUPi'].values - 1):
            CUPidataset = self._root_group[self._Fitness[CUPi][0]]
            #print(f'{CUPi} {CUPidataset.name}')
            for item in CUPidataset[()].tolist():
                subname = self._root_group[item[0]].name
                outrow.append(subname)
            outcomes[CUPi+1] = outrow.copy()
            outrow.clear()
        self._outcome_df = pd.DataFrame(outcomes).T # dataframe of datasets names
        self._number_of_outcomes = self._outcome_df.shape[1]
        #print(f'{self._outcome_df} outcome_df shape')
        # Now we need the shape of an outcome so we can populate the
        # risks, age groups, locations, and points.
        # use the last subname found above to determine the shape 
        temp = self._root_group[subname]
        self._outcome_risks = temp.shape[0]
        self._outcome_ages = temp.shape[1]
        self._outcome_locations = temp.shape[2]
        self._outcome_points = temp.shape[3]
        # load tempMG the list of CBSA codes
        self._CBSA_codes = self._root_group['tempMG'][()].astype('int')[0]
    ##
    def _CBSA_index(self,CBSA):
        """Returns the index into the tempMG array of the given CBSA
        The index is decremented by one to account for c style indexint
        """
        return np.where(self._CBSA_codes == CBSA)[0][0] -1 # c indexing
    ###
    def get_outcome(self,outcome,scen,school,sodi,risk,age,location):
        """Return a dataframe with the desired contents

        outcome - outcome number 
        scen - scenario number
        school - school policy
        sodi - social distance policy
        risk  - risk number whatever that is
        age - age group number
        location - location number

        The data are assembled based on the content of the passed parameters. Data
        summation occures for multiple values of a parameter. """
        # find run CUPi by combination of scen,school,sodi
        fmdf = self._focus_matrix_df
        # test to see if the input to the function is valid
        if (scen in self._scenario_focus) & (school in self._school_focus) & (sodi in self._social_distance_focus) :
            logicv = (fmdf['scen'] == scen) & (fmdf['schl'] == school) & (fmdf['sodi'] == sodi)
            CUProw = self._focus_matrix_df[logicv]['CUPi'].values[0]
            #get the dataset associated with the CUProw and outcome number
            outcomedsname = self._outcome_df.loc[CUProw][outcome]
            #print(f'{outcomedsname}')
            #get the value of the dataset associated with the outcomedsname
            outcomedataset = self._root_group[outcomedsname][()]
            outcomedataset[np.isnan(outcomedataset)] = 0
            #index into the location vector.
            city_index = self._CBSA_index(location)
            #assemble the data from the dataset.
            thisoutcome = outcomedataset[risk,age,city_index,:].T
            cols = [str(item) for item in age]
            print(cols)
            return pd.DataFrame(thisoutcome,columns = cols)
        else:
            raise ValueError