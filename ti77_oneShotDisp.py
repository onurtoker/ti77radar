# TI 77GHz Radar sample code

import ti77radar
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, ifft, fftshift, fftfreq

tir = ti77radar.Device('awr1642')
tir.config(NS = 256)

tir.clear_buffer()          # clear kernel UDP buffer
tir.capture_frame()         # capture all RX channels

# generate a subplot for each receive antenna
fig, axv = plt.subplots(2,2)

for k in range(tir.rx):
    s = tir.get_channel(k)  # get channel k data from captured info

    sI=np.real(s)
    sQ=np.imag(s)
    axv[k//2, k%2].plot(np.array(range(tir.NS)), sI, 'b-')
    axv[k//2, k%2].plot(np.array(range(tir.NS)), sQ, 'r-')
    axv[k//2, k%2].grid()

plt.show()
