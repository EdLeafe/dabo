import wx, dabo
import dControlMixin as cm
import dDataControlMixin as dcm
import dEvents
from dabo.dLocalize import _

class dSpinner(wx.SpinCtrl, dcm.dDataControlMixin, cm.dControlMixin):
	""" Allows editing integer values.
	"""
	def __init__(self, parent, id=-1, name="dSpinner", style=0, *args, **kwargs):

		self._baseClass = dSpinner

		pre = wx.PreSpinCtrl()
		self._beforeInit(pre)                  # defined in dPemMixin
		pre.Create(parent, id, name, style=style|pre.GetWindowStyle(), *args, **kwargs)

		self.PostCreate(pre)

		cm.dControlMixin.__init__(self, name)
		dcm.dDataControlMixin.__init__(self)
		self._afterInit()                      # defined in dPemMixin


	def initEvents(self):
		# init the common events:
		cm.dControlMixin.initEvents(self)
		dcm.dDataControlMixin.initEvents(self)

		# init the widget's specialized event(s):
		self.bindEvent(dEvents.Spinner, self.onSpinner)
		self.bindEvent(dEvents.Spinner, self._onSpinner)
		self.bindEvent(dEvents.Text, self.onText)
		self.bindEvent(dEvents.Text, self._onText)

	# Event callback method(s) (override in subclasses):
	def onSpinner(self, event):
		if self.debug:
			dabo.infoLog.write(_("onSpinner received by %s") % self.Name)
		event.Skip()
		
	def onText(self, event):
		if self.debug:
			dabo.infoLog.write(_("onText received by %s") % self.Name)
		event.Skip()
		
	# Private event callbacks (do not override):
	def _onSpinner(self, event):
		self.raiseEvent(dEvents.ValueChanged)
		event.Skip()
		
	def _onText(self, event):
		self.raiseEvent(dEvents.ValueChanged)
		event.Skip()
		
	# Property get/set/del methods follow. Scroll to bottom to see the property
	# definitions themselves.
	def _getMax(self):
		return self._pemObject.GetMax()
	def _setMax(self, value):
		rangeLow = self._pemObject.GetMin()
		rangeHigh = int(value)
		self._pemObject.SetRange(rangeLow, rangeHigh)

	def _getMin(self):
		return self.GetMin()
	def _setMin(self, value):
		rangeLow = int(value)
		rangeHigh = self.Max
		self.SetRange(rangeLow, rangeHigh)

	def _getSpinnerWrap(self):
		return self.hasWindowStyleFlag(wx.SP_WRAP)
	def _setSpinnerWrap(self, value):
		self.delWindowStyleFlag(wx.SP_WRAP)
		if value:
			self.addWindowStyleFlag(wx.SP_WRAP)

	def _getSpinnerArrowKeys(self):
		return self.hasWindowStyleFlag(wx.SP_ARROW_KEYS)
	def _setSpinnerArrowKeys(self, value):
		self.delWindowStyleFlag(wx.SP_ARROW_KEYS)
		if value:
			self.addWindowStyleFlag(wx.SP_ARROW_KEYS)

	# Property definitions:
	Min = property(_getMin, _setMin, None, 
						'Specifies the lowest possible value for the spinner. (int)')

	Max = property(_getMax, _setMax, None, 
						'Specifies the highest possible value for the spinner. (int)')

	SpinnerWrap = property(_getSpinnerWrap, _setSpinnerWrap, None,
						'Specifies whether the spinner value wraps at the high/low value. (bool)')

	SpinnerArrowKeys = property(_getSpinnerArrowKeys, _setSpinnerArrowKeys, None,
						'Specifies whether the user can use the arrow keys to increment. (bool)')

if __name__ == "__main__":
	import test
	test.Test().runTest(dSpinner)
