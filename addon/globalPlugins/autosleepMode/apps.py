# Autosleep Mode: finding the applications that are running
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""Enumeration of the applications the user can pick from in the settings panel.

An application counts as running when it has a window the user could switch to.
That is a narrower thing than having a process, and narrower than having a window
Windows calls visible: a great many processes keep top level windows around that
are never drawn, and listing those gives the user a page of names belonging to
nothing they could put in the foreground.

The test applied here is the one the task switcher applies, and the cloaking test
is the part of it that matters most. Each surviving window is then turned into the
title it shows the user and the name NVDA would give its process, the latter being
the string the add-on matches against the list of applications to put to sleep.
"""

import ctypes
from ctypes.wintypes import RECT
from typing import Dict, List, NamedTuple, Optional

import appModuleHandler
import globalVars
import winUser
from logHandler import log
from winBindings.user32 import EnumChildWindows, EnumWindows, GetWindowRect, WNDENUMPROC

from . import dwm

#: The class of the frame Windows draws around a packaged ("Store") application.
#: The frame belongs to the application frame host rather than to the application,
#: so a frame taken at face value names every packaged application on the system
#: ``applicationframehost``.
APP_FRAME_CLASS = "ApplicationFrameWindow"

#: The class of the window a packaged application actually draws into. It sits
#: inside the frame while the application is on screen, and Windows hands it back
#: to the desktop, cloaked, as soon as the application is minimised. Wherever it
#: is, it belongs to the application's own process, and that is what makes it the
#: way to find out whose frame a frame is.
CORE_WINDOW_CLASS = "Windows.UI.Core.CoreWindow"

#: How far a chain of window owners is followed before it is given up on. Nothing
#: legitimate nests anywhere near this deeply; the limit is only there so that a
#: walk over another process's windows cannot become an endless one.
MAX_OWNER_DEPTH = 32


class RunningApp(NamedTuple):
	"""One application to offer the user, under both of the names it goes by."""

	#: The name NVDA gives the application, which is what the configuration holds
	#: and what the add-on matches against: normally the executable's name without
	#: its extension.
	appName: str
	#: What the list shows: the title of the application's window, which is the
	#: name the user knows it by, falling back to L{appName} for a window that
	#: carries no title at all.
	displayName: str


def _topLevelWindows() -> List[int]:
	"""Every top level window there is, front to back.

	The order is the one the window manager keeps them in, so an application's
	frontmost window is the first of its windows to come past. That is the window
	whose title is worth showing.
	"""
	windows: List[int] = []

	@WNDENUMPROC
	def collect(hwnd: int, _lParam: int) -> int:
		windows.append(hwnd)
		# Keep going: every window has to be looked at, not just the first.
		return 1

	EnumWindows(collect, 0)
	return windows


def _childWindows(hwnd: int) -> List[int]:
	"""Every window inside C{hwnd}, however deeply nested."""
	windows: List[int] = []

	@WNDENUMPROC
	def collect(child: int, _lParam: int) -> int:
		windows.append(child)
		return 1

	EnumChildWindows(hwnd, collect, 0)
	return windows


def _hasArea(hwnd: int) -> bool:
	"""Whether the window covers any of the screen at all.

	A window of no width or height draws nothing and is there only to receive
	messages, which several application frameworks make liberal use of. A
	minimised window is not one of these: Windows parks it off the edge of the
	screen at a size of its own, so it keeps an area and stays in the list, as it
	should, since the user can switch straight back to it.
	"""
	rect = RECT()
	if not GetWindowRect(hwnd, ctypes.byref(rect)):
		return False
	return rect.right > rect.left and rect.bottom > rect.top


def _isDrawnWindow(hwnd: int) -> bool:
	"""Whether this window is one the user can actually see.

	Between them these are the conditions that separate a window on the screen
	from the many that only look like windows:

	- it has to be shown rather than hidden;
	- it must not be a tool window, the style meant for the palettes and helpers an
	  application keeps beside its real windows;
	- it must not be cloaked, which is the state Windows leaves the windows of a
	  suspended packaged application in, and the reason the application frame host
	  was offered as something to put to sleep;
	- and it has to occupy some of the screen.
	"""
	if not winUser.isWindowVisible(hwnd):
		return False
	if winUser.getExtendedWindowStyle(hwnd) & winUser.WS_EX_TOOLWINDOW:
		return False
	if dwm.isCloaked(hwnd):
		return False
	return _hasArea(hwnd)


def _hasDrawnOwner(hwnd: int) -> bool:
	"""Whether this window belongs to another window that is itself on the screen.

	A window that does is a dialog, or something else an application has put up
	beside a window it already has, and it is that other window the application
	should be named after.

	Which is why the question asked is about an owner the user can see, and not
	merely about an owner. An application built with Visual Basic 6, as a good
	many self-voicing games are, owns each of its forms by an invisible
	application window of no size; taking any owner at all as disqualifying would
	throw away every window such a game has, and the game with it. The same goes
	for the applications that put up a dialog and keep their main window hidden
	behind it.
	"""
	owner = winUser.getWindow(hwnd, winUser.GW_OWNER)
	# Windows does not allow a loop in a chain of owners, but this walks windows
	# belonging to other processes, so it is bounded rather than trusted.
	for _step in range(MAX_OWNER_DEPTH):
		if not owner:
			return False
		if _isDrawnWindow(owner):
			return True
		owner = winUser.getWindow(owner, winUser.GW_OWNER)
	log.debugWarning("Gave up walking the owners of window %r" % hwnd)
	return False


def _isSwitchableWindow(hwnd: int) -> bool:
	"""Whether this window is the one its application should be named after.

	That is a window the user can see which is not subordinate to another window
	the user can see.
	"""
	return _isDrawnWindow(hwnd) and not _hasDrawnOwner(hwnd)


def _processId(hwnd: int) -> int:
	return winUser.getWindowThreadProcessID(hwnd)[0]


def _title(hwnd: int) -> str:
	return winUser.getWindowText(hwnd).strip()


def _coreWindowProcessIdsByTitle(windows: List[int]) -> Dict[str, int]:
	"""The process behind each packaged application parked on the desktop, by title.

	A minimised packaged application leaves its core window among the top level
	windows, cloaked, still carrying the title its frame carries. That title is the
	only thing left tying the two together, and this is the index that lets a frame
	be looked up in it.
	"""
	byTitle: Dict[str, int] = {}
	for hwnd in windows:
		if winUser.getClassName(hwnd) != CORE_WINDOW_CLASS:
			continue
		title = _title(hwnd)
		processId = _processId(hwnd)
		if title and processId:
			# The frontmost of any two applications sharing a title wins, which is
			# the rule the list itself goes by as well.
			byTitle.setdefault(title, processId)
	return byTitle


def _hostedProcessId(hwnd: int, hostProcessId: int, coreWindows: Dict[str, int]) -> Optional[int]:
	"""The process of the packaged application this frame shows, where it can be found.

	While the application is on screen its core window is inside the frame and says
	whose the frame is outright. Once the application is minimised that core window
	has gone back to the desktop and the shared title is all there is left to go on,
	so it is looked up there instead.
	"""
	for child in _childWindows(hwnd):
		if winUser.getClassName(child) != CORE_WINDOW_CLASS:
			continue
		processId = _processId(child)
		if processId and processId != hostProcessId:
			return processId
	return coreWindows.get(_title(hwnd))


def runningApps() -> List[RunningApp]:
	"""The applications that have a window open now, ready to be listed.

	One entry per application however many windows it has, titled after its
	frontmost one and sorted the way the user reads them. NVDA is left out
	deliberately: its own windows, the Settings dialog this list is shown in among
	them, are switchable like any others, but offering NVDA as something to put to
	sleep would only give the user a way to silence NVDA's own interface.
	"""
	windows = _topLevelWindows()
	#: Built only if a packaged application turns up, since it costs a pass of its own.
	coreWindows: Optional[Dict[str, int]] = None
	#: NVDA resolves a name by walking a snapshot of every process on the system, so
	#: each process is asked about once however many windows it has.
	namesByProcessId: Dict[int, str] = {}
	found: Dict[str, RunningApp] = {}

	for hwnd in windows:
		try:
			if not _isSwitchableWindow(hwnd):
				continue
			processId = _processId(hwnd)
			if winUser.getClassName(hwnd) == APP_FRAME_CLASS:
				if coreWindows is None:
					coreWindows = _coreWindowProcessIdsByTitle(windows)
				# Falling back to the host itself is the honest answer when the
				# application behind the frame cannot be made out.
				processId = _hostedProcessId(hwnd, processId, coreWindows) or processId
			if not processId or processId == globalVars.appPid:
				continue
			if processId not in namesByProcessId:
				namesByProcessId[processId] = appModuleHandler.getAppNameFromProcessID(processId)
			appName = namesByProcessId[processId]
			if not appName:
				continue
			title = _title(hwnd)
		except Exception:
			log.debugWarning("Error examining window %r" % hwnd, exc_info=True)
			continue
		# The windows come front to back, so the first one seen for an application
		# is its frontmost, and gives the title the user is most likely to know it by.
		found.setdefault(appName, RunningApp(appName, title or appName))

	return sorted(found.values(), key=lambda app: (app.displayName.lower(), app.appName))
