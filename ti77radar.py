# Python module for TI 77GHz radars
# TODO: Generalize for all TI AWR/IWR devices
# TODO: Add documentation strings
import socket
import numpy as np
import math

class Device:
    # TI radar device

    # Static attributes
    EL = 1466   # expected UDP packet length
    UL = 1500   # max bytes in UDP packet (Buffer size)
    NW = 32     # no of bits for sequence number

    def __init__(self, device='awr1642'):
        # Constructor (Default device is awr1642)
        self.device = device
        self.rx = None
        self.tx = None
        self.UDP_IP = None
        self.UDP_PORT = None
        self.NS = None
        self.fs = None
        self.cf = None
        self.sock = None
        self.frame = None
        print('Device created')

    def config(self, rx=4, tx=2, UDP_IP = "192.168.33.30", UDP_PORT = 4098, NS = 256, \
                        fs=10e6, cf =0.5*3e8*1e-6/29.982e6):
        # Configuration of the ti77radar
        self.rx = rx
        self.tx = tx
        self.UDP_IP = UDP_IP
        self.UDP_PORT = UDP_PORT
        self.NS = NS
        self.fs = fs
        self.cf = cf
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            self.sock.bind((UDP_IP, UDP_PORT))
            print('Device configured')
        except:
            e = sys.exc_info()[0]
            print(e)

    @staticmethod
    def bytes_to_ints(cdata):
        # Utility function to convert bytes to np.array(dtype=np.int16)
        cl = len(cdata)
        cx = np.zeros((cl - 10) // 2, dtype=np.int16)
        ci = 0
        for k in range(10, cl, 2):
            c16 = cdata[k:k+2]
            c16 = int.from_bytes(c16, byteorder='little', signed=True)
            cx[ci] = c16
            ci = ci + 1

        return cx

    def get_channel(self, k):
        # Get channel data from captured frame info
        return self.frame[k,:]

    def average_frames(self, n):
        f = np.zeros((self.rx, self.NS))
        self.clear_buffer()
        k = 0
        while (k < n):
            try:
                f = f + self.capture_frame()
                k = k + 1
            except:
                break
        f = f / k
        self.frame = f
        return f

    def capture_frame(self):
        # Read a single frame, and return as an rx by NS matrix

        NC = math.ceil(2 * self.rx * self.NS * 4 / (self.EL - 10))

        # Read successive NC frames
        data_v = [None] * NC
        for k in range(NC):
            data_v[k], _ = self.sock.recvfrom(Device.UL)
            if not(len(data_v[k]) == Device.EL):
                raise IOError #return None
            seq_no = int.from_bytes(data_v[k][0:4], byteorder='little')
            if (k == 0):
                cseq_no = seq_no
            else:
                if ((cseq_no + 1) % (2**Device.NW) == seq_no):
                    cseq_no = seq_no
                else:
                    raise IOError #return None

        # adapted from MATLAB sample provided by TI
        lvds = np.zeros(NC * (self.EL - 10) // 4, dtype=np.complex)
        counter = 0
        for k in range(NC):
            # generate local adc_data
            adc_data = self.bytes_to_ints(data_v[k])
            for i in range(0, len(adc_data), 4):
                lvds[counter]       = adc_data[i]   + 1j * adc_data[i+2]
                lvds[counter + 1]   = adc_data[i+1] + 1j * adc_data[i+3]
                counter = counter + 2

        # find block start/end
        rn = int.from_bytes(data_v[0][4:10], byteorder='little') // 4
        dk = (-rn) % (self.rx * self.NS)

        #print(cseq_no, rn, dk, counter)

        # finally
        f = lvds[dk : dk + self.rx * self.NS]
        f = f.reshape((self.rx,-1))
        self.frame = f
        return f

    def clear_buffer(self):
        # Clear UDP buffer (Discard older data)
        self.sock.setblocking(0)
        while True:
            try:
                _, _ = self.sock.recvfrom(1500)
            except IOError:
                break
        # print('Cleaned up buffer!')
        self.sock.setblocking(1)

    def __del__(self):
        self.sock.close()

