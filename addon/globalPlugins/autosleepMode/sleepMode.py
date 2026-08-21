# Autosleep Mode: driving NVDA's own sleep mode
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""The two points of contact with NVDA's built-in sleep mode.

:func:`activate` switches sleep mode on by calling the very command NVDA+shift+s
is bound to, so that the announcement the user hears is NVDA's own, already
translated into whichever language NVDA is running in, and so that everything
else that command does (telling the focused object it is losing focus before the
application falls silent) happens exactly as it would by hand.

:func:`installManualToggleHook` lets the add-on find out that the user has used
that command themselves, which is what the "add manually slept applications"
option needs.
"""

import functools

import globalCommands
from logHandler import log

#: The unwrapped command, kept so that the wrapper can be undone.
_originalScript = None
#: The wrapper currently installed over it, or C{None} if there is none.
_wrapperScript = None


def activate():
	"""Switch sleep mode on for the focused application.

	This is NVDA+shift+s, called directly rather than reimplemented: it toggles,
	so the caller has to have established that the application is awake.
	"""
	globalCommands.commands.script_toggleCurrentAppSleepMode(None)


def installManualToggleHook(callback):
	"""Arrange for C{callback} to be called after every sleep mode toggle.

	The callback takes no arguments and is called once the command has finished,
	whichever way it left sleep mode; it is up to the callback to look at the
	focused application and decide whether anything is worth doing.
	"""
	global _originalScript, _wrapperScript
	if _wrapperScript is not None:
		return
	original = globalCommands.GlobalCommands.script_toggleCurrentAppSleepMode

	@functools.wraps(original)
	def wrapper(commands, gesture):
		original(commands, gesture)
		try:
			callback()
		except Exception:
			log.exception("Error handling a sleep mode toggle")

	globalCommands.GlobalCommands.script_toggleCurrentAppSleepMode = wrapper
	# Replacing the attribute on the class is not enough on its own. A gesture is
	# bound by storing the function taken from the class at binding time
	# (baseObject.ScriptableObject.bindGesture), and the built-in gestures for
	# this command were bound when NVDA imported globalCommands, long before this
	# add-on was loaded, so their entries still hold the original function.
	# A gesture assigned by the user in the Input Gestures dialog needs no such
	# fixing up: those are resolved by name against the class when the key is
	# pressed, and so find the wrapper by themselves.
	_repointGestures(original, wrapper)
	_originalScript = original
	_wrapperScript = wrapper
	# functools.wraps has copied the attributes the script decorator left on the
	# original, which is what keeps this command working in sleep mode
	# (allowInSleepMode) and keeps its description and category in Input Help and
	# the Input Gestures dialog.


def removeManualToggleHook():
	"""Undo :func:`installManualToggleHook`."""
	global _originalScript, _wrapperScript
	if _wrapperScript is None:
		return
	# Only take the wrapper back out if it is still the outermost one: another
	# add-on may have wrapped it in turn since, and restoring the original over
	# the top of that would throw its wrapper away.
	if globalCommands.GlobalCommands.script_toggleCurrentAppSleepMode is _wrapperScript:
		globalCommands.GlobalCommands.script_toggleCurrentAppSleepMode = _originalScript
	_repointGestures(_wrapperScript, _originalScript)
	_originalScript = None
	_wrapperScript = None


def _repointGestures(oldFunc, newFunc):
	"""Point every gesture bound to C{oldFunc} at C{newFunc} instead."""
	try:
		gestureMap = globalCommands.commands._gestureMap
	except AttributeError:
		log.debugWarning("No gesture map to update on the global commands object", exc_info=True)
		return
	for identifier, func in list(gestureMap.items()):
		if func is oldFunc:
			gestureMap[identifier] = newFunc
