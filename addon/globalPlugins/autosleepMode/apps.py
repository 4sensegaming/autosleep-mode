# Autosleep Mode: finding the applications that are running
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""Enumeration of the applications the user can pick from in the settings panel.

An application counts as running when it owns a top-level window that would show
up in the task switcher: visible, unowned, and not a tool window. Each such
window is reduced to the name NVDA would use for its process, which is the very
string the add-on matches against the list of applications to put to sleep.
"""

from typing import List

import appModuleHandler
import globalVars
import winUser
from logHandler import log
from winBindings.user32 import EnumWindows, WNDENUMPROC


def _isTaskWindow(hwnd: int) -> bool:
	"""Whether this top-level window makes its application count as running.

	These are the conditions the task switcher itself applies: the window has to
	be visible, must not belong to another window, and must not be one of the
	auxiliary tool windows an application keeps around. Between them these drop
	the helper and message-only windows applications keep alongside their real
	ones, as well as the desktop and the taskbar. A window title is deliberately
	not required, so that an application which does not give its window one, as
	a full screen self-voicing game may well not, still shows up.
	"""
	if not winUser.isWindowVisible(hwnd):
		return False
	if winUser.getWindow(hwnd, winUser.GW_OWNER):
		return False
	return not winUser.getExtendedWindowStyle(hwnd) & winUser.WS_EX_TOOLWINDOW


def _taskWindowProcessIds() -> List[int]:
	"""The process IDs behind every task window, NVDA's own process excluded.

	NVDA is left out deliberately. Its own windows, among them the Settings
	dialog this list is displayed in, are task windows like any other, but
	offering NVDA as something to put to sleep would only give the user a way to
	silence NVDA's own interface.
	"""
	processIds = []

	@WNDENUMPROC
	def collect(hwnd: int, _lParam: int) -> int:
		try:
			if _isTaskWindow(hwnd):
				processId = winUser.getWindowThreadProcessID(hwnd)[0]
				if processId and processId != globalVars.appPid and processId not in processIds:
					processIds.append(processId)
		except Exception:
			log.debugWarning("Error examining window %r" % hwnd, exc_info=True)
		# Keep going: every window has to be looked at, not just the first match.
		return 1

	EnumWindows(collect, 0)
	return processIds


def runningAppNames() -> List[str]:
	"""The applications that are running now, named the way NVDA names them.

	The names are those of the processes owning the task windows, resolved
	through NVDA so that an executable hosting several applications (javaw and
	the Windows application frame host among them) is reported as the application
	it is hosting rather than as the host. The result is sorted and free of
	duplicates, since several windows, and indeed several processes, commonly
	belong to one application.
	"""
	names = set()
	for processId in _taskWindowProcessIds():
		try:
			# One call per process rather than per window: each one walks a
			# snapshot of every process on the system.
			name = appModuleHandler.getAppNameFromProcessID(processId)
		except Exception:
			log.debugWarning("Could not get the application name of process %d" % processId, exc_info=True)
			continue
		if name:
			names.add(name)
	return sorted(names, key=str.lower)
