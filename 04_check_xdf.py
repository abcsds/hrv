import pyxdf
import numpy as np
import matplotlib.pyplot as plt
from rich import print
from numpy.lib.stride_tricks import sliding_window_view

fp = "/home/beto/Desktop/exp001/block_Default.xdf"
# fp = "/home/beto/Desktop/exp001/block_Default_polar.xdf"
data, header = pyxdf.load_xdf(fp)
print(data)
rr = data[0]["time_series"]

window_sizes = [2, 5, 10, 25, 50, 100, 150]
fig, axs = plt.subplots(2 + len(window_sizes), figsize=(2*6.4, (len(window_sizes)+2)*4.8))
# Plot RR intervals
axs[0].plot(rr, label="RR intervals")
axs[0].scatter(np.arange(len(rr)), rr)
axs[0].legend()

# Plot NN intervals
nn = np.diff(rr.ravel())
axs[1].plot(nn, label="NN intervals")
axs[1].scatter(np.arange(len(nn)), nn)
# Plot scatter of NN intervals above 50 ms (Related to the PNN50)
pnn50 = len(nn[nn > 50])/len(nn)
axs[1].scatter(np.arange(len(nn))[nn > 50], nn[nn > 50], label=f"PNN50={pnn50:.2f}", c="r")
axs[1].legend()

# Sliding window SDNN
for i, window_size in enumerate(window_sizes):
    sdnn = []
    windows = sliding_window_view(rr, window_shape=window_size, axis=0)
    for window in windows:
        sdnn.append(np.std(window))
    axs[2+i].plot(sdnn, label=f"SDNN window size {window_size}")
    axs[2+i].scatter(np.arange(len(sdnn)), sdnn)
    axs[2+i].legend()

plt.show()