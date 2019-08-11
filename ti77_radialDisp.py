# TI 77GHz Radar sample code

import ti77radar
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, ifft, fftshift, fftfreq

tir = ti77radar.Device('awr1642')
tir.config(NS = 256)

tir.clear_buffer()          # clear kernel UDP buffer
f = tir.capture_frame()     # capture all RX channels

# FFT upscale and Rmax
Mu = 256
Rmax = 1.00

# DSP
fs = tir.fs
M = Mu * tir.NS
cf = tir.cf
fval = np.array(range(M))*fs/M
kmax = round(Rmax * M / fs / cf)

tetv=np.linspace(-np.pi/3,np.pi/3,100)
yv=0*tetv
for (k,tet) in enumerate(tetv):
    w = np.exp(1j*tet)
    s = np.matmul(np.array([w**p for p in range(tir.rx)]), f)
    s = s.reshape((-1,))
    S = fft(s, M)
    S = np.abs(S[:kmax])
    S = S / M
    yv[k] = np.max(S)

plt.plot(180/np.pi*tetv, yv)
plt.grid()
plt.show()
