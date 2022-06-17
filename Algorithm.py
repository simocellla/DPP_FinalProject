from tokenize import group
import numpy as np
from numpy import histogram
import pandas as pd
import sys


class Algorithm:
    '''
    This class is built to buil the group of anonymization from the dataset.
    '''
    alpha = None
    p = None
    band_matrix = None
    s_items_set = None
    sensitive_histogram = None
    sensitiveDF = None
    histogram_KL = None


    def __init__(self, band_matrix, s_items_set, p, sensitiveDF, sensitive_hist, sensitive_rows, alpha=3):
        """Constructor method"""
        self.original_band_matrix = band_matrix.copy()
        self.band_matrix = band_matrix
        #self.band_matrix.index = range(0, len(self.band_matrix.index))
        self.s_items_set = s_items_set
        self.p = p
        self.alpha = alpha 
        self.QID_items = [i for i in list(self.band_matrix) if i not in self.s_items_set]
        self.group_dict = None
        self.group_list = list()
        self.sensitive_histogram = sensitive_hist.copy()
        self.sensitive_row = sensitive_rows
        self.sensitiveDF = sensitiveDF
        self.histogram_KL = sensitive_hist     
        print("[3] I'm doing the Anonymization process")
        print("---------------CAHD Info---------------")
        print("Length S_I: ", len(s_items_set))
        print("Length Q_I: ", len(self.QID_items))
        print("p = ",p)
        print("alpha = ",alpha)
        print("---------------------------------------")         
        
        
    def check_duplicates(self, list_s_added, index):
        """
        Function that checks if the sensitive items was already added 
        inside the target group.
        
        :param index: sensitive transaction to insert
        :param list_s_added: list of sensitive items already added in the groups
        :return: True if index is already inside the group, False viceversa
        """
        for sensitive_item in list_s_added:
            if index==sensitive_item:
                return True
        return False


    def privacy_chek(self, remaining):
        """
        Function that compute if the privacy degree is satisfiable
        or not
        
        :param remaining: remaining rows in the list
        :return: True if it's okay
        """
        for elem in self.sensitive_histogram.values():
            if elem * self.p > remaining:
                return False
        return True
    
    
    def qid_similar(self, sensitive_row, candidate_list):
        """
        Function that from the candidate list, select the rows that
        are going to be insert in the group based on the QID similarity.
        
        :param candidate_list: list of candidates
        :param sensitive_row: sensitive row on which we make the group
        :return: list of name of rows that are in the group
        """
        row_len_dict = dict()
        count = 0
        for row in candidate_list:
            row_len_dict[count] = len(sensitive_row.compare(row))
            count+=1
        ordered_dict = sorted(row_len_dict.items(), key=lambda kv: (kv[1], kv[0]))
        result = list()
        result.append(sensitive_row.name)
        for i in range(0, self.p-1):
            result.append(candidate_list[ordered_dict[i][0]].name)
        return result
    
    
    def populate(self, candidate_list, main_index, index):
        """
        Function that add the row(index) to the candidate list.
        
        :param candidate_list: list of candidates
        :param main_index: index of sensitive row that I'm examinating
        :param idx: candidate to enter in the list
        :return: 
            -1: addable
            -0: impossible to add
        """
        if index in self.sensitive_row:
            for sensitive_item in self.sensitive_row[main_index]:
                for other_s_items in self.sensitive_row[index]:
                    if sensitive_item == other_s_items:
                        return 0
        candidate_list[main_index].append(self.band_matrix.loc[index, :])
        return 1
    
    
    def create_groups(self):
        """
        Function that creates the Anonymized groups of transaction
        
        :return: dictionary that link the sensitive_row to the dataframe
        """
        candidate_list = dict()
        rows = self.band_matrix.index.values
        left_to_do = len(rows)
        sensitive_added = list()
        group_dict = dict()
        
        blocker = 1
        old_value = 0
        while blocker > 0:
            for j in self.sensitiveDF.index.values:
                if self.check_duplicates(sensitive_added,j):
                    continue
                tmp = self.band_matrix.loc[j,:]
                candidate_list[j] = list()
                index = np.where(rows == j)[0][0]
                pos_idx = index + 1
                neg_idx = index - 1
                counter = 0
                stop = 2 * self.alpha * self.p
                not_groupable = False
                while counter < stop:
                    if neg_idx >= 0:
                        counter += self.populate(candidate_list, j, rows[neg_idx])
                        neg_idx -= 1
                    if pos_idx < left_to_do:
                        counter += self.populate(candidate_list, j, rows[pos_idx])
                        pos_idx += 1
                    if pos_idx == left_to_do and neg_idx == -1:
                        if len(candidate_list[j]) < self.p - 1:
                            not_groupable = True
                        break
                if not_groupable:
                    continue
                list_similar = self.qid_similar(tmp,candidate_list[j])
                for i in list_similar:
                    if i in self.sensitive_row:
                        sensitive_added.append(i)
                        for si in self.sensitive_row[i]:
                            self.sensitive_histogram[si] -= 1 #decrement of histogram
                if self.privacy_chek(left_to_do):
                    for elem in list_similar:
                        rows = rows[rows != elem]
                    left_to_do = len(rows)
                    group_dict[tmp.name] = list_similar
                else:
                    for i in list_similar:
                        if i in self.sensitive_row:
                            sensitive_added.remove(i)
                            for si in self.sensitive_row[i]:
                                self.sensitive_histogram[si] += 1
            blocker = 0
            
            for hist_value in self.sensitive_histogram.items():
                blocker += hist_value[1]
            if blocker > 0 and old_value == blocker:
                print("[ERROR] Privacy degree",self.p,"not satisfiable")
                sys.exit(1)
            elif blocker > 0:
                old_value = blocker
        print("[DONE] Privacy Degree",self.p,"satisfiable")
        counter = 0
        result = dict()
        for g in group_dict:
            counter += 1
            anonymized = pd.DataFrame()
            for row in group_dict[g]:
                new = self.band_matrix.iloc[lambda x: x.index == row]
                anonymized = pd.concat([anonymized, new])
            result[g] = anonymized
        anonymized = pd.DataFrame()
        for non_sens_row_index in rows:
            new = self.band_matrix.iloc[lambda x: x.index == non_sens_row_index]
            anonymized = pd.concat([anonymized, new])
        result[-1] = anonymized
        print("       Group created:", len(result))
        return result       
    
    
    def print_groups(self, groups, group_dictionary):
        """
        Function that prints the created groups
        
        :param groups: Groups of anonymization 
        :param group_dictionary: Dictionary of all the group that the Algorithm creates.
        """
        choose = input("Do you wanna print the created groups? [y/n]")
        #choose = 'n'
        if((choose=="y") | (choose == "Y")):
            if group_dictionary != -1:
                print("[5] Printing groups")
                print("")
                counter = 0
                for row in group_dictionary:
                    counter += 1
                    if row == -1:
                        print("Group",counter,"without sensitive item:")
                    else:
                        #print("Column sensitive:",group_dictionary[row][groups.sensitive_row[row]],sep="\n")
                        print("Group",counter," with sensitive item",groups.sensitive_row[row])
                    print(group_dictionary[row])
                print("")
            else:
                print("[ERROR] in printing groups")
                sys.exit(1)
        
    def make_groups_list(self, group_dictionary):
        if group_dictionary != -1:
            for row in group_dictionary:
                self.group_list.append(group_dictionary[row])