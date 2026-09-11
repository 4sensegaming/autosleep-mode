# Autosleep Mode: driving NVDA's own sleep mode
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

import functools
from collections.abc import Callable

import globalCommands
from logHandler import log

_Script = Callable[..., None]

_originalScript: _Script | None = None
_wrapperScript: _Script | None = None


def activate():
	"""NVDA+shift+s, which toggles, so only call it for an application that is awake."""
	globalCommands.commands.script_toggleCurrentAppSleepMode(None)


def installManualToggleHook(callback):
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
	_repointGestures(original, wrapper)
	_originalScript = original
	_wrapperScript = wrapper


def removeManualToggleHook():
	global _originalScript, _wrapperScript
	if _wrapperScript is None:
		return
	if globalCommands.GlobalCommands.script_toggleCurrentAppSleepMode is _wrapperScript:
		globalCommands.GlobalCommands.script_toggleCurrentAppSleepMode = _originalScript
	_repointGestures(_wrapperScript, _originalScript)
	_originalScript = None
	_wrapperScript = None


def _repointGestures(oldFunc, newFunc):
	try:
		gestureMap = globalCommands.commands._gestureMap
	except AttributeError:
		log.debugWarning("No gesture map to update on the global commands object", exc_info=True)
		return
	for identifier, func in list(gestureMap.items()):
		if func is oldFunc:
			gestureMap[identifier] = newFunc
