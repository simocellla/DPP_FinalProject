import itertools
import operator
from math import log10 as log
import numpy as np
import pandas as pd


class KL_Divergence:
    """
    Class used for the calculation of the index of KL Divergence, according
    to what wrote on the scientific paper. 
    """
    p = None
    r = None
    band_matrix = None
    groups = None
    sensitive_rows = None
    sensitive_histogram = None


    def __init__(self, p, r, band_matrix, groups, sensitive_rows, sensitive_histogram):
        self.p = p
        self.r = r
        self.band_matrix = band_matrix
        self.groups = groups
        self.sensitive_rows = sensitive_rows
        self.sensitive_rows[-1] = []
        self.sensitive_histogram = sensitive_histogram
        self.si = self.get_max_sensitive()
        
        
    def get_all_r(self,r):
        """
        Function that calculates all the possible combination of r
        """
        lst = [list(i) for i in itertools.product([0, 1], repeat=r)]
        return lst
    
    
    def get_max_sensitive(self):
        """
        Function used to findout the most revelant sensitive item (with max occorencies).
        
        :return: sensitive item with max occurencies in the group created (from histogram)
        """
        return max(self.sensitive_histogram.items(), key=operator.itemgetter(1))[0]
    
    
    def compute_act_s_c(self, QID_chosen, row_, si):
        """
        Function that compute 'probability distribution function (pdf)'
        for each sensitive item given as argument.
        
        :param QID_chosen: QID items chosen before by random permutation
        :param row_: row_ that we need to analyze
        :param si: sensitive items with max occurencies
        
        :return: result of the division
        """
        denominator = self.sensitive_histogram[si] # Number of occurencies of SensItem
        occurrences = 0
        for row, items in self.sensitive_rows.items():
            if si in items:
                matching_row = self.band_matrix.loc[row, QID_chosen]
                if len(row_.compare(matching_row)) == 0:
                    occurrences += 1
        result = float(occurrences) / float(denominator)
        return result


    def compute_est_s_c(self, QID_chosen, row_, si):
        """
        Function that compute 'probability distribution function (pdf)'
        for each sensitive item given as argument.
        
        :param QID_chosen: QID items chosen before by random permutation
        :param row_: row_ that we need to analyze
        :param si: sensitive items with max occurencies
        
        :return: result of the division
        """
        G_cardinality = 0
        a = 1
        b = 0
        for row, group_df in self.groups.items():
            if si not in self.sensitive_rows[row]:
                continue
            G_cardinality += len(self.groups[row])
            temp_df = group_df.loc[:, QID_chosen]
            for group_row in temp_df.iterrows():
                if len(row_.compare(group_row[1])) == 0:
                    b += 1
        numerator = float(a * b) / float(G_cardinality)
        if G_cardinality == 0:
            return 0
        else:
            return numerator


    def compute_kl_divergence(self):
        """
        Function that make the summation of all the calls of the function (2^r)
        
        :return: result of KL Divergence
        """
        new_list = np.random.permutation(self.band_matrix.columns.values)
        QID_chosen = new_list[-self.r:]
        lst = self.get_all_r(self.r)
        final_result = 0.0
        for combination in lst:
            row_ = pd.Series(combination, index=QID_chosen)
            act = self.compute_act_s_c(QID_chosen, row_, self.si)
            est = self.compute_est_s_c(QID_chosen, row_, self.si)
            if est != 0 and act != 0:
                final_result += act * log(act / est)
        if(final_result < 0):
            print("[DONE] Kl-Divergence value: 0")
        else:      
            print("[DONE] Kl-Divergence value:",final_result)
        return final_result