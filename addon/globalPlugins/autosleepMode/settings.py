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

Both lists are list views rather than list boxes. A multiple selection list box
is the obvious control for the job and the wrong one: it reports a selection to
the screen reader on every arrow key even when the key moved nothing, and its
selection cannot be toggled from the keyboard at all. A list view stays silent
when a key changes nothing, and reports an item being selected and unselected as
it happens, which is what lets the screen reader say so.

The item the arrow keys are on is always the selected item, until the user
selects more than one, which is how every other list view on Windows behaves and
what a screen reader expects. Leaving it merely current and not selected is worth
naming as a mistake, because it looks tidier and is not: the list view then
reports the item twice over, once as current and once as selected, and a screen
reader reads it out twice and calls it "not selected" every time.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING

import addonHandler
import winUser
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from . import addonConfig, apps

if TYPE_CHECKING:
	# NVDA puts the translation lookup into this module's namespace at run time,
	# which a type checker reading the source has no way of knowing. This says what
	# it will be; nothing is imported when the add-on is actually running, which is
	# what the suppression below records.
	from gettext import gettext as _  # noqa: TC004

addonHandler.initTranslation()

#: The keys that move towards the first item, and those that move towards the
#: last. The numeric keypad sends its own codes for these when Num Lock is off.
_TOWARDS_THE_TOP = frozenset(
	(wx.WXK_UP, wx.WXK_PAGEUP, wx.WXK_HOME, wx.WXK_NUMPAD_UP, wx.WXK_NUMPAD_PAGEUP, wx.WXK_NUMPAD_HOME),
)
_TOWARDS_THE_BOTTOM = frozenset(
	(wx.WXK_DOWN, wx.WXK_PAGEDOWN, wx.WXK_END, wx.WXK_NUMPAD_DOWN, wx.WXK_NUMPAD_PAGEDOWN, wx.WXK_NUMPAD_END),
)

#: The keys that ask for the selected applications to be taken off the autosleep
#: list, which is what the Remove button does. The numeric keypad sends its own
#: code for this one as well when Num Lock is off.
_REMOVES = frozenset((wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE))

#: Messages and styles for switching a list view's own tooltip off. A list view
#: pops one up to show the whole of an item whose text is wider than the column,
#: and a screen reader announces it, so a long window title is read out a second
#: time and called a tooltip. Nothing here wants a tooltip, so the control is
#: told to have none: the styles that ask for one are cleared, and the tooltip
#: window it would use is taken away as well.
_LVM_FIRST = 0x1000
_LVM_SETEXTENDEDLISTVIEWSTYLE = _LVM_FIRST + 54
_LVM_SETTOOLTIPS = _LVM_FIRST + 74
_LVS_EX_INFOTIP = 0x00000400
_LVS_EX_LABELTIP = 0x00004000

#: How big a list asks to be before the panel is laid out. It is given all the
#: width the panel can spare afterwards, so this is really the height, and the
#: width it falls back on.
_LIST_SIZE = (250, 150)

#: What each button is called, singular and plural. A button is renamed as the
#: selection it acts on grows past one and shrinks back again, so both names are
#: needed at once.
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

	#: The list of applications as it will be saved, edited in place until then.
	_sleepApps: list[str]
	#: Every application currently running, filled in by L{onPanelActivated}.
	_runningApps: list[apps.RunningApp]
	#: Set while a list is being refilled, so that the events that causes are not
	#: mistaken for the user changing the selection.
	_refreshing: bool
	#: Each button with the list it acts on and the two names it goes by.
	_buttons: tuple[tuple[wx.Button, wx.ListCtrl, str, str], ...]
	#: The applications that are put to sleep automatically.
	sleepList: wx.ListCtrl
	#: The applications running now that are not on the autosleep list yet.
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
		# Which applications are running is only true for as long as it takes the
		# user to start or close one, so it is looked up each time the category is
		# selected rather than once when the panel is built.
		self._runningApps = apps.runningApps()
		self._refreshLists()
		super().onPanelActivated()

	def onSave(self):
		addonConfig.setApps(self._sleepApps)
		addonConfig.setAddManuallySleptApps(self.addManuallySleptCheckBox.IsChecked())
		addonConfig.setRemoveManuallyWokenApps(self.removeManuallyWokenCheckBox.IsChecked())

	# --- the two lists ------------------------------------------------------
	def _addAppList(self, sHelper, settingsSizer: wx.Sizer, label: str) -> wx.ListCtrl:
		"""Add a labelled list of application names.

		One nameless column, and no header over it, so that the list reads as the
		plain column of names it looks like. The label beside it is what names the
		list itself to a screen reader.
		"""
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
		"""Let this list have all the width the panel can spare, for longer titles.

		A sizer gives its spare room only to the items that have asked for it, and
		an item that has not keeps the size it was built with, so the width has to
		be asked for at both of the steps between the list and the panel: the row
		the list shares with its label, and the column of rows the panel is.

		In the row, which is horizontal, it is the proportion that hands the width
		left over from the label to the list. In the panel's column it is expanding
		that makes the row as wide as the panel; the proportion is deliberately left
		alone there, since in a vertical sizer that would divide up the height
		instead and make the lists taller than they were meant to be.
		"""
		row = listCtrl.GetContainingSizer()
		item = row.GetItem(listCtrl)
		# wxPython's own type stub says this cannot be None. It can: the call
		# underneath answers NULL for a window the sizer does not hold, which is
		# exactly the case this guard is here for. The stub is wrong, so the
		# checker is told so rather than the guard being taken out.
		if item is not None:  # pyright: ignore[reportUnnecessaryComparison]
			item.SetFlag(item.GetFlag() | wx.EXPAND)
			# Asked for only where it means width. Which sizer a helper put the list
			# in is that helper's business, so the sizer is asked rather than assumed.
			if isinstance(row, wx.BoxSizer) and row.GetOrientation() == wx.HORIZONTAL:
				item.SetProportion(1)
		item = settingsSizer.GetItem(row) if row is not settingsSizer else None
		if item is not None:
			item.SetFlag(item.GetFlag() | wx.EXPAND)

	def _onListResized(self, evt: wx.SizeEvent):
		"""Keep the single column as wide as the list itself.

		How wide the list ends up is not known until the panel has been laid out,
		and it changes again whenever the dialog is resized, so the column follows
		the list rather than being set once when the list is filled.
		"""
		listCtrl = evt.GetEventObject()
		listCtrl.SetColumnWidth(0, listCtrl.GetClientSize().width)
		evt.Skip()

	def _silenceTooltip(self, listCtrl: wx.ListCtrl):
		"""Stop this list from putting a tooltip over an item it has had to cut short."""
		handle = listCtrl.GetHandle()
		winUser.sendMessage(handle, _LVM_SETEXTENDEDLISTVIEWSTYLE, _LVS_EX_LABELTIP | _LVS_EX_INFOTIP, 0)
		winUser.sendMessage(handle, _LVM_SETTOOLTIPS, 0, 0)

	def _availableApps(self) -> list[apps.RunningApp]:
		"""The running applications that are not on the list already.

		An application already listed is left out rather than shown and ignored,
		so that adding one always has an effect. The order is the one the list is
		displayed in, which is what lets a selected row be turned back into the
		application it stands for.
		"""
		listed = {addonConfig.normalize(app) for app in self._sleepApps}
		return [app for app in self._runningApps if addonConfig.normalize(app.appName) not in listed]

	def _runningAppsByName(self) -> dict[str, apps.RunningApp]:
		"""Each running application by its name, so that a listed one can be looked up."""
		return {addonConfig.normalize(app.appName): app for app in self._runningApps}

	def _row(self, app: apps.RunningApp) -> str:
		"""The line shown for a running application.

		An application NVDA is asleep in says so, which is worth saying in either
		list: in the autosleep list it is the add-on's own work reported back, and
		in the list of available applications it is one the user has put to sleep by
		hand without adding it here, which they may well have meant to do.

		Marking the text is safe because the text is never read back: a row is
		always resolved by its position in the list it was filled from, never by
		what it says, which is what leaves the text free to carry something for the
		user to hear.
		"""
		if not app.sleeping:
			return app.displayName
		# Translators: how an application NVDA is currently asleep in is shown in
		# both lists of applications. {app} is the name of the application.
		return _("{app} (sleeping)").format(app=app.displayName)

	def _sleepListRow(self, appName: str, running: dict[str, apps.RunningApp]) -> str:
		"""The line shown for an application on the autosleep list.

		An application on the list need not be running, and one that is not has no
		window to take a title from and cannot be asleep either; that is the case,
		and the only one, where the stored name is shown on its own.
		"""
		app = running.get(addonConfig.normalize(appName))
		return appName if app is None else self._row(app)

	def _refreshLists(self, sleepIndex: int = 0, runningIndex: int = 0):
		"""Redisplay both lists, leaving the given item current in each.

		Both lists show an application under the title of its window, which is the
		name the user sees on the application itself, marked if NVDA is asleep in it.
		"""
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
		"""Put C{items} in the list, with the one at C{index} current and selected."""
		self._refreshing = True
		try:
			listCtrl.DeleteAllItems()
			for position, text in enumerate(items):
				listCtrl.InsertItem(position, text)
			# The single column carries the whole width, so that a long window
			# title is not cut off in the middle.
			listCtrl.SetColumnWidth(0, listCtrl.GetClientSize().width)
			if not items:
				return
			index = max(0, min(index, len(items) - 1))
			# Current and selected together, which is the state the arrow keys
			# leave an item in and the one the screen reader reads as a plain name.
			listCtrl.Focus(index)
			listCtrl.Select(index)
		finally:
			self._refreshing = False

	def _selectedIndices(self, listCtrl: wx.ListCtrl) -> list[int]:
		"""The positions of the items the user has selected, in order."""
		indices: list[int] = []
		index = listCtrl.GetFirstSelected()
		while index != -1:
			indices.append(index)
			index = listCtrl.GetNextSelected(index)
		return indices

	def _returnFocus(self, emptied: wx.ListCtrl, other: wx.ListCtrl):
		"""Put focus back on a list once a button has done its work.

		Never on the button that was pressed. A button says nothing about what it
		has just done, so focus left sitting on it leaves the screen reader silent
		and the user with no idea whether anything happened. A list, given focus,
		reads out where it now is, which is the answer.

		The list the button belongs to is the one to go back to, since that is
		where the user was, unless the button has just emptied it.
		"""
		(emptied if emptied.GetItemCount() else other).SetFocus()

	def _onListKeyDown(self, evt: wx.KeyEvent):
		"""Press the Remove button, or drop a navigation key that has nowhere to go.

		Delete is what a list of things one can take away is expected to answer to,
		and on the autosleep list it does exactly what the Remove button does, on
		exactly the applications the button would have acted on. The other list has
		nothing to remove from, so there it is left alone.

		Home on the first item, and End on the last, leave the item the user is on
		exactly where it was, but the list view still reports a selection for it,
		and a screen reader dutifully reads the item out again. Reading the same
		item over and over is how the list tells the user it has run out of items,
		and it is the wrong way round: silence is what says that.

		So the key is dropped here instead, before the list view ever sees it.
		Nothing happens, nothing is reported, and nothing is said. The arrow keys
		are dropped on the same terms even though the list view already ignores
		them quietly, so that the rule is one rule.
		"""
		if evt.GetEventObject() is self.sleepList and self._removes(evt):
			self._onRemove(evt)
			return
		if self._movesNothing(evt):
			# Deliberately not skipped: skipping is what passes the key on.
			return
		evt.Skip()

	def _removes(self, evt: wx.KeyEvent) -> bool:
		"""Whether this key is asking for the Remove button.

		Only a key pressed on its own, as with the navigation keys: Delete with a
		modifier held down means something else wherever Windows uses it, and the
		add-on has no business claiming those combinations for itself.
		"""
		return evt.GetModifiers() == wx.MOD_NONE and evt.GetKeyCode() in _REMOVES

	def _movesNothing(self, evt: wx.KeyEvent) -> bool:
		"""Whether this key would leave the list exactly as it is.

		Only a key pressed on its own is considered. Shift and control turn these
		same keys into ways of selecting rather than of moving, and what they do at
		either end of the list is the list view's business, not ours.

		Being at the end the key points to is not on its own enough. Home and End
		also draw the selection in to the single item they land on, so with several
		applications selected they still have something to do, and doing it is worth
		reporting. The key is only dropped when the item the user is on is the whole
		of the selection, and there is therefore nothing left for it to change.
		"""
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

	# --- the two buttons ----------------------------------------------------
	def _updateButtons(self):
		"""Rename each button for its list and switch it off for an empty one.

		A disabled button is skipped when tabbing, which is what keeps a button
		out of the way while the list it belongs to has nothing to act on.
		"""
		for button, listCtrl, single, several in self._buttons:
			label = several if len(self._selectedIndices(listCtrl)) > 1 else single
			if button.GetLabel() != label:
				button.SetLabel(label)
			button.Enable(listCtrl.GetItemCount() > 0)

	def _onRemoveKeyDown(self, evt: wx.KeyEvent):
		"""Let Delete on the Remove button press it.

		The button is the other place the user can be standing when they mean to
		take an application off the list, since that is where Tab from the list
		leads, and Delete there does what pressing the button does rather than
		nothing at all. Space and Enter are the button's own and are left to it.
		"""
		if self._removes(evt):
			self._onRemove(evt)
			return
		evt.Skip()

	def _onSelectionChanged(self, evt: wx.ListEvent):
		# Refilling a list selects and focuses items of its own accord; those are
		# not the user changing their mind and the buttons are updated once at the
		# end of the refresh anyway.
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
		"""Take the new autosleep list, redisplay both lists and hand focus back.

		This is everything the two buttons do once each has worked out which
		applications it is acting on. Refilling comes before the focus is handed
		back, so that the list being given focus is the new one and what the screen
		reader reads is where the user has actually ended up.
		"""
		self._sleepApps = sleepApps
		self._refreshLists(sleepIndex=sleepIndex, runningIndex=runningIndex)
		self._returnFocus(pressed, other)

	def _onRemove(self, evt: wx.Event):
		chosen = self._selectedIndices(self.sleepList)
		if not chosen:
			return
		# A row is a title as often as it is a name, so what a row stands for is
		# found by its position in the list it was filled from, never by its text.
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
		# As in _onRemove: the row is resolved by its position, since its text is
		# a title rather than the name that is stored.
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
