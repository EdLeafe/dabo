import sys, os
import dabo.ui
dabo.ui.loadUI("wx")
import dabo.dEvents as dEvents
from reportWriter import ReportWriter


class BandLabel(dabo.ui.dPanel):
	def afterInit(self):
		self._dragging = False
		self._dragStart = (0,0)
		self._dragImage = None


	def initEvents(self):
		self.bindEvent(dEvents.Paint, self.onPaint)
		self.bindEvent(dEvents.MouseLeftDown, self.onLeftDown)
		self.bindEvent(dEvents.MouseLeftUp, self.onLeftUp)
		self.bindEvent(dEvents.MouseLeftDoubleClick, self.onDoubleClick)
		self.bindEvent(dEvents.MouseEnter, self.onMouseEnter)
		self.bindEvent(dEvents.MouseMove, self.onMouseMove)


	def onMouseMove(self, evt):
		import wx  ## need to abstract DC and mouse cursors!!
		if self._dragging:
			self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
			pos = evt.EventData["mousePosition"]

			if pos[1] != self._dragStart[1]:
				ypos = (self.Parent.Top + self.Top + pos[1] 
				     - self._dragStart[1]    ## (correct for ypos in the band)
				     + 2)                    ## fudge factor


				if ypos < self.Parent.Top:
					# Don't show the band dragging above the topmost valid position:
					ypos = self.Parent.Top

				if self._dragImage is None:
					# Erase the band label, and instantiate the dragImage rendition of it.
					dc = wx.WindowDC(self)
					dc.Clear()

					self._dragImage = wx.DragImage(self._captureBitmap,
					                               wx.StockCursor(wx.CURSOR_HAND))

					self._dragImage.BeginDragBounded((self.Parent.Left, ypos), 
					                                 self, self.Parent.Parent)
					self._dragImage.Show()

				self._dragImage.Move((self.Parent.Left,ypos))



	def onLeftUp(self, evt):
		dragging = self._dragging
		self._dragging = False
		if dragging:
			if self._dragImage is not None:
				self._dragImage.EndDrag()
			self._dragImage = None
			pos = evt.EventData["mousePosition"]
			starty = self._dragStart[1]
			currenty = pos[1]
			yoffset = currenty - starty
			if yoffset != 0:
				z = self.Parent.Parent._zoom
				# dragging the band is changing the height of the band.
				oldHeight = self.Parent._rw.getPt(self.Parent.getProp("height"))
				newHeight = oldHeight + (yoffset/z)
				if newHeight < 0: newHeight = 0
				self.Parent.setProp("height", newHeight)
			self.Form.Refresh()

	def onLeftDown(self, evt):
		if not self.Parent.getProp("designerLock"):
			self._dragging = True
			self._dragStart = evt.EventData["mousePosition"]
			self._captureBitmap = self.getCaptureBitmap()


	def onMouseEnter(self, evt):
		import wx		## need to abstract mouse cursor

		if self.Parent.getProp("designerLock"):
			self.SetCursor(wx.NullCursor)
		else:
			self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))


	def onDoubleClick(self, evt):
		self.Parent.propertyDialog()


	def onPaint(self, evt):
		import wx		## (need to abstract DC drawing)
		dc = wx.PaintDC(self)
		rect = self.GetClientRect()
		font = self.Font

		dc.SetTextForeground(self.ForeColor)
		dc.SetBrush(wx.Brush(self.BackColor, wx.SOLID))
		dc.SetFont(font)
		dc.DrawRectangle(rect[0],rect[1],rect[2],rect[3])
		rect[0] = rect[0]+5
		rect[1] = rect[1]+1
		dc.DrawLabel(self.Caption, rect, wx.ALIGN_LEFT)


	def _getCaption(self):
		try:
			c = self._caption
		except:
			c = self._caption = ""
		return c

	def _setCaption(self, val):
		self._caption = val

	Caption = property(_getCaption, _setCaption)


class Band(dabo.ui.dPanel):
	def afterInit(self):
		self._rd = self.Form.editor
		self._rw = self._rd._rw
		self._objects = []
		self._bandLabelHeight = 18
		self.Bands = self._rw.Bands
		self.BackColor = (255,255,255)
		self.Top = 100
		self.addObject(BandLabel, "bandLabel", FontSize=9, 
		               BackColor=(215,215,215), ForeColor=(128,128,128),
		               Height=self._bandLabelHeight)

	def initEvents(self):
		self.bindEvent(dEvents.MouseLeftClick, self.onLeftClick)


	def onLeftClick(self, evt):
		self._rd._selectedObjects = []
		self._rd.Refresh()


	def drawObjects(self):
		for o in self._objects:
			o.Destroy()
		self._objects = []
		if self.props.has_key("objects"):
			for obj in self.props["objects"]:
				o = self.getObject(obj)
				self._objects.append(o)
	
	def getObject(self, obj):
		class ObjectPanel(dabo.ui.dPanel):
			def afterInit(self):
				self._rd = self.Form.editor
				self._rw = self._rd._rw
				self.props = obj

			def initEvents(self):
				self.bindEvent(dEvents.Paint, self.onPaint)
				self.bindEvent(dEvents.MouseLeftClick, self.onLeftClick)
				self.bindEvent(dEvents.MouseMove, self.onMouseMove)
				self.bindEvent(dEvents.MouseEnter, self.onMouseEnter)
				self.bindEvent(dEvents.MouseLeave, self.onMouseLeave)

			def onMouseLeave(self, evt):
				import wx
				self.SetCursor(wx.NullCursor)	

			def onMouseEnter(self, evt):
				self._setMouseCursor(evt.EventData["mousePosition"])

			def onMouseMove(self, evt):
				self._setMouseCursor(evt.EventData["mousePosition"])

			def _setMouseCursor(self, pos):
				import wx
				if self.Selected:
					if self._mouseOnAnchor(pos):
						self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
					else:
						self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENWSE))
				else:
					self.SetCursor(wx.NullCursor)					

			def _mouseOnAnchor(self, pos):
				retval = False
				for v in self._anchors.values():
					vv = []
					for x in range(self._anchorThickness):
						for y in range(self._anchorThickness):
							vv.append((v[2]+x,v[3]+y))						
					if pos in vv:
						retval = True
						break
				return retval

			def onLeftClick(self, evt):
				if not self.Selected:
					self._rd._selectedObjects = [self,]
					self._rd.Refresh()

			def onPaint(self, evt):
				import wx		## (need to abstract DC drawing)
				dc = wx.PaintDC(self)
				rect = self.GetClientRect()
				dc.SetBrush(wx.Brush(self.BackColor, wx.SOLID))
				if self.Selected:
					# border around selected control with sizer boxes:
					dc.DrawRectangle(rect[0]+1,rect[1]+1,rect[2]-2,rect[3]-2)
					dc.SetBrush(wx.Brush(self.ForeColor, wx.SOLID))

					x,y = (rect[0], rect[1])
					width, height = (rect[2], rect[3])
					thickness = 3

					if self.props.has_key("hAnchor"):
						hAnchor = eval(self.props["hAnchor"])
					else:
						hAnchor = self._rw.default_hAnchor

					if self.props.has_key("vAnchor"):
						vAnchor = eval(self.props["vAnchor"])
					else:
						vAnchor = self._rw.default_vAnchor

					anchors = {"tl": ["top", "left", x, y],
					           "bl": ["bottom", "left", x, y + height - thickness],
					           "tc": ["top", "center", x+(.5*width), y],
					           "bc": ["bottom", "center", x+(.5*width), y+height-thickness],
					           "tr": ["top", "right", x+width-thickness, y],
					           "br": ["bottom", "right", x+width-thickness, y+height-thickness],}

					self._anchors = anchors
					self._anchorThickness = thickness

					pen = dc.GetPen()

					for k,v in anchors.items():
						if hAnchor == v[1] and vAnchor == v[0]:
							dc.SetBrush(wx.Brush((192,0,192), wx.SOLID))
							dc.SetPen(wx.Pen((192,0,192)))
						else:
							dc.SetBrush(wx.Brush(self.ForeColor, wx.SOLID))
							dc.SetPen(pen)
						dc.DrawRectangle(v[2], v[3], thickness, thickness)
				else:
					# border around unselected control
					dc.DrawRectangle(rect[0],rect[1],rect[2],rect[3])

			def _getSelected(self):
				return self in self._rd._selectedObjects
			
			def _setSelected(self, val):
				if val:
					self._rd._selectedObjects.append(self)
				else:
					for idx in range(len(self._rd._selectedObjects)):
						if self._rd._selectedObjects[idx] == self:
							del self._rd._selectedObjects[idx]
							break
				self.Refresh
					
					
			Selected = property(_getSelected)

		o = ObjectPanel(self)
		rw = self.Parent._rw
		z = self.Parent._zoom

		if obj.has_key("x"):
			x = rw.getPt(eval(obj["x"]))
		else:
			x = rw.default_x

		if obj.has_key("y"):
			y = rw.getPt(eval(obj["y"]))
		else:
			y = rw.default_y
		y = ((self.Height - self._bandLabelHeight)/z) - y

		if obj.has_key("width"):
			width = rw.getPt(eval(obj["width"]))
		else:
			width = rw.default_width

		if obj.has_key("height"):
			height = rw.getPt(eval(obj["height"]))
		else:
			height = rw.default_height

		if obj.has_key("hAnchor"):
			hAnchor = eval(obj["hAnchor"])
		else:
			hAnchor = rw.default_hAnchor

		if obj.has_key("vAnchor"):
			vAnchor = eval(obj["vAnchor"])
		else:
			vAnchor = rw.default_vAnchor

		if hAnchor == "right":
			x = x - width
		elif hAnchor == "center":
			x = x - (width/2)

		if vAnchor == "top":
			y = y + height
		elif vAnchor == "center":
			y = y + (height/2)

		o.Size = (z*width, z*height)
		o.Position = (z*x, (z*y) - o.Height)
		return o

	def getProp(self, prop):
		"""Evaluate and return the specified property value."""
		try:
			val = eval(self.props[prop])
		except KeyError:
			val = None
		return val


	def setProp(self, prop, val, sendPropsChanged=True):
		"""Set the specified object property to the specified value.

		If setting more than one property, self.setProps() is faster.
		"""
		self.props[prop] = str(val)
		if sendPropsChanged:
			self.Parent.propsChanged()

	def setProps(self, propvaldict):
		"""Set the specified object properties to the specified values."""
		for p,v in propvaldict.items():
			self.setProp(p, v, False)
		self.Parent.propsChanged()


	def propertyDialog(self):
		band = self
		class PropertyDialog(dabo.ui.dDialog):
			def afterInit(self):
				self.Accepted = False

			def addControls(self):
				try:
					lock = eval(band.props["designerLock"])
				except KeyError:
					lock = False

				self.addObject(dabo.ui.dLabel, Name="lblHeight", Caption="Band Height:",
				               Alignment="Right", Width=125)
				self.addObject(dabo.ui.dTextBox, Name="txtHeight", Width=200, 
				               Value=band.props["height"])
				self.addObject(dabo.ui.dCheckBox, Name="chkLock", Caption="Lock", Value=lock)
			
				h = dabo.ui.dSizer("h")
				h.append(self.lblHeight, "fixed", alignment=("middle", "right"))
				h.append(self.txtHeight, alignment=("middle", "right"), border=5)
				h.append(self.chkLock, alignment=("middle", "right"), border=5)
				self.Sizer.append(h, border=5)

				self.addObject(dabo.ui.dButton, Name="cmdAccept", Caption="&Accept",
				               DefaultButton=True)
				self.addObject(dabo.ui.dButton, Name="cmdCancel", Caption="&Cancel",
				               CancelButton=True)

				self.cmdAccept.bindEvent(dEvents.Hit, self.onAccept)
				self.cmdCancel.bindEvent(dEvents.Hit, self.onCancel)
				self.bindKey("enter", self.onAccept)

				h = dabo.ui.dSizer("h")
				h.append(self.cmdAccept, border=5)
				h.append(self.cmdCancel, border=5)
				self.Sizer.append(h, border=5, alignment="right")

			def onAccept(self, evt):
				self.Accepted = True
				self.Visible = False

			def onCancel(self, evt):
				self.Accepted = False
				self.Visible = False


		dlg = PropertyDialog(self.Form, 
		                     Caption="%s Properties" % self.bandLabel.Caption)
		dlg.show()

		if dlg.Accepted:
			self.setProps({"height": dlg.txtHeight.Value,
			               "designerLock": str(dlg.chkLock.Value)})

	def _getCaption(self):
		return self.bandLabel.Caption

	def _setCaption(self, val):
		self.bandLabel.Caption = val

	Caption = property(_getCaption, _setCaption)


class ReportDesigner(dabo.ui.dScrollPanel):
	def afterInit(self):
		self._bands = []
		self._rulers = {}
		self._selectedObjects = []
		self._zoom = self._normalZoom = 1.3
		self.BackColor = (192,192,192)
		self.clearReportForm()

		self.Form.bindEvent(dEvents.Resize, self._onFormResize)

	
	def clearReportForm(self):
		"""Called from afterInit and closeFile to clear the report form."""
		for o in self._rulers.values():
			o.Destroy()
		self._rulers = {}
		for o in self._bands:
			o.Destroy()
		self._bands = []
		self._rw = ReportWriter()
		self.ReportForm = None


	def promptToSave(self):
		"""Decides whether user should be prompted to save, and whether to save."""
		result = True
		if self._rw._isModified():
			result = dabo.ui.dMessageBox.areYouSure("Save changes to file %s?" 
			                                        % self._fileName)
			if result:
				self.saveFile()
		return result


	def promptForFileName(self, prompt="Select a file"):
		"""Prompt the user for a file name."""
		import wx   ## need to abstract getFile()
		try:
			dir_ = self._curdir
		except:
			dir_ = ""
	
		dlg = wx.FileDialog(self, 
			message = prompt,
			defaultDir = dir_, 
			wildcard="Dabo Report Forms (*.rfxml)|*.rfxml|All Files (*)|*")

		if dlg.ShowModal() == wx.ID_OK:
			fname = dlg.GetPath()
		else:
			fname = None
		dlg.Destroy()
		return fname


	def promptForSaveAs(self):
		"""Prompt user for the filename to save the file as.
		
		If the file exists, confirm with the user that they really want to
		overwrite.
		"""
		while True:
			fname = self.promptForFileName(prompt="Save As")
			if fname is None:
				break
			if os.path.exists(fname):
				r = dabo.ui.dMessageBox.areYouSure("File '%s' already exists. "
					"Do you want to overwrite it?" % fname, defaultNo=True)
					
				if r == None:
					# user canceled.
					fname = None
					break
				elif r == False:
					# let user pick another file
					pass
				else:
					# User chose to overwrite fname
					break
			else:
				break
		
		return fname


	def saveFile(self, fileSpec=None):
		if fileSpec == None:
			fileSpec = self._rw.ReportFormFile
			if fileSpec is None:
				fileSpec = self.promptForSaveAs()
				if fileSpec is None:
					return False
				else:
					self._fileName = fileSpec
		else:
			self._fileName = fileSpec
		xml = self._rw._getXMLFromForm(self._rw.ReportForm)
		file = open(fileSpec, "w")
		file.write(xml)
		file.close()
		self._rw._setMemento()
		self.setCaption()


	def closeFile(self):
		result = self.promptToSave()

		if result is not None:
			self._rw.ReportFormFile = None
			self.clearReportForm()
		return result


	def setCaption(self):
		"""Sets the form's caption based on file name, whether modified, etc."""
		if self._rw._isModified():
			modstr = "* "
		else:
			modstr = ""
		self.Form.Caption = "%s%s: %s" % (modstr,
		                                  self.Form._captionBase,
			                                self._fileName)

	def newFile(self):
		if self.closeFile():
			self._rw.ReportForm = self._rw._getEmptyForm()
			self.initReportForm()
			self._fileName = "< New >"
			self.setCaption()

	def openFile(self, fileSpec):
		if os.path.exists(fileSpec):
			if self.closeFile():
				self._rw.ReportFormFile = fileSpec
				self.initReportForm()
				self._fileName = fileSpec
				self.setCaption()
		else:
			raise ValueError, "File %s does not exist." % fileSpec


	def initReportForm(self):
		"""Called from openFile and newFile when time to set up the Report Form."""
		self.ReportForm = self._rw.ReportForm
		self._rw.UseTestCursor = True
		self._rw.write()

		self._rulers = {}
		self._rulers["top"] = self.getRuler("h")
		self._rulers["bottom"] = self.getRuler("h")

		for band in ("pageHeader", "detail", "pageFooter"):
			self._rulers["%s-left" % band] = self.getRuler("v")
			self._rulers["%s-right" % band] = self.getRuler("v")
			b = Band(self, Caption=band)
			b.props = self.ReportForm[band]
			b._rw = self._rw
			self._bands.append(b)

		self.drawReportForm()


	def propsChanged(self):
		"""Called by subobjects to notify the report designer that a prop has changed."""
		self.setCaption()
		self.drawReportForm()
		
	def _onFormResize(self, evt):
		self.drawReportForm()

	def drawReportForm(self):
		"""Resize and position the bands accordingly."""
		rw = self._rw
		rf = self._rw.ReportForm
		z = self._zoom

		if rf is None:
			return

		pageWidth = rw.getPageSize()[0] * z
		ml = rw.getPt(eval(rf["page"]["marginLeft"])) * z
		mr = rw.getPt(eval(rf["page"]["marginRight"])) * z
		mt = rw.getPt(eval(rf["page"]["marginTop"])) * z
		mb = rw.getPt(eval(rf["page"]["marginBottom"])) * z
		bandWidth = pageWidth - ml - mr

		tr = self._rulers["top"]
		tr.Length = pageWidth

		for index in range(len(self._bands)):
			band = self._bands[index]
			band.Width = bandWidth
			b = band.bandLabel
			b.Width = band.Width
		
			bandCanvasHeight = z * (band._rw.getPt(eval(band.props["height"])))
			band.Height = bandCanvasHeight + b.Height
			b.Top = band.Height - b.Height

			if index == 0:
				band.Top = mt + tr.Height
			else:
				band.Top = self._bands[index-1].Top + self._bands[index-1].Height

			lr = self._rulers["%s-left" % band.Caption]
			lr.Length = bandCanvasHeight
			
			rr = self._rulers["%s-right" % band.Caption]
			rr.Length = bandCanvasHeight

			band.Left = ml + lr.Thickness
			lr.Position = (0, band.Top)
			rr.Position = (lr.Width + pageWidth, band.Top)
			totPageHeight = band.Top + band.Height

			band.drawObjects()

		u = 10
		totPageHeight = totPageHeight + mb

		br = self._rulers["bottom"]
		br.Length = pageWidth

		tr.Position = (lr.Width,0)
		br.Position = (lr.Width, totPageHeight)
		totPageHeight += br.Height

		self.SetScrollbars(u,u,(pageWidth + lr.Width + rr.Width)/u,totPageHeight/u)


	def getRuler(self, orientation):
		defaultThickness = 10
		defaultLength = 1

		class Ruler(dabo.ui.dPanel):
			def afterInit(self):
				self.BackColor = (192,128,192)
				self._orientation = orientation[0].lower()

			def _getThickness(self):
				if self._orientation == "v":
					val = self.Width
				else:
					val = self.Height
				return val

			def _setThickness(self, val):
				if self._orientation == "v":
					self.Width = val
				else:
					self.Height = val
				
			def _getLength(self):
				if self._orientation == "v":
					val = self.Height
				else:
					val = self.Width
				return val

			def _setLength(self, val):
				if self._orientation == "v":
					self.Height = val
				else:
					self.Width = val
			
			Length = property(_getLength, _setLength)
			Thickness = property(_getThickness, _setThickness)

		return Ruler(self, Length=defaultLength, Thickness=defaultThickness)


class ReportDesignerForm(dabo.ui.dForm):
	def afterInit(self):
		self._captionBase = self.Caption = "Dabo Report Designer"
		self.Sizer = None
		self.addObject(ReportDesigner, Name="editor")
		self.fillMenu()
		self.bindEvent(dEvents.Close, self.onClose)

	def getCurrentEditor(self):
		return self.editor

	def onClose(self, evt):
		result = self.editor.closeFile()
		if result is None:
			evt.stop()
		
	def onFileNew(self, evt):
		o = self.editor
		if o._rw.ReportFormFile is None and not o._rw._isModified():
			# open in this editor
			o = self
		else:
			# open in a new editor
			o = ReportDesignerForm(self.Parent)
			o.Size = self.Size
			o.Position = self.Position + (20,20)
		o.editor.newFile()
		o.Show()

	def onFileOpen(self, evt):
		o = self.editor
		fileName = o.promptForFileName("Open")
		if fileName is not None:
			if o._rw.ReportFormFile is None and not o._rw._isModified():
				# open in this editor
				o = self
			else:
				# open in a new editor
				o = ReportDesignerForm(self.Parent)
				o.Size = self.Size
				o.Position = self.Position + (20,20)
			o.editor.newFile()
			o.Show()
			o.editor.openFile(fileName)

	def onFileSave(self, evt):
		self.editor.saveFile()
		
	def onFileClose(self, evt):
		result = self.editor.closeFile()
		if result is not None:
			self.Close()
		
	def onFileSaveAs(self, evt):
		fname = self.editor.promptForSaveAs()
		if fname:
			self.editor.saveFile(fname)
			
	def onViewZoomIn(self, evt):
		ed = self.getCurrentEditor()
		ed._zoom = ed._zoom + .1
		ed._onFormResize(None)

	def onViewZoomNormal(self, evt):
		ed = self.getCurrentEditor()
		ed._zoom = ed._normalZoom
		ed._onFormResize(None)

	def onViewZoomOut(self, evt):
		ed = self.getCurrentEditor()
		ed._zoom = ed._zoom - .1
		ed._onFormResize(None)

	def fillMenu(self):
		mb = self.MenuBar
		fileMenu = mb.getMenu("File")
		viewMenu = mb.getMenu("View")
		dIcons = dabo.ui.dIcons
				
		fileMenu.prependSeparator()

		fileMenu.prepend("Save &As", bindfunc=self.onFileSaveAs, bmp="saveAs", 
                     help="Save under a different file name")

		fileMenu.prepend("&Save\tCtrl+S", bindfunc=self.onFileSave, bmp="save",
		                 help="Save file")

		fileMenu.prepend("&Close\tCtrl+W", bindfunc=self.onFileClose, bmp="close",
		                 help="Close file")

		fileMenu.prepend("&Open\tCtrl+O", bindfunc=self.onFileOpen, bmp="open",
		                 help="Open file")

		fileMenu.prepend("&New\tCtrl+N", bindfunc=self.onFileNew, bmp="new",
		                 help="New file")

		viewMenu.appendSeparator()

		viewMenu.append("Zoom &In\tCtrl++", bindfunc=self.onViewZoomIn, 
		                bmp="zoomIn", help="Zoom In")

		viewMenu.append("&Normal Zoom\tCtrl+/", bindfunc=self.onViewZoomNormal, 
		                bmp="zoomNormal", help="Normal Zoom")

		viewMenu.append("Zoom &Out\tCtrl+-", bindfunc=self.onViewZoomOut, 
		                bmp="zoomOut", help="Zoom Out")

if __name__ == "__main__":
	app = dabo.dApp()
	app.MainFormClass = None
	app.setup()
	if len(sys.argv) > 1:
		for fileSpec in sys.argv[1:]:
			form = ReportDesignerForm(None)
			form.editor.openFile("%s" % fileSpec)
			form.Show()
	else:
		form = ReportDesignerForm(None)
		form.editor.newFile()
		form.Show()
	app.start()
