# Autosleep Mode
# An NVDA add-on that switches NVDA's sleep mode on by itself whenever one of
# the applications you have listed comes to the foreground.
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

from typing import TYPE_CHECKING

import addonHandler
import api
import core
import eventHandler
import globalPluginHandler
import gui
import queueHandler
import ui
import wx
from gui.settingsDialogs import NVDASettingsDialog
from logHandler import log
from scriptHandler import script

from . import addonConfig, sleepMode
from . import settings as settingsModule

if TYPE_CHECKING:
	from gettext import gettext as _  # noqa: TC004

addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: the category this add-on's commands are listed under in the
	# Input gestures dialog.
	scriptCategory = _("Autosleep Mode")

	def __init__(self):
		super().__init__()
		addonConfig.initialize()
		NVDASettingsDialog.categoryClasses.append(settingsModule.AutosleepSettingsPanel)
		sleepMode.installManualToggleHook(self._onSleepModeToggled)
		self._scheduleInitialCheck()

	def terminate(self):
		sleepMode.removeManualToggleHook()
		try:
			NVDASettingsDialog.categoryClasses.remove(settingsModule.AutosleepSettingsPanel)
		except ValueError:
			pass
		core.postNvdaStartup.unregister(self._checkFocusedApp)
		super().terminate()

	@script(
		# Translators: the description of the command that opens the add-on's
		# settings, shown in the Input gestures dialog.
		description=_("Displays autosleep mode settings"),
	)
	def script_showSettings(self, gesture):
		wx.CallAfter(
			gui.mainFrame.popupSettingsDialog,
			NVDASettingsDialog,
			settingsModule.AutosleepSettingsPanel,
		)

	def event_foreground(self, obj, nextHandler):
		nextHandler()
		if self._focusedAppShouldSleep():
			sleepMode.activate()

	def event_gainFocus(self, obj, nextHandler):
		if obj.sleepMode:
			return
		nextHandler()

	def _checkFocusedApp(self):
		if self._focusedAppShouldSleep():
			sleepMode.activate()

	def _focusedAppShouldSleep(self) -> bool:
		try:
			appModule = api.getFocusObject().appModule
			if appModule is None or appModule.sleepMode:
				return False
			return bool(appModule.appName) and addonConfig.isListed(appModule.appName)
		except Exception:
			log.exception("Error deciding whether to put the focused application to sleep")
			return False

	def _scheduleInitialCheck(self):
		if eventHandler.lastQueuedFocusObject is None:
			core.postNvdaStartup.register(self._checkFocusedApp)
		else:
			queueHandler.queueFunction(queueHandler.eventQueue, self._checkFocusedApp)

	def _onSleepModeToggled(self):
		focus = api.getFocusObject()
		appModule = focus.appModule if focus else None
		if appModule is None or not appModule.appName:
			return
		if appModule.sleepMode:
			listChanged = addonConfig.getAddManuallySleptApps() and addonConfig.addApp(appModule.appName)
		else:
			listChanged = addonConfig.getRemoveManuallyWokenApps() and addonConfig.removeApp(
				appModule.appName
			)
		if listChanged:
			# Translators: announced right after NVDA's own "Sleep mode on" or
			# "Sleep mode off" when that toggle has just put the application on the
			# autosleep list or taken it off it.
			ui.message(_("Saved"))
