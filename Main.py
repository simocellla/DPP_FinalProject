from makeDataset import makeDataset
from Dataset import Dataset
from Algorithm import Algorithm
from KL_Divergence import KL_Divergence
import time

# Boundries:
dim_finale = 10000
dim_band_matrix = 1000
n_sensitive = 5
r = 4
p = 10
dataset_ = "BMS1"

# Files:
ds_scv = "Dataset/"+dataset_+".csv"
transaction_csv = "Dataset/"+dataset_+"_transactionMatrix.csv"
dataset_item = "Dataset/"+dataset_+"_items.txt"

'''if dataset_=="BMS2" and dim_band_matrix < dim_finale:
    if(dim_band_matrix < 1000):
        dim_finale = dim_band_matrix = 1000
    else:
        dim_finale = dim_band_matrix'''
    
start_time = time.time()
# Prepare DS:
data = makeDataset(dataset_path=ds_scv,
                delimitier=dim_finale,
                dim_finale=dim_band_matrix,
                transaction_csv_path=transaction_csv, 
                items_path=dataset_item)

# Build DS:
dataset = Dataset(data.dataset,
                list_items_path=dataset_item)
dataset.make_band_matrix(dim_final=dim_band_matrix,
                        n_sensitive_items=n_sensitive)
# Not-necessary output:
#print("Sensitive Items Extracted:",dataset.sensitive_hist) #OK
#print("Number of Sensitive Transaction: ",len(dataset.sensitiveDF))
#print("Sensitive transaction:", dataset.sensitiveDF)

# Make Groups:
groups = Algorithm(band_matrix=dataset.band_matrix,
                s_items_set=dataset.s_items_set,
                p=p,
                sensitiveDF=dataset.sensitiveDF,
                sensitive_hist=dataset.sensitive_hist,
                sensitive_rows=dataset.sensitive_rows,
                alpha=3)
dict = groups.create_groups()
end_time_groups = time.time() - start_time
print("       in ",int(end_time_groups)," sec")
print("---------------------------------------")
groups.print_groups(groups, dict)

# Make calculus of Kl Divergence:
KL = KL_Divergence(p=p, 
                band_matrix=dataset.dataset, 
                groups=dict, 
                r=r, 
                sensitive_rows=dataset.sensitive_rows, 
                sensitive_histogram=groups.histogram_KL)
KL.compute_kl_divergence()
