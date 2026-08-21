# Autosleep Mode: the settings panel
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""The "Autosleep Mode" category in NVDA's multi-category Settings dialog.

The panel edits a working copy of the list of applications and only writes it to
NVDA's configuration from :meth:`AutosleepSettingsPanel.onSave`, which the
Settings dialog calls when OK or Apply is pressed. Cancelling therefore leaves
the configuration exactly as it was, and the panel is built afresh every time the
dialog is opened.
"""

from typing import List, Sequence

import addonHandler
import winUser
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from . import addonConfig
from . import apps

addonHandler.initTranslation()

#: Moves the item with the caret in a list box, which a multiple selection list
#: box tracks separately from the items that are selected.
LB_SETCARETINDEX = 0x019E


class AutosleepSettingsPanel(SettingsPanel):
	# Translators: the title of the add-on's category in NVDA's Settings dialog.
	title = _("Autosleep Mode")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		#: The list of applications as it will be saved, edited in place until then.
		self._sleepApps: List[str] = addonConfig.getApps()
		#: Every application currently running, filled in by L{onPanelActivated}.
		self._runningApps: List[str] = []
		listSize = self.scaleSize((250, 150))

		self.sleepList = sHelper.addLabeledControl(
			# Translators: the label of the list of applications that are put to sleep automatically.
			_("Apps to sleep"),
			wx.ListBox,
			choices=[],
			size=listSize,
			style=wx.LB_EXTENDED,
		)
		self.sleepList.Bind(wx.EVT_LISTBOX, self._onSelectionChanged)
		self.removeButton = sHelper.addItem(wx.Button(self, label=self._removeLabel(1)))
		self.removeButton.Bind(wx.EVT_BUTTON, self._onRemove)

		self.runningList = sHelper.addLabeledControl(
			# Translators: the label of the list of applications that are running now.
			_("Running apps"),
			wx.ListBox,
			choices=[],
			size=listSize,
			style=wx.LB_EXTENDED,
		)
		self.runningList.Bind(wx.EVT_LISTBOX, self._onSelectionChanged)
		self.addButton = sHelper.addItem(wx.Button(self, label=self._addLabel(1)))
		self.addButton.Bind(wx.EVT_BUTTON, self._onAdd)

		self.addManuallySleptCheckBox = sHelper.addItem(
			wx.CheckBox(
				self,
				# Translators: an option to grow the list from the applications slept by hand.
				label=_("Add apps that are put to sleep manually to the autosleep list"),
			),
		)
		self.addManuallySleptCheckBox.SetValue(addonConfig.getAddManuallySleptApps())

		self._refreshLists()

	def onPanelActivated(self):
		# Which applications are running is only true for as long as it takes the
		# user to start or close one, so it is looked up each time the category is
		# selected rather than once when the panel is built.
		self._runningApps = apps.runningAppNames()
		self._refreshLists()
		super().onPanelActivated()

	def onSave(self):
		addonConfig.setApps(self._sleepApps)
		addonConfig.setAddManuallySleptApps(self.addManuallySleptCheckBox.IsChecked())

	# --- the two lists ------------------------------------------------------
	def _availableApps(self) -> List[str]:
		"""The running applications that are not on the list already.

		An application already listed is left out rather than shown and ignored,
		so that adding one always has an effect.
		"""
		listed = {addonConfig.normalize(app) for app in self._sleepApps}
		return [app for app in self._runningApps if addonConfig.normalize(app) not in listed]

	def _refreshLists(self, sleepIndex: int = 0, runningIndex: int = 0):
		"""Redisplay both lists, leaving the given item current in each."""
		self._fillList(self.sleepList, self._sleepApps, sleepIndex)
		self._fillList(self.runningList, self._availableApps(), runningIndex)
		self._updateButtons()

	def _fillList(self, listBox: wx.ListBox, items: Sequence[str], index: int):
		listBox.Set(list(items))
		if not items:
			return
		index = max(0, min(index, len(items) - 1))
		listBox.SetSelection(index)
		# Selecting an item in a multiple selection list box does not move the
		# caret to it, and it is the item with the caret that is announced when
		# the list is tabbed into and that the arrow keys start from.
		winUser.sendMessage(listBox.GetHandle(), LB_SETCARETINDEX, index, 0)

	def _selectedStrings(self, listBox: wx.ListBox) -> List[str]:
		return [listBox.GetString(index) for index in listBox.GetSelections()]

	# --- the two buttons ----------------------------------------------------
	def _removeLabel(self, selectionCount: int) -> str:
		if selectionCount > 1:
			# Translators: the button that takes several selected applications off the autosleep list.
			return _("Remove selected")
		# Translators: the button that takes the current application off the autosleep list.
		return _("Remove")

	def _addLabel(self, selectionCount: int) -> str:
		if selectionCount > 1:
			# Translators: the button that puts several selected applications on the autosleep list.
			return _("Add selected")
		# Translators: the button that puts the current application on the autosleep list.
		return _("Add")

	def _updateButtons(self):
		"""Relabel each button for its list and switch it off for an empty one.

		A disabled button is skipped when tabbing, which is what keeps a button
		out of the way while the list it belongs to has nothing to act on.
		"""
		for button, listBox, label in (
			(self.removeButton, self.sleepList, self._removeLabel),
			(self.addButton, self.runningList, self._addLabel),
		):
			newLabel = label(len(listBox.GetSelections()))
			if button.GetLabel() != newLabel:
				button.SetLabel(newLabel)
			button.Enable(listBox.GetCount() > 0)

	def _onSelectionChanged(self, evt: wx.CommandEvent):
		self._updateButtons()
		evt.Skip()

	def _onRemove(self, evt: wx.CommandEvent):
		selection = self.sleepList.GetSelections()
		if not selection:
			return
		removed = {addonConfig.normalize(name) for name in self._selectedStrings(self.sleepList)}
		self._sleepApps = [app for app in self._sleepApps if addonConfig.normalize(app) not in removed]
		if not self._sleepApps:
			# This button is about to be disabled and it is the one with focus, so
			# focus is put somewhere sensible first rather than left to land
			# wherever Windows decides.
			self.runningList.SetFocus()
		self._refreshLists(sleepIndex=selection[0])

	def _onAdd(self, evt: wx.CommandEvent):
		selection = self.runningList.GetSelections()
		if not selection:
			return
		self._sleepApps = sorted(
			self._sleepApps + self._selectedStrings(self.runningList),
			key=addonConfig.normalize,
		)
		if not self._availableApps():
			# As in _onRemove: move away before the button disappears from the
			# tab order underneath the focus.
			self.sleepList.SetFocus()
		self._refreshLists(runningIndex=selection[0])
