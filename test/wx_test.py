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

from numpy import arange, sin, cos, exp, pi, linspace, ones, random

from wxmplot.plotframe import PlotFrame

class TestFrame(wx.Frame):
    def __init__(self, parent=None, *args,**kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, parent, wx.NewId(), '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kwds)
        self.SetTitle(" WXMPlot Plotting Demo")
        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        self.plotframe  = None
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)
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
        self.x = arange(0.0, 3, 0.01)
        self.y = sin(2 * pi * self.x + self.count)
        self.plotframe.plot(self.x, self.y)

    def OnExit(self, event):
        try:
            if self.plotframe != None:  self.plotframe.onExit()
        except:
            pass
        self.Destroy()

if __name__ == '__main__':
    app = wx.App()
    f = TestFrame(None,-1)
    #f.Show(True)
    app.MainLoop()
