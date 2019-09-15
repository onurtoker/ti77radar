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
gLen=100

# DSP
fs = tir.fs
M = Mu * tir.NS
cf = tir.cf
fval = np.array(range(M))*fs/M
kmax = round(Rmax * M / fs / cf)

# Figure / Animation
fig = plt.figure()
ax = plt.axes(xlim=(-gLen, 0), ylim=(0, 100))
ax.set_title('Distance (cm)')
ax.grid()
[line] = ax.plot([], [], 'b-')

def init():
    line.set_xdata(np.arange(-gLen,0))
    line.set_ydata(np.zeros(gLen))
    return [line]

def animate(i):
    try:
        tir.clear_buffer()
        #f = tir.capture_frame()
        f = tir.average_frames(8)
        s = np.matmul(np.ones((1,tir.rx)) / tir.rx, f)
        s = s.reshape((-1,))
        S = fft(s, M)
        S = np.abs(S[:kmax])
        #S = S / M
    except:
        S = np.zeros(kmax)

    dist = 100 * cf * fval[np.argmax(S)]
    line.set_ydata(np.append(line.get_ydata()[-gLen+1:], dist))
    return [line]

anim = FuncAnimation(fig, animate, init_func=init, interval=100, blit=True)

plt.show()

