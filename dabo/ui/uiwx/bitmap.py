# -*- coding: utf-8 -*-
import wx
import dabo
import dabo.ui
from . import controlmixin as cm
from . import imagemixin as dim
from dabo.dLocalize import _
from . import icons
from dabo.ui import makeDynamicProperty


class dBitmap(cm.dControlMixin, dim.dImageMixin, wx.StaticBitmap):
	"""Creates a simple bitmap control to display images on your forms."""
	def __init__(self, parent, properties=None, attProperties=None, *args, **kwargs):
		self._baseClass = dBitmap
		preClass = wx.StaticBitmap
		picName = self._extractKey((kwargs, properties, attProperties), "Picture", "")

		dim.dImageMixin.__init__(self)
		cm.dControlMixin.__init__(self, preClass, parent, properties=properties,
				attProperties=attProperties, *args, **kwargs)

		if picName:
			self.Picture = picName
