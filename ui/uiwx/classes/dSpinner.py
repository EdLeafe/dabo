import wx
from dControlMixin import dControlMixin

class dSpinner(wx.SpinCtrl, dControlMixin):
    def __init__(self, parent):
        widgetId = wx.NewId()
        wx.SpinCtrl.__init__(self, parent, widgetId)
        self.SetName("dSpinner")
        dControlMixin.__init__(self)
        
        self.SetRange(-64000, 64000)
    
    def initEvents(self):
        # init the common events:
        dControlMixin.initEvents(self)
        
        # init the widget's specialized event(s):
        wx.EVT_SPINCTRL(self, self.GetId(), self.onEvent)
        wx.EVT_TEXT(self, self.GetId(), self.onEvent)

    # Event callback method(s) (override in subclasses):
    def OnSpin(self, event): pass
    def OnText(self, event): pass
    
if __name__ == "__main__":
    import test
    class c(dSpinner):
        def OnSpin(self, event): print "OnSpin!"
        def OnText(self, event): print "OnText!"
    test.Test().runTest(c)
