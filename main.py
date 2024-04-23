#!/usr/bin/python
"""
Update a simple plot as rapidly as possible to measure speed.
"""

import argparse
from collections import deque
from time import perf_counter

import numpy as np

import pyqtgraph as pg
import pyqtgraph.functions as fn
import pyqtgraph.parametertree as ptree
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import scipy
import socket
import sine_lut

DEBUG = False

# defaults here result in the same configuration as the original PlotSpeedTest
parser = argparse.ArgumentParser()
parser.add_argument('--noise', dest='noise', action='store_true')
parser.add_argument('--no-noise', dest='noise', action='store_false')
parser.set_defaults(noise=True)
parser.add_argument('--nsamples', default=5000, type=int)
parser.add_argument('--frames', default=50, type=int)
parser.add_argument('--fsample', default=1000, type=float)
parser.add_argument('--frequency', default=0, type=float)
parser.add_argument('--amplitude', default=5, type=float)
parser.add_argument('--ip_address', default="192.168.1.100", type=str)
parser.add_argument('--port', default=5006, type=int)
parser.add_argument('--opengl', dest='use_opengl', action='store_true')
parser.add_argument('--no-opengl', dest='use_opengl', action='store_false')
parser.set_defaults(use_opengl=None)
parser.add_argument('--allow-opengl-toggle', action='store_true',
    help="""Allow on-the-fly change of OpenGL setting. This may cause unwanted side effects.
    """)
args = parser.parse_args()

if args.use_opengl is not None:
    pg.setConfigOption('useOpenGL', args.use_opengl)
    pg.setConfigOption('enableExperimental', args.use_opengl)

# don't limit frame rate to vsync
sfmt = QtGui.QSurfaceFormat()
sfmt.setSwapInterval(0)
QtGui.QSurfaceFormat.setDefaultFormat(sfmt)


class MonkeyCurveItem(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.monkey_mode = ''

    def setMethod(self, value):
        self.monkey_mode = value

    def paint(self, painter, opt, widget):
        if self.monkey_mode not in ['drawPolyline']:
            return super().paint(painter, opt, widget)

        painter.setRenderHint(painter.RenderHint.Antialiasing, self.opts['antialias'])
        painter.setPen(pg.mkPen(self.opts['pen']))

        if self.monkey_mode == 'drawPolyline':
            painter.drawPolyline(fn.arrayToQPolygonF(self.xData, self.yData))

app = pg.mkQApp("Plot Speed Test")

default_pen = pg.mkPen()

params = ptree.Parameter.create(name='Parameters', type='group')
pt = ptree.ParameterTree(showHeader=False)
pt.setParameters(params)
pw = pg.PlotWidget()
pw1 = pg.PlotWidget()

splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
splitter2 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)



splitter1.addWidget(pt)
splitter.addWidget(pw)
splitter.addWidget(pw1)

splitter.addWidget(splitter1)

splitter2.addWidget(splitter)
splitter2.addWidget(splitter1)

splitter2.show()

interactor = ptree.Interactor(
    parent=params, nest=False, runOptions=ptree.RunOptions.ON_CHANGED
)

pw.setWindowTitle('Signal: PlotSpeedTest')
pw.setLabel('bottom', 'Index', units='B')
curve = MonkeyCurveItem(pen=default_pen, brush='b')
pw.addItem(curve)
curve_fft = MonkeyCurveItem(pen=default_pen, brush='b')
pw.setWindowTitle('Signal Spectrum: PlotSpeedTest')
pw.setLabel('bottom', 'Index', units='seconds')
pw1.addItem(curve_fft)
pw1.setLabel('bottom', 'Frequency', units='Hz')


sine_wave = sine_lut.sine_wave
low_pass = sine_lut.low_pass

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.1.100', 5006)
data_prev = np.array(sine_wave[:2048]).astype(np.int32)
sock.setblocking(False)
try:
    sock.bind(server_address)
except:
    print("Already Binded with port")


def resetTimings(*args):
    elapsed.clear()



@interactor.decorate(
    nest=True,
    nsamples={'limits': [0, None]},
    Sampling_FREQ={'units': 'Hz'},
    ip_address={'ip_address': ''},
    port={'PORT': ''}
)
def makeData(nsamples=2048, Sampling_FREQ=30720000):
    global T, t, xf, fs, N 
    fs = Sampling_FREQ
    N = nsamples
    dt = 1/Sampling_FREQ
    T = nsamples * dt
    t = np.linspace(0.0, nsamples/Sampling_FREQ, nsamples)
    xf = np.linspace(0.0, (1.0*Sampling_FREQ)/(2.0), nsamples//2)
    # pw.setXRange(0,T)
    # pw.setYRange(-500,500)
    # pw1.setXRange(0,fs//2)
    # pw1.setYRange(0,(10**4))



    

params.child('makeData').setOpts(title='Plot Options')

@interactor.decorate(
    connect={'type': 'list', 'limits': ['all', 'pairs', 'finite', 'array']}
)
def update(
    antialias=pg.getConfigOption('antialias'),
    connect='all',
    skipFiniteCheck=False
):
    global data, data_prev, curve, curve_fft, data, ptr, elapsed
    
    if DEBUG:
        data = np.array(sine_wave[:N]).astype(np.int32)
    else:
        try: 
            stream, _ = sock.recvfrom(2 * N) 
            data = np.frombuffer(stream, dtype=np.int16)
            data_prev = data
        except TimeoutError:
            data = data_prev
        
            
                            
    #data = np.convolve(data, low_pass)[:N]
    data_fft = abs(scipy.fftpack.fft(data))[:N//2]
    


    curve.setData(x=t ,y=data)
    curve_fft.setData(x=xf, y=data_fft)

    pw.setTitle('SIGNAL')
    pw1.setTitle('SPECTRUM')

@interactor.decorate(
    useOpenGL={'readonly': not args.allow_opengl_toggle},
    curvePen={'type': 'pen'}
)
def updateOptions(
    curvePen=pg.mkPen(),
    useOpenGL=True,
):
    pg.setConfigOption('useOpenGL', useOpenGL)
    curve.setPen(curvePen)

params.sigTreeStateChanged.connect(resetTimings)

makeData()


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

if __name__ == '__main__':
    # Splitter by default gives too small of a width to the parameter tree,
    # so fix that right before the event loop
    # Set up UDP socket

    pt.setMinimumSize(225,0)
    pg.exec()
    sock.close()
    
