# Autosleep Mode: the settings panel
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

from collections.abc import Sequence
from typing import TYPE_CHECKING

import addonHandler
import winUser
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from . import addonConfig, apps

if TYPE_CHECKING:
	from gettext import gettext as _  # noqa: TC004

addonHandler.initTranslation()

_TOWARDS_THE_TOP = frozenset(
	(wx.WXK_UP, wx.WXK_PAGEUP, wx.WXK_HOME, wx.WXK_NUMPAD_UP, wx.WXK_NUMPAD_PAGEUP, wx.WXK_NUMPAD_HOME),
)
_TOWARDS_THE_BOTTOM = frozenset(
	(wx.WXK_DOWN, wx.WXK_PAGEDOWN, wx.WXK_END, wx.WXK_NUMPAD_DOWN, wx.WXK_NUMPAD_PAGEDOWN, wx.WXK_NUMPAD_END),
)

_REMOVES = frozenset((wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE))

_LVM_FIRST = 0x1000
_LVM_SETEXTENDEDLISTVIEWSTYLE = _LVM_FIRST + 54
_LVM_SETTOOLTIPS = _LVM_FIRST + 74
_LVS_EX_INFOTIP = 0x00000400
_LVS_EX_LABELTIP = 0x00004000

_LIST_SIZE = (250, 150)

# Translators: the button that takes the current application off the autosleep list.
_REMOVE = _("&Remove")
# Translators: the button that takes several selected applications off the autosleep list.
_REMOVE_SELECTED = _("&Remove selected")
# Translators: the button that puts the current application on the autosleep list.
_ADD = _("&Add")
# Translators: the button that puts several selected applications on the autosleep list.
_ADD_SELECTED = _("&Add selected")


class AutosleepSettingsPanel(SettingsPanel):
	# Translators: the title of the add-on's category in NVDA's Settings dialog.
	title = _("Autosleep Mode")

	_sleepApps: list[str]
	_runningApps: list[apps.RunningApp]
	_refreshing: bool
	_buttons: tuple[tuple[wx.Button, wx.ListCtrl, str, str], ...]
	sleepList: wx.ListCtrl
	runningList: wx.ListCtrl
	removeButton: wx.Button
	addButton: wx.Button
	addManuallySleptCheckBox: wx.CheckBox
	removeManuallyWokenCheckBox: wx.CheckBox

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self._sleepApps = addonConfig.getApps()
		self._runningApps = []
		self._refreshing = False

		self.sleepList = self._addAppList(
			sHelper,
			settingsSizer,
			# Translators: the label of the list of applications that are put to sleep automatically.
			_("Apps to &sleep"),
		)
		self.removeButton = sHelper.addItem(wx.Button(self, label=_REMOVE))
		self.removeButton.Bind(wx.EVT_BUTTON, self._onRemove)
		self.removeButton.Bind(wx.EVT_KEY_DOWN, self._onRemoveKeyDown)

		self.runningList = self._addAppList(
			sHelper,
			settingsSizer,
			# Translators: the label of the list of applications that are running now and
			# can be added to the autosleep list.
			_("A&vailable apps"),
		)
		self.addButton = sHelper.addItem(wx.Button(self, label=_ADD))
		self.addButton.Bind(wx.EVT_BUTTON, self._onAdd)
		self._buttons = (
			(self.removeButton, self.sleepList, _REMOVE, _REMOVE_SELECTED),
			(self.addButton, self.runningList, _ADD, _ADD_SELECTED),
		)

		self.addManuallySleptCheckBox = sHelper.addItem(
			wx.CheckBox(
				self,
				# Translators: an option to grow the list from the applications slept by hand.
				label=_("Add apps with &manually activated sleep mode to the autosleep list"),
			),
		)
		self.addManuallySleptCheckBox.SetValue(addonConfig.getAddManuallySleptApps())

		self.removeManuallyWokenCheckBox = sHelper.addItem(
			wx.CheckBox(
				self,
				# Translators: an option to shrink the list by the applications woken by hand.
				label=_("Remove &manually woken apps from the autosleep list"),
			),
		)
		self.removeManuallyWokenCheckBox.SetValue(addonConfig.getRemoveManuallyWokenApps())

		self._refreshLists()

	def onPanelActivated(self):
		self._runningApps = apps.runningApps()
		self._refreshLists()
		super().onPanelActivated()

	def onSave(self):
		addonConfig.setApps(self._sleepApps)
		addonConfig.setAddManuallySleptApps(self.addManuallySleptCheckBox.IsChecked())
		addonConfig.setRemoveManuallyWokenApps(self.removeManuallyWokenCheckBox.IsChecked())

	def _addAppList(self, sHelper, settingsSizer: wx.Sizer, label: str) -> wx.ListCtrl:
		listCtrl = sHelper.addLabeledControl(
			label,
			wx.ListCtrl,
			size=self.scaleSize(_LIST_SIZE),
			style=wx.LC_REPORT | wx.LC_NO_HEADER,
		)
		listCtrl.InsertColumn(0, "")
		self._silenceTooltip(listCtrl)
		self._widenToThePanel(listCtrl, settingsSizer)
		for event in (wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED, wx.EVT_LIST_ITEM_FOCUSED):
			listCtrl.Bind(event, self._onSelectionChanged)
		listCtrl.Bind(wx.EVT_KEY_DOWN, self._onListKeyDown)
		listCtrl.Bind(wx.EVT_SIZE, self._onListResized)
		return listCtrl

	def _widenToThePanel(self, listCtrl: wx.ListCtrl, settingsSizer: wx.Sizer):
		row = listCtrl.GetContainingSizer()
		item = row.GetItem(listCtrl)
		if item is not None:  # pyright: ignore[reportUnnecessaryComparison]
			item.SetFlag(item.GetFlag() | wx.EXPAND)
			if isinstance(row, wx.BoxSizer) and row.GetOrientation() == wx.HORIZONTAL:
				item.SetProportion(1)
		item = settingsSizer.GetItem(row) if row is not settingsSizer else None
		if item is not None:
			item.SetFlag(item.GetFlag() | wx.EXPAND)

	def _onListResized(self, evt: wx.SizeEvent):
		listCtrl = evt.GetEventObject()
		listCtrl.SetColumnWidth(0, listCtrl.GetClientSize().width)
		evt.Skip()

	def _silenceTooltip(self, listCtrl: wx.ListCtrl):
		handle = listCtrl.GetHandle()
		winUser.sendMessage(handle, _LVM_SETEXTENDEDLISTVIEWSTYLE, _LVS_EX_LABELTIP | _LVS_EX_INFOTIP, 0)
		winUser.sendMessage(handle, _LVM_SETTOOLTIPS, 0, 0)

	def _availableApps(self) -> list[apps.RunningApp]:
		listed = {addonConfig.normalize(app) for app in self._sleepApps}
		return [app for app in self._runningApps if addonConfig.normalize(app.appName) not in listed]

	def _runningAppsByName(self) -> dict[str, apps.RunningApp]:
		return {addonConfig.normalize(app.appName): app for app in self._runningApps}

	def _row(self, app: apps.RunningApp) -> str:
		if not app.sleeping:
			return app.displayName
		# Translators: how an application NVDA is currently asleep in is shown in
		# both lists of applications. {app} is the name of the application.
		return _("{app} (sleeping)").format(app=app.displayName)

	def _sleepListRow(self, appName: str, running: dict[str, apps.RunningApp]) -> str:
		app = running.get(addonConfig.normalize(appName))
		return appName if app is None else self._row(app)

	def _refreshLists(self, sleepIndex: int = 0, runningIndex: int = 0):
		running = self._runningAppsByName()
		self._fillList(
			self.sleepList,
			[self._sleepListRow(app, running) for app in self._sleepApps],
			sleepIndex,
		)
		self._fillList(
			self.runningList,
			[self._row(app) for app in self._availableApps()],
			runningIndex,
		)
		self._updateButtons()

	def _fillList(self, listCtrl: wx.ListCtrl, items: Sequence[str], index: int):
		self._refreshing = True
		try:
			listCtrl.DeleteAllItems()
			for position, text in enumerate(items):
				listCtrl.InsertItem(position, text)
			listCtrl.SetColumnWidth(0, listCtrl.GetClientSize().width)
			if not items:
				return
			index = max(0, min(index, len(items) - 1))
			# Focused but not selected, the item is read twice and called "not selected".
			listCtrl.Focus(index)
			listCtrl.Select(index)
		finally:
			self._refreshing = False

	def _selectedIndices(self, listCtrl: wx.ListCtrl) -> list[int]:
		indices: list[int] = []
		index = listCtrl.GetFirstSelected()
		while index != -1:
			indices.append(index)
			index = listCtrl.GetNextSelected(index)
		return indices

	def _returnFocus(self, emptied: wx.ListCtrl, other: wx.ListCtrl):
		(emptied if emptied.GetItemCount() else other).SetFocus()

	def _onListKeyDown(self, evt: wx.KeyEvent):
		if evt.GetEventObject() is self.sleepList and self._removes(evt):
			self._onRemove(evt)
			return
		if self._movesNothing(evt):
			return
		evt.Skip()

	def _removes(self, evt: wx.KeyEvent) -> bool:
		return evt.GetModifiers() == wx.MOD_NONE and evt.GetKeyCode() in _REMOVES

	def _movesNothing(self, evt: wx.KeyEvent) -> bool:
		if evt.GetModifiers() != wx.MOD_NONE:
			return False
		listCtrl = evt.GetEventObject()
		current = listCtrl.GetFocusedItem()
		if current == -1:
			return False
		keyCode = evt.GetKeyCode()
		if keyCode in _TOWARDS_THE_TOP:
			atTheEnd = current == 0
		elif keyCode in _TOWARDS_THE_BOTTOM:
			atTheEnd = current == listCtrl.GetItemCount() - 1
		else:
			return False
		return atTheEnd and self._selectedIndices(listCtrl) in ([], [current])

	def _updateButtons(self):
		for button, listCtrl, single, several in self._buttons:
			label = several if len(self._selectedIndices(listCtrl)) > 1 else single
			if button.GetLabel() != label:
				button.SetLabel(label)
			button.Enable(listCtrl.GetItemCount() > 0)

	def _onRemoveKeyDown(self, evt: wx.KeyEvent):
		if self._removes(evt):
			self._onRemove(evt)
			return
		evt.Skip()

	def _onSelectionChanged(self, evt: wx.ListEvent):
		if not self._refreshing:
			self._updateButtons()
		evt.Skip()

	def _apply(
		self,
		sleepApps: list[str],
		pressed: wx.ListCtrl,
		other: wx.ListCtrl,
		sleepIndex: int = 0,
		runningIndex: int = 0,
	):
		self._sleepApps = sleepApps
		self._refreshLists(sleepIndex=sleepIndex, runningIndex=runningIndex)
		self._returnFocus(pressed, other)

	def _onRemove(self, evt: wx.Event):
		chosen = self._selectedIndices(self.sleepList)
		if not chosen:
			return
		removed = set(chosen)
		self._apply(
			[app for index, app in enumerate(self._sleepApps) if index not in removed],
			self.sleepList,
			self.runningList,
			sleepIndex=chosen[0],
		)

	def _onAdd(self, evt: wx.CommandEvent):
		chosen = self._selectedIndices(self.runningList)
		if not chosen:
			return
		available = self._availableApps()
		self._apply(
			sorted(
				self._sleepApps + [available[index].appName for index in chosen if index < len(available)],
				key=addonConfig.normalize,
			),
			self.runningList,
			self.sleepList,
			runningIndex=chosen[0],
		)
