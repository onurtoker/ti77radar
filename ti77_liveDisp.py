# TI 77GHz Radar sample code

import ti77radar
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numpy.fft import fft, ifft, fftshift, fftfreq

# TI radar
tir = ti77radar.Device('awr1642')
tir.config(NS = 256)

# Figure
fig = plt.figure()
ax = plt.axes(xlim=(0, tir.NS), ylim=(-500, 500))
[line1, line2] = ax.plot([], [], 'b-', [], [], 'r-')

def init():
    line1.set_xdata(np.arange(tir.NS))
    line2.set_xdata(np.arange(tir.NS))
    return [line1, line2]

def animate(i):
    try:
        tir.clear_buffer()
        # f = tir.capture_frame()
        f = tir.average_frames(8)
        s = np.matmul(np.ones((1,tir.rx)), f)
        #s = tir.get_channel(0)
        s = s.reshape((-1,))
        sI = np.real(s)
        sQ = np.imag(s)
    except:
        sI = sQ = np.zeros(tir.NS)
    line1.set_ydata(sI)
    line2.set_ydata(sQ)
    return [line1, line2]

anim = FuncAnimation(fig, animate, init_func=init, interval=100, blit=True)

plt.show()

