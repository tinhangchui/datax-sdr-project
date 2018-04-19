#To run this file:
#run conda install python.app
#run pip install wxPython
#run pip install wxmplot
#then run pythonw wx_test.py

import sys
import wx
is_wxPhoenix = 'phoenix' in wx.PlatformInfo
if is_wxPhoenix:
    PyDeadObjectError = RuntimeError
else:
    from wx._core import PyDeadObjectError

import time, os, sys

import numpy as np
from numpy.fft import *
from rtlsdr import RtlSdr

from wxmplot.plotframe import PlotFrame

from rtlsdr import RtlSdr
sdr = RtlSdr()
sdr.sampling_rate = 2.4e6
sdr.center_freq = 970e5
sdr.gain = 4

class TestFrame(wx.Frame):
    def __init__(self, parent=None, *args,**kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, parent, wx.NewId(), '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kwds)
        self.SetTitle("signal test")
        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        self.plotframe  = None
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)

        #slider
        self.sld = wx.Slider(self, value = 973, minValue = 800, maxValue = 1100, style = wx.SL_HORIZONTAL)
        self.sld.Bind(wx.EVT_SLIDER, self.OnSliderScroll)

        self.Refresh()
        self.ShowPlotFrame(do_raise=False, clear=False)
        self.onStartTimer()

    def ShowPlotFrame(self, do_raise=True, clear=True):
        "make sure plot frame is enabled, and visible"
        if self.plotframe is None:
            self.plotframe = PlotFrame(self)
            self.has_plot = False
        try:
            self.plotframe.Show()
        except PyDeadObjectError:
            self.plotframe = PlotFrame(self)
            self.plotframe.Show()

        if do_raise:
            self.plotframe.Raise()
        if clear:
            self.plotframe.panel.clear()
            self.plotframe.reset_config()

    def onStartTimer(self,event=None):
        self.count = 0
        self.timer.Start(1)

    def onTimer(self, event):
        # print 'timer ', self.count, time.time()
        self.count += 1
        N_Samples = 256 * 1024
        samples = sdr.read_samples(N_Samples)

        interval = 2048
        N = N_Samples//interval * interval
        y = samples[:N]

        y = y[:len(y//interval*interval)]
        y = y.reshape(N//interval, interval)
        y_windowed = y*np.kaiser(interval, 6)
        Y = fftshift(fft(y_windowed,axis=1),axes=1)

        Pspect = np.mean(abs(Y)*abs(Y),axis=0);
        self.plotframe.plot(np.arange(0, len(Pspect), 1),Pspect)

    def OnExit(self, event):
        try:
            if self.plotframe != None:  self.plotframe.onExit()
        except:
            pass
        self.Destroy()

    def OnSliderScroll(self, e):
        obj = e.GetEventObject()
        val = obj.GetValue()
        sdr.center_freq = val * 1e5
        print("frequency: "+str(sdr.center_freq / 10e6)+"MHz")

if __name__ == '__main__':
    app = wx.App()
    f = TestFrame(None,-1)
    f.Show(True)
    app.MainLoop()
