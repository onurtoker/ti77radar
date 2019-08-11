# TI 77GHz Radar sample code

import ti77radar
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numpy.fft import fft, ifft, fftshift, fftfreq

# TI radar
tir = ti77radar.Device('awr1642')
tir.config()

# FFT upscale and Rmax
Mu = 256
Rmax = 1.00

# DSP
fs = tir.fs
M = Mu * tir.NS
cf = tir.cf
fval = np.array(range(M))*fs/M
kmax = round(Rmax * M / fs / cf)

# Figure / Animation
fig = plt.figure()
ax = plt.axes(xlim=(0, Rmax), ylim=(0, 2))
ax.set_title('FFT spectrum')
ax.grid()
[line] = ax.plot([], [], 'b-')

def init():
    line.set_xdata(cf*fval[:kmax])
    return [line]

def animate(i):
    try:
        tir.clear_buffer()
        f = tir.capture_frame()
        #f = tir.average_frames(8)
        s = np.matmul(np.ones((1,tir.rx)), f)
        s = s.reshape((-1,))
        S = fft(s, M)
        S = np.abs(S[:kmax])
        S = S / M
    except:
        S = np.zeros(kmax)
    line.set_ydata(S)
    return [line]

anim = FuncAnimation(fig, animate, init_func=init, interval=100, blit=True)

plt.show()

