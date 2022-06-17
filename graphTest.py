
import matplotlib.pyplot as plt

# 1000 items 
# 10 sensitive items
# alpha = 3

# BMS1
privacy = [4, 6, 8, 10, 12, 14, 16]
time_lista = [20, 39, 98, 132, 166, 201, 230]
kl_value = [0.29, 0.32, 0.42, 0.46, 0.53, 0.62, 0.75]

# Execution time plot
plt.subplot(1, 2, 1)
plt.grid(True)
plt.suptitle("Execution and Kl value of BMS1")
plt.plot(privacy, time_lista, marker='o',linestyle='--',color='b')
plt.title("Execution Time (BMS1)  ")
plt.xlabel("Privacy")
plt.ylabel("Time (sec)")
# Kl value plot:
plt.subplot(1, 2, 2)
plt.grid(True)
plt.plot(privacy, kl_value, marker='o',linestyle='--',color='b')
plt.title("KL value")
plt.xlabel("Privacy")
plt.ylabel("KL")
plt.show()

# BMS2
time_lista = [45, 96, 146, 200, 257, 311, 370]
kl_value = [0.036, 0.041, 0.050, 0.063, 0.074, 0.089, 0.098]

# Execution time plot:
plt.subplot(1, 2, 1)
plt.grid(True)
plt.suptitle("Execution and Kl value of BMS2")
plt.plot(privacy, time_lista, marker='o',linestyle='--',color='g')
plt.title("Execution Time (BMS2)  ")
plt.xlabel("Privacy")
plt.ylabel("Time (sec)")
# Kl value plot:
plt.subplot(1, 2, 2)
plt.grid(True)
plt.plot(privacy, kl_value, marker='o',linestyle='--',color='g',)
plt.title("KL value")
plt.xlabel("Privacy")
plt.ylabel("KL")
plt.show()