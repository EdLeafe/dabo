import wx, dabo
import dControlMixin as cm
import dDataControlMixin as dcm
import dEvents
from dabo.dLocalize import _

class dCheckBox(wx.CheckBox, dcm.dDataControlMixin, cm.dControlMixin):
	""" Allows visual editing of boolean values.
	"""
	def __init__(self, parent, id=-1, name='dCheckBox', style=0, *args, **kwargs):

		self._baseClass = dCheckBox

		pre = wx.PreCheckBox()
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
		self.bindEvent(dEvents.CheckBox, self._onCheckBox)
		self.bindEvent(dEvents.CheckBox, self.onCheckBox)

	
	# Event callback methods (override in subclasses):
	def onCheckBox(self, event):
		if self.debug:
			dabo.infoLog.write(_("onCheckBox received by %s") % self.Name)
		event.Skip()
		
	# Private callback methods (do not override):
	def _onCheckBox(self, event):
		self.raiseEvent(dEvents.ValueChanged)
		event.Skip()
		
	# property get/set functions
	def _getAlignment(self):
		if self.hasWindowStyleFlag(wx.ALIGN_RIGHT):
			return 'Right'
		else:
			return 'Left'

	def _getAlignmentEditorInfo(self):
		return {'editor': 'list', 'values': ['Left', 'Right']}

	def _setAlignment(self, value):
		self.delWindowStyleFlag(wx.ALIGN_RIGHT)
		if str(value) == 'Right':
			self.addWindowStyleFlag(wx.ALIGN_RIGHT)
		elif str(value) == 'Left':
			pass
		else:
			raise ValueError, "The only possible values are 'Left' and 'Right'."

	# property definitions follow:
	Alignment = property(_getAlignment, _setAlignment, None,
						'Specifies the alignment of the text. (int) \n'
						'   Left  : Checkbox to left of text (default) \n'
						'   Right : Checkbox to right of text')
if __name__ == "__main__":
	import test
	test.Test().runTest(dCheckBox)
