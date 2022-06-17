from operator import index
import sys
from matplotlib.pyplot import axis
import warnings
import pandas as pd
import numpy as np
from scipy.sparse.csgraph import reverse_cuthill_mckee
from scipy.sparse import csr_matrix
import matplotlib.pylab as plt


class Dataset:
    '''
    This class is built to prepare the before-inspected Dataset
    and start to make some operations on it (BandMatrix, building 
    of sensitive transaction dataset and so on).
    '''
    dataset = None
    n_dataset = None
    items = None
    n_items = None
    s_items_set = None
    n_sensitive_items = None
    band_matrix = None
    sensitive_label = None
    list_item = None
    label_list = None
    sensitive_trans = pd.DataFrame()
    label_list = list()
    sensitiveDF = None


    def __init__(self, dataset, list_items_path):
        """Constructor method"""
        if (dataset is None):
            print("[ERROR]")
            sys.exit(1)
        else:
            self.dataset = dataset
            self.list_item = np.genfromtxt(list_items_path, dtype=np.int)
            self.n_items = len(self.list_item)
            self.dataset.columns = range(0, self.n_items)
            self.n_dataset = self.dataset.shape[0]
            self.items = self.list_item
            warnings.filterwarnings(action='ignore')
    
    def random_sensitive_items(self):
        """
        Used to extract n sensitive random items
        """
        bound = range(0,len(self.items))
        self.s_items_set=np.random.permutation(bound)[:self.n_sensitive_items]


    def make_sensitive_transaction(self,square_mtrx):
        """
        Function that construct the "Sensitive Dataset" from the square matrix
        
        :param square_mtrx: square matrix after random permutations
        """
        for item in self.s_items_set:
            #pd.concat([self.sensitive_trans[item],square_mtrx[item].copy()],axis =1)
            self.sensitive_trans[item] = square_mtrx[item].copy() 
            self.dataset.drop(columns=item, axis=1, inplace=True)
            #self.dataset.drop[item]
            self.label_list.append(self.items[item])
        self.sensitive_label = np.array(self.label_list)
        self.list_item = np.delete(self.list_item, self.s_items_set)

    def reform_items(self): # Un-necessary
        """
        Function that only take into account the transaction with the 
        sensitive items involved in.
        
        :return :new dataframe with the sensitive transactions inside
        """    
        self.list_item = np.concatenate((self.list_item, self.sensitive_label))
        
        
    def make_only_sensitive(self):
        """
        Function that build a new dataframe with only the sensitive transaction on it
        """
        self.sensitiveDF = self.sensitive_trans[(self.sensitive_trans != 0).any(1)]
      
        
    def make_band_matrix(self, dim_final=None, n_sensitive_items=None):
        """
        Function that build a band matrix with reverse_cuthill_mckee algorithm
        """
        print("[2] I'm making the BandMatrix")
        if((dim_final is None) | (n_sensitive_items is None)):
            print("ERROR")
            sys.exit(1)
        else:
            ds = self.dataset
            self.n_sensitive_items = n_sensitive_items
            if (len(ds) >= dim_final and len(ds.columns) >= dim_final):
                np.random.seed(seed=20)
                rnd_row = np.random.permutation(ds.shape[0])[:dim_final]
                rnd_col = np.random.permutation(ds.shape[1])[:dim_final]
                square_mtrx = ds.iloc[rnd_row][rnd_col]
            elif (len(ds) >= dim_final):
                np.random.seed(seed=20) # To delete the randomness 
                rnd_row = np.random.permutation(ds.shape[0])
                ds = ds.iloc[rnd_row][:dim_final]
                ds = ds.reset_index()
                ds.drop('index',axis=1,inplace=True)
                columns = ds.columns
                data_to_add = np.zeros(shape=(len(ds),len(ds)-len(columns)))
                columns_to_add = ["temp"+str(x) for x in range(0,len(ds)-len(columns))]
                df_to_add = pd.DataFrame(data_to_add, columns=columns_to_add, index=ds.index,dtype='uint8')
                ds = pd.concat([ds, df_to_add], axis=1)
                rnd_col = np.random.permutation(ds.shape[1])
                rnd_row = np.random.permutation(ds.shape[0])
                ds.columns = [i for i in range(0, len(ds.columns))]
                square_mtrx = ds.iloc[rnd_row][rnd_col] 
                
            self.random_sensitive_items()
            self.make_sensitive_transaction(square_mtrx=square_mtrx) 
            
            graph = csr_matrix(square_mtrx)
            new_order = reverse_cuthill_mckee(graph)
            column_reordered = [square_mtrx.columns[i] for i in new_order]
            self.band_matrix = square_mtrx.iloc[new_order][column_reordered]
            self.band_matrix.index = range(0, len(self.band_matrix.index))
            # Graph Part:    
            f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)
            f.suptitle('Band Matrix after reverse_cuthill_mckee algorithm')
            ax1.set_title("Dataset")
            ax2.set_title("Band Matrix")
            ax1.spy(square_mtrx, marker='.', markersize='1')
            ax2.spy(self.band_matrix, marker='.', markersize='1', markeredgecolor='red')
            plot = input("Do you want to plot the result? [y/n] ")
            #plot = "n"
            if ((plot=="y") | (plot == "Y")):
                plt.show()
            # Bandwidth before RCM algorithm
            i, j = graph.nonzero()
            default_bandwidth = (i - j).max() + 1
            # Bandwidth after RCM algorithm
            i, j = self.band_matrix.to_numpy().nonzero()
            band_bandwidth = (i - j).max() + 1
            print("------------Band Matrix Info----------")
            print(f"Bandwidth before RCM: {default_bandwidth}")
            print(f"Bandwidth after RCM: {band_bandwidth}")
            print(f"Bandwidth reduction: {default_bandwidth - band_bandwidth}")
            print("---------------------------------------")
            self.compute_sensitive()
            self.reform_items()
        
        
    def compute_sensitive(self):
        """
        This function build two dictionary:
        - sensitive_histogram: keeps track of the number of the sensitive transaction in the dataset
        - sensitive_rows: keeps track of the sensitive rows contained in the dataset
        """
        self.make_only_sensitive() # Used to make the partition only with sensistive stuff
        sensitive_hist = dict()
        sensitive_rows = dict()
        sens_rows, sens_col = self.sensitiveDF.to_numpy().nonzero()
        for item in self.sensitiveDF.columns.values:
            sensitive_hist[item] = 0
        for i in range(0, len(sens_rows)):
            active_sensitive_column = self.sensitiveDF.columns.values[sens_col[i]]
            active_sensitive_rows = self.sensitiveDF.index.values[sens_rows[i]]
            sensitive_hist[active_sensitive_column] += 1
            if active_sensitive_rows not in sensitive_rows:
                sensitive_rows[active_sensitive_rows] = list()
            sensitive_rows[active_sensitive_rows].append(active_sensitive_column)
        self.sensitive_rows = sensitive_rows
        self.sensitive_hist = sensitive_hist