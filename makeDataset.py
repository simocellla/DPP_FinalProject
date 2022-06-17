import pandas as pd
import numpy as np
import csv
import sys
from pathlib import Path



class makeDataset:
    
    '''
    This class is built to manage (and build at the startup) all the proprieties of the Dataset that
    we want to anonymize.
    '''
    # Proprieties:
    delimitier = None 
    dataset = None  
    n_dataset = None  
    n_items = None  
    transactions_matrix = None  
    items = list()
    item_set = set()
    # Files:
    transaction_csv_path = None 
    items_path = None 
    
    def __init__(self, dataset_path=None, delimitier=None, transaction_csv_path=None, items_path=None, dim_finale=None):
        """Constructor method"""
        """
        :param dataset_path: path of the Dataset
        :param delimitier: stopper-row of the process
        """
        print("[1] I'm preparing the dataset's files")
        self.transaction_csv_path = transaction_csv_path
        self.items_path = items_path
        self.delimitier = delimitier
        self.dim_finale = dim_finale
        if self.delimitier is None:
            self.delimitier = 10000
            print("Auto setted : Delimitier = ",self.delimitier," lines")
        if dataset_path is None:
            print("Error, no able to find the file of the dataset. Check and try again")
            sys.exit(1)
        with open(dataset_path) as dataset_file:
            n_lines = 0
            for lines in dataset_file:
                n_lines+=1
        print("---------------Main Info---------------")
        d = Path(dataset_path)
        print("Working Dataset:",str(d.stem))
        print("Transactions in the Dataset file:",n_lines)
        self.make_files(dataset_path)
        

    def make_files(self, ds_scv=None):
        """
        Build all the necessary files for the project, from the dataset
        file this function will allows us to make the items set 
        and the transaction matrix.
        
        :param ds_scv: csv file that contains all the transactions.
        """
        with open(ds_scv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            n_line = 0
            for row in csv_reader:
                for col in row:
                    if col not in self.item_set:
                        self.item_set.add(col)
                n_line += 1
                # Break the loop with the delimiter number:
                if n_line == self.delimitier :
                    break
            csv_file.close()
            
        for elem in self.item_set: 
            self.items.append(elem)
            
        self.n_items = len(self.item_set)
        print("Number of items in the DataSet:", self.n_items)
        with open(self.items_path, 'w+') as item_file:
            for i in range(0, self.n_items - 1):
                item_file.write("%s\n" % self.items[i])
            item_file.write("%s" % self.items[self.n_items-1])
            item_file.close()
            
        " Working on Transaction Matrix"
        self.transaction_matrix = np.zeros((n_line, self.n_items))
        with open(ds_scv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            n_line = 0
            for row in csv_reader:
                for col in row:
                    self.transaction_matrix[n_line][self.items.index(col)] = 1
                n_line += 1
                if n_line == self.delimitier:
                    break
            csv_file.close()
        # Build the transaction Matrix, made by zeros and ones
        with open(self.transaction_csv_path, 'w') as t:
            for row in range(0, n_line-1):
                for col in range(0, self.n_items-1):
                    t.write("%s," % int(self.transaction_matrix[row][col]))
                t.write("%s\n" % int(self.transaction_matrix[row][self.n_items-1]))
            for col in range(0, self.n_items - 1):
                t.write("%s," % int(self.transaction_matrix[n_line - 1][col]))
            t.write("%s" % int(self.transaction_matrix[n_line - 1][self.n_items - 1]))
            t.close()
            
        self.dataset = pd.read_csv(self.transaction_csv_path, header=None, index_col=None)
        self.n_dataset = self.dataset.shape[0]
        # Information printing:
        print("Shapes of the Dataset: ",self.dataset.shape[0],self.dataset.shape[1])
        print("---------------------------------------")