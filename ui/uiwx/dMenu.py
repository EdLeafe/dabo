""" dMenu.py """
import wx
import dPemMixin as pm
import dMenuItem
import dIcons
from dabo.dLocalize import _
import dabo.dEvents as dEvents


# wx constants for styles
NormalItemType = wx.ITEM_NORMAL
CheckItemType =  wx.ITEM_CHECK
RadioItemType = wx.ITEM_RADIO


class dMenu(wx.Menu, pm.dPemMixin):
	"""Creates a menu, which can contain submenus, menu items, and separators.
	"""
	def __init__(self, parent=None, properties=None, *args, **kwargs):
		self._baseClass = dMenu
		preClass = wx.Menu
		self.Parent = parent
		## pkm: When a dMenuItem is added to a dMenu, the wx functions only
		##      add the C++ portion, not the mixed-in dabo dMenuItem object.
		##      To work around this, we maintain an internal dictionary that
		##      maps the id of the wxMenuItem to the dMenuItem object.
		self._daboChildren = {}
		pm.dPemMixin.__init__(self, preClass, parent, properties, *args, **kwargs)


	def _initEvents(self):
		## see self._setId(), which is where the binding of wxEvents needs to take 
		## place.
		self.bindEvent(dEvents.MenuHighlight, self._onMenuHighlight)


	def _onMenuHighlight(self, evt):
		## Note that this code is here in a dabo binding instead of in the wx binding
		## because of the way we've worked around wx limitations: dMenu as a top-level
		## menu in a menu bar doesn't send wx events.
		self._setDynamicEnabled()


	def _setDynamicEnabled(self):
		"""For each dMenuItem, set Enabled per the item's DynamicEnabled prop."""
		for item in self.Children:
			# separators haven't been abstracted yet, so there are still pure wx items.
			try:
				de = item.DynamicEnabled
			except:
				de = None
			if de is not None:
				item.Enabled = de()


	def __onWxMenuHighlight(self, evt):
		self.raiseEvent(dEvents.MenuHighlight)
		evt.Skip()


	def appendItem(self, item):
		"""Insert a dMenuItem at the bottom of the menu."""
		wxItem = self.AppendItem(item)
		item.Parent = self
		self._daboChildren[wxItem.GetId()] = item
		

	def insertItem(self, pos, item):
		"""Insert a dMenuItem before the specified position in the menu."""
		self.InsertItem(pos, item)
		item.Parent = self
		self._daboChildren[wxItem.GetId()] = item
		

	def prependItem(self, item):
		"""Insert a dMenuItem at the top of the menu."""
		self.PrependItem(item)
		item.Parent = self
		self._daboChildren[wxItem.GetId()] = item


	def appendMenu(self, menu):
		"""Insert a dMenu at the bottom of the menu."""
		wxMenuItem = self.AppendMenu(-1, menu.Caption, menu, help=menu.HelpText)
		menu._setId(wxMenuItem.GetId())
		menu.Parent = self
		self._daboChildren[wxMenuItem.GetId()] = menu
		

	def insertMenu(self, pos, menu):
		"""Insert a dMenu before the specified position in the menu."""
		wxMenuItem = self.InsertMenu(-1, pos, menu.Caption, menu, help=menu.HelpText)
		menu._setId(wxMenuItem.GetId())
		menu.Parent = self
		self._daboChildren[wxMenuItem.GetId()] = menu
		
		
	def prependMenu(self, menu):
		"""Insert a dMenu at the top of the menu."""
		wxMenuItem = self.PrependMenu(-1, menu.Caption, menu, help=menu.HelpText)
		menu._setId(wxMenuItem.GetId())
		menu.Parent = self
		self._daboChildren[wxMenuItem.GetId()] = menu


	def appendSeparator(self):
		"""Insert a separator at the bottom of the menu."""
		self.AppendSeparator()
		

	def insertSeparator(self, pos):
		"""Insert a separator before the specified position in the menu."""
		self.InsertSeparator(pos)


	def prependSeparator(self):
		"""Insert a separator at the top of the menu."""
		self.PrependSeparator()
	

	def append(self, caption, bindfunc=None, help="", bmp=None, menutype="", 
				**kwargs):
		"""Append a dMenuItem with the specified properties.

		This is a convenient way to add a dMenuItem to a dMenu, give it a caption,
		help string, bitmap, and also bind it to a function, all in one call.

		Any additional keyword arguments passed will be interpreted as properties
		of the dMenuItem: if valid property names/values, the dMenuItem will take
		them on; if not valid, an exception will be raised.
		"""
		item = self._getItem(caption, bindfunc, help, bmp, menutype, **kwargs)
		self.appendItem(item)
		return item
		
	
	def insert(self, pos, caption, bindfunc=None, help="", bmp=None, menutype=""):
		"""Insert a dMenuItem at the given position with the specified properties.

		This is a convenient way to add a dMenuItem to a dMenu, give it a caption,
		help string, bitmap, and also bind it to a function, all in one call.

		Any additional keyword arguments passed will be interpreted as properties
		of the dMenuItem: if valid property names/values, the dMenuItem will take
		them on; if not valid, an exception will be raised.
		"""
		item = self._getItem(caption, bindfunc, help, bmp, menutype)
		self.insertItem(pos, item)
		return item
		

	def prepend(self, caption, bindfunc=None, help="", bmp=None, menutype=""):
		"""Prepend a dMenuItem with the specified properties.

		This is a convenient way to add a dMenuItem to a dMenu, give it a caption,
		help string, bitmap, and also bind it to a function, all in one call.

		Any additional keyword arguments passed will be interpreted as properties
		of the dMenuItem: if valid property names/values, the dMenuItem will take
		them on; if not valid, an exception will be raised.
		"""
		item = self._getItem(caption, bindfunc, help, bmp, menutype)
		self.prependItem(item)
		return item
		
		
	def remove(self, index, release=True):
		"""Removes the item at the specified index from the menu.

		If release is True (the default), the item is deleted as well. If release 
		is False, a reference to the  object will be returned, and the caller 
		is responsible for deleting it.
		"""
		item = self.Children[index]
		id_ = item.GetId()
		if self._daboChildren.has_key(id_):
			del self._daboChildren[id_]
		self.RemoveItem(item)
		if release:
			item.Destroy()
		return item


	def _getItem(self, prompt, bindfunc, help, icon, menutype, **kwargs):
		itmtyp = self._getItemType(menutype)
		itm = dMenuItem.dMenuItem(self, Caption=prompt, HelpText=help, Icon=icon, 
				kind=itmtyp, **kwargs)
		if bindfunc:
			itm.bindEvent(dEvents.Hit, bindfunc)
		return itm


	def _getItemType(self, typ):
		typ = str(typ).lower()[:3]
		ret = NormalItemType
		# This is to work around a bug in Gtk 
		if self.Application.Platform != "GTK":
			if typ in ("che", "chk"):
				ret = CheckItemType
			elif typ == "rad":
				# Currently only implemented under Windows and GTK, 
				# use #if wxHAS_RADIO_MENU_ITEMS to test for 
				# availability of this feature.
				ret = RadioItemType
		return ret


	def _setId(self, id_):
		"""wxMenus don't have ids of their own - they only get set when the 
		menu gets added as a submenu - and then it becomes a wxMenuItem with a
		special submenu flag. This hook, called from append|insert|prependMenu(),
		allows the menu event bindings to take place.
		"""
		## MenuOpen and MenuClose don't appear to be working on Linux. Need
		## to test on Mac and Win.
		if self.Application is not None:
			# Set up a mechanism to catch menu events and re-raise Dabo events. 
			# If Application is None, however, this won't work because of wx 
			# limitations.
			self.Application.uiApp.Bind(wx.EVT_MENU_HIGHLIGHT,
					self.__onWxMenuHighlight, id=id_)
		
	def _isPopupMenu(self):
		## TODO: Make dMenu work as a submenu, a child of dMenuBar, or as a popup.
		return False


	def getItemIndex(self, caption):
		"""Returns the index of the item with the specified caption.

		If the item isn't found, None is returned.
		"""
		for pos, itm in enumerate(self.Children):
			if itm.GetLabel() == caption:
				return pos
		return None
		

	def getItem(self, caption):
		"""Returns a reference to the menu item with the specified caption.

		If the item isn't found, None is returned.
		"""
		idx = self.getItemIndex(caption)
		if idx is not None:
			wxItem = self.FindItemByPosition(idx)
			if wxItem:
				return self._daboChildren.get(wxItem.GetId(), wxItem)
		return None


	def GetChildren(self):
		# wx doesn't provide GetChildren() for menubars or menus, but dPemMixin
		# calls it in _getChildren(). The Dabo developer wants the submenus and
		# items in this menu, but is using the consistent Children property to 
		# do it.
		children = self.GetMenuItems()
		daboChildren = [self._daboChildren.get(c.GetId(), c) for c in children]
		return daboChildren


	def _getCaption(self):
		try:
			v = self._caption
		except:
			v = self._caption = ""
		return v

	def _setCaption(self, val):
		if self._constructed():
			self._caption = val
			if self._isPopupMenu():
				self.SetTitle(val)
		else:
			self._properties["Caption"] = val


	def _getEnabled(self):
		return self.IsEnabled()

	def _setEnabled(self, val):
		if self._constructed():
			self.Enable(bool(val))
		else:
			self._properties["Enabled"] = val


	def _getForm(self):
		return self.Parent.Form


	def _getHelpText(self):
		try:
			v = self._helpText
		except AttributeError:
			v = self._helpText = ""
		return v

	def _setHelpText(self, val):
		self._helpText = val


	def _getParent(self):
		try:
			v = self._parent
		except AttributeError:
			v = self._parent = None
		return v

	def _setParent(self, val):
		self._parent = val

		
	Caption = property(_getCaption, _setCaption, None,
		_("Specifies the text of the menu."))

	Enabled = property(_getEnabled, _setEnabled, None,
		_("Specifies whether the menu can be interacted with."))

	Form = property(_getForm, None, None,
		_("Specifies the form that contains the menu."))

	HelpText = property(_getHelpText, _setHelpText, None,
		_("Specifies the help text associated with this menu. (str)"))

	Parent = property(_getParent, _setParent, None, 
		_("Specifies the parent menu or menubar."))
