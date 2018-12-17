"""
Copyright 2018 Albane Schwob 
"""

# -*- coding: utf-8 -*-
import numpy as np
from scipy.io import FortranFile
import glob
from timeit import default_timer as timer
from collections import defaultdict
from matplotlib import pyplot as plt

class ParamSimulation(dict):
    """
    reads .m file, loads parameters and associated values
    determines position in .mda file of all signals in white_list
    """

    def __init__(self, mfile_path, white_list):
        super(ParamSimulation, self).__init__()
        self._mfile = mfile_path
        self._signals_to_load = []
        self._signals_and_positions = []
        self._white_list = white_list
        self._intersect_white_list_mfile = []
        self.domain = 'u' # f : frequency, t : time
        self._index_domain = 0
        # Booleans
        self._params_loaded = False
        self._domain_initialized = False
        # loads parameters of simulation
        self.load_params()

    def load_params(self):
        """
        read the .m file line by line and loads parameters and associated values
         """
        with open(self._mfile, "r") as f:
            for line in f:
                self.read(line)
        self._params_loaded = True
        self.load_signals_and_positions()
        self.intersect_white_list_mfile()

    def load_signals_and_positions(self):
        """
        loads the list of signals in white_list and their position in .mda file
        """
        for [param, link] in self._signals_to_load:
            self.load_signals_and_positions_for_specific_param(param, link)

    def read(self, line):
        if ':' in line:
            self.insert_vector(line)
        elif 'strvcat' in line:
            self.insert_strvcat(line)
        else:
            self.insert_equality(line)

    def insert(self, param, value):
        """
        inserts a key and the associated value
        """
        self.setdefault(param, []).append(value)

    def insert_equality(self, line):
        """
        for a line which is a simple equality
        inserts the key and its value
        checks that second line of .m file is already parsed if so finds domain and prepare for loading signals and positions 
        """
        self._index_domain += 1
        line = line.split("=")
        value = ((line[1].strip('\r\n')).strip(';')).strip("'")
        param = line[0]
        self.insert(param, value)
        if self._index_domain >=3:
            self.get_domain()
            self.pre_load_signals_and_positions(param, value)

    def insert_strvcat(self, line):
        """
        for a line which contains strvcat
        inserts the key and its value
        """
        line = line.split("'")
        value = line[1]
        param = line[0].split('=')[0]
        self.insert(param, value)
        self.pre_load_signals_and_positions(param, value)

    def insert_vector(self, line):
        """
        for a line which contains a vector
        inserts the key and its value
        """
        line = line.split('=')
        param = line[0]
        line = ((line[1].strip('\r\n')).strip(';')).split(':')
        line = list(map(int, line))
        value1 = line[0]
        value2 = line[2]
        value = [value1, value2]
        self.insert(param, value)

    def pre_load_signals_and_positions(self, param, signal):
        """
        if signal is in white_list, finds the link
        for param Nvn, the link is vn (for time domain) or vnmag (for frequency domain)
        for param Nis, the link is is  (for time domain) or ismag (for frequency domain)
        ...
        the link is necessary to determine its position 
        """
        if signal in self._white_list:
            link = list(param)
            link.pop(0)
            link = ('').join(link)
            if self.domain == 'f':
                link = link + 'mag'
            if [param, link] not in self._signals_to_load:
                self._signals_to_load.append([param, link])
        return self._signals_to_load

    def get_domain(self):
        """
        finds the domain (frequency or time)
        """
        if self._domain_initialized is False:
            if 'f' in self.keys():
                self.domain = 'f'
                self._domain_initialized = True
            elif 't' in self.keys():
                self.domain = 't'
                self._domain_initialized = True
            else:
                self.domain = 'u'
                print('error : domain unknown')
  
    def load_signals_and_positions_for_specific_param(self, param, link):
        """
        computes the list of signals and position for one specific parameter
        list is ordered by position of signal in white_list
        """
        index = 0
        for signal in self.get(param):
            position = self.get(link)[0][0] + index
            index += 1
            if signal in self._white_list:
                self._signals_and_positions += [(signal, position)]
        self._signals_and_positions.sort(key=lambda x: x[1])

    def intersect_white_list_mfile(self):
        """
        creates a list of signals that are both in white list and .m file
        (if user entered in the whitelist a signal that is not in the .m file, its data should not be loaded)
        """
        for signal in self._white_list:
            for (signal,line) in self._signals_and_positions:
                if signal not in self._intersect_white_list_mfile:
                    self._intersect_white_list_mfile += [signal]

    def get(self, parametre):
        """
        Returns the values of a loaded parameter
        if the .m file is not loaded, loads it
        """
        if not self._params_loaded:
            self.load_params()
        return self[parametre]

class Simulation():
    """
        loads the data of all signals in white list for a simulation
    """

    def __init__(self, mda_path, m_path, white_list):
        self._white_list = white_list
        self._mda = FortranFile(mda_path, 'r')
        self._m = ParamSimulation(m_path, white_list)
        self._data_loaded = False
        self._ft=[]
        self._ftmin = 0
        self._ft15 = 0
        self._ft16 = 0
        self._ftdelta = 0
        self._ftmax = 0
        self._data = [[0] for i in range(len(self._m._signals_and_positions))]

    def load_data(self):
        """
        loads the signals' values in data and computes overshoot
        """
        it = 0
        try:
            while True:
                mda_ft = self._mda.read_reals(dtype=np.float64)
                self._ft += [mda_ft[0]]
                for j in range(len(self._m._signals_and_positions)):
                    values = self._m._signals_and_positions[j]
                    name, line = values
                    if it==0:
                        self._data[j][it] = mda_ft[line-1]
                        self._ftmin = int(mda_ft[0])
                    if it==15:
                        self._ft15 = mda_ft[0]
                    if it==16:
                        self._ft16 = mda_ft[0]
                    else:
                        self._data[j].append(mda_ft[line-1])
                it += 1
        except TypeError:
            pass
        self._data_loaded = True
        self._ftmax = int(self._ft[-1])
        self._ftrange=int(self._ftmax-self._ftmin)
        self._ftdelta = self._ft16-self._ft15
        self._data=np.array(self._data)

    def get(self, signal):
        """
            returns the value of a signal
        """
        signal_found = False
        position_in_white_list = -1
        for element in self._m._intersect_white_list_mfile:
            position_in_white_list += 1
            if element == signal:
                signal_found = True
                return self._data[position_in_white_list]
        if signal_found is False:
            return "signal not found"

    def get_ftmin(self):
        return self._ftmin

    def get_ftmax(self):
        return self._ftmax

    def get_ftdelta(self):
        return self._ftdelta

    def get_signals_and_lines(self):
        return self._m._signals_and_lines

    def get_ft(self):
        return self._ft

    def get_data(self):
        return self._data

    def is_data_loaded(self):
        return self._data_loaded

class Simulations():
    """
        loads the data of all signals in white list for a tree of simulations
    """

    def __init__(self, simulation_path, name, white_list):
        self._white_list = white_list
        self._CP_paths = glob.glob(simulation_path+ '/CP*')
        self._nb_simu_tot = len(self._CP_paths)
        self._m_paths = []
        self._mda_paths = []
        self._overshoot_initialized = False
        self._simulations = [0] * self._nb_simu_tot
        self._ftdelta = 0
        #correction for compatibility with Windows
        i = 0
        #end of correction
        for CP_path in self._CP_paths:
            # correction for compatibility with Windows
            self._CP_paths[i] = CP_path.replace('\\','/')
            CP_path_corrected = self._CP_paths[i]
            i += 1
            #end of correction
            self._m_paths += [CP_path_corrected + '/' + name + '_pj' + '/' + name + 'm.m']
            self._mda_paths += [CP_path_corrected + '/' + name + '_pj' + '/' + name + '.mda']

    def build_all_simulations(self):
        start_loading = timer()
        print('loading data')
        index = -1
        for mda_path, m_path in zip(self._mda_paths, self._m_paths): # iterate over all simulations
            index += 1
            s = Simulation(mda_path, m_path, self._white_list) # build simulation
            self._simulations[index] = s # adds simulation in list of simulations
            s.load_data() #loads simulation
        print("total loading {}".format(timer() - start_loading))
        self.pass_simulation_parameters()
        
    def pass_simulation_parameters(self):
        self._ftdelta = self.get_simulation(0)._ftdelta
        self._ftmin = self.get_simulation(0)._ftmin

    def get_nb_simu_tot(self):
        return self._nb_simu_tot

    def get_simulation(self, index):
        return self._simulations[index]

    def get_simulations(self):
        return self._simulations
