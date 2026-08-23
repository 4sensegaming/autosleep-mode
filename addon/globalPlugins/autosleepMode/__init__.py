# Autosleep Mode
# An NVDA add-on that switches NVDA's sleep mode on by itself whenever one of
# the applications you have listed comes to the foreground.
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""The global plugin: it watches for foreground changes, registers the settings
panel and the command that opens it, and notices when the user switches sleep
mode on or off by hand.
"""

import addonHandler
import api
import core
import eventHandler
import globalPluginHandler
import gui
import queueHandler
import speech
import ui
import wx
from gui.settingsDialogs import NVDASettingsDialog
from logHandler import log
from scriptHandler import script

from . import addonConfig
from . import settings as settingsModule
from . import sleepMode

addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: the category this add-on's commands are listed under in the
	# Input gestures dialog.
	scriptCategory = _("Autosleep Mode")

	def __init__(self):
		super(GlobalPlugin, self).__init__()
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
		# Harmless if the startup check was queued rather than registered: an
		# extension point reports an unknown handler rather than complaining.
		core.postNvdaStartup.unregister(self._checkFocusedApp)
		super(GlobalPlugin, self).terminate()

	# --- the command --------------------------------------------------------
	@script(
		# Translators: the description of the command that opens the add-on's
		# settings, shown in the Input gestures dialog.
		description=_("Displays autosleep mode settings"),
	)
	def script_showSettings(self, gesture):
		"""Open NVDA's Settings dialog on this add-on's category.

		The dialog is opened from the main thread rather than from the thread the
		command was run on, which is what every one of NVDA's own commands that
		puts a dialog on the screen does.
		"""
		wx.CallAfter(
			gui.mainFrame.popupSettingsDialog,
			NVDASettingsDialog,
			settingsModule.AutosleepSettingsPanel,
		)

	# --- the automatic behaviour --------------------------------------------
	def event_foreground(self, obj, nextHandler):
		"""Put the newly foregrounded application to sleep if it is a listed one.

		This is the once-per-window-change moment: NVDA fires this event when the
		foreground window changes and at no other time, so no listed application
		is looked at twice for one switch.
		"""
		if not self._focusedAppShouldSleep():
			nextHandler()
			return
		# The rest of the chain is deliberately not run: NVDAObject.event_foreground,
		# at the end of it, cancels speech, and that would swallow the announcement
		# about to be made. Cancelling is still the right thing to do on a change of
		# foreground window, so it happens here instead, before the announcement
		# rather than after it, and NVDA stays quiet in this application from then
		# on in any case.
		speech.cancelSpeech()
		sleepMode.activate()

	def event_gainFocus(self, obj, nextHandler):
		"""Drop a focus event for an application that is already asleep.

		eventHandler.executeEvent decides whether to drop an event by reading
		sleepMode once, before the foreground event that precedes a gainFocus has
		run. A gainFocus therefore still arrives here carrying the value sleep
		mode had a moment before this add-on switched it on, and without this the
		newly focused control would be announced after all.
		"""
		if obj.sleepMode:
			return
		nextHandler()

	def _checkFocusedApp(self):
		"""Put the focused application to sleep if it is a listed one.

		This is the one-off check made when the add-on starts. A change of
		foreground window goes through :meth:`event_foreground` instead, which has
		a little more to take care of.
		"""
		if self._focusedAppShouldSleep():
			sleepMode.activate()

	def _focusedAppShouldSleep(self) -> bool:
		"""Whether the focused application is a listed one that is still awake."""
		try:
			# The focused object decides, not the foreground object the event came
			# with, because the focus is what NVDA's own sleep mode command acts on
			# and NVDA has already moved it by the time a foreground event is fired.
			appModule = api.getFocusObject().appModule
			if appModule is None or appModule.sleepMode:
				return False
			return bool(appModule.appName) and addonConfig.isListed(appModule.appName)
		except Exception:
			log.exception("Error deciding whether to put the focused application to sleep")
			return False

	def _scheduleInitialCheck(self):
		"""Have the application that is in the foreground already checked once.

		At NVDA's startup this plugin is built before the initial focus has been
		reported, so the check waits for the action NVDA fires once the core loop
		is running and that focus is known. When the plugin is loaded into an NVDA
		that is already running, as happens when plugins are reloaded, that action
		will never fire again, but there is a focus to look at already and the
		check merely has to queue behind whatever else is pending.
		"""
		if eventHandler.lastQueuedFocusObject is None:
			core.postNvdaStartup.register(self._checkFocusedApp)
		else:
			queueHandler.queueFunction(queueHandler.eventQueue, self._checkFocusedApp)

	# --- growing the list from the manual command ---------------------------
	def _onSleepModeToggled(self):
		"""Follow the list along with what the user has just done by hand.

		The command toggles, so which way it has left sleep mode decides which of
		the two options applies. They are looked at one at a time and never
		together: they are independent settings, either can be on without the
		other, and the add-on has no reason to care whether they agree.

		This also runs when the add-on itself switched sleep mode on, and costs
		nothing when it does: such an application is on the list by definition, so
		there is nothing left to add. The add-on never switches sleep mode off, so
		the other way round is always the user's own doing.

		A list that has actually grown or shrunk is said out loud. The
		announcement is made the way NVDA makes its own, and it is queued rather
		than spoken at once, so that it follows NVDA's "Sleep mode on" or "Sleep
		mode off" and the two are heard as one. Nothing is said when the list was
		already as the toggle would leave it, so that the word means what it says.
		"""
		appModule = api.getFocusObject().appModule
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
