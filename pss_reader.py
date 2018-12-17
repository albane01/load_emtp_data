"""
Copyright 2018 Albane Schwob 
"""

import re

class PssParams(dict):
    """
    reads a .pss file associated to a parametric Simulation
    creates a dictionnary containing parameters and associated number of values
    """ 

    def __init__(self, path):
        super(PssParams, self).__init__()
        self._first_time = True
        self._extend_list_name = False
        self._extend_list_values = False
        self._count_variation_group = 0
        self.ord_keys = [[]]
        self._values = [[]]
        self._load_pss(path)
        self._filter()

    def _load_pss(self, path):
        f = open(path, 'r')
        for line in f:
            self._read(line)


    def _read(self, line):
        """ 
        reads the pss file with is a correputed XML file
        """
        if '<VariationGroup>' in line:
            if self._first_time:
                self._first_time = False
            else:
                self._count_variation_group += 1
                self._extend_list_name = True
                self._extend_list_values = True
        if '<Name>' in line:
            if self._extend_list_name:
                self.ord_keys.append([re.split('</*Name>', line)[1]])
                self._extend_list_name = False
            else:
                self.ord_keys[self._count_variation_group].append(re.split('</*Name>', line)[1])
        if '<VariationCount>' in line:
            if self._extend_list_values:
                self._values.append([int(re.split('</*VariationCount>', line)[1])])
                self._extend_list_values = False
            else:
                self._values[self._count_variation_group].append(int(re.split('</*VariationCount>', line)[1]))
        
    def _filter(self):
        """
        Reverse order of values
        """
        for table in self._values:
            table.reverse()

    def _load_dict(self):
        for i in range(len(self.ord_keys)):
            dict.__setitem__(self, self.ord_keys[i], self._values[i])
