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

The whole of this runs while the settings dialog waits to be drawn, so the two
questions that are not cheap are asked as sparingly as the answer allows: whether
the compositor is hiding a window, which is put to another process and answered
back, and what NVDA calls a process, which NVDA works out by walking a snapshot of
every process on the system.
"""

import ctypes
from ctypes.wintypes import RECT
from typing import NamedTuple

import appModuleHandler
import globalVars
import winUser
from logHandler import log
from winBindings.user32 import WNDENUMPROC, EnumChildWindows, EnumWindows, GetWindowRect

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
	#: Whether NVDA's sleep mode is on for this application at the moment the list
	#: is drawn up. True whether the add-on switched it on when the application
	#: came to the foreground or the user switched it on by hand, and it is the
	#: second of those that makes it worth showing: an application slept by hand
	#: and not on the autosleep list is one the user may have meant to put there.
	sleeping: bool


def _topLevelWindows() -> list[int]:
	"""Every top level window there is, front to back.

	The order is the one the window manager keeps them in, so an application's
	frontmost window is the first of its windows to come past. That is the window
	whose title is worth showing.
	"""
	windows: list[int] = []

	@WNDENUMPROC
	def collect(hwnd: int, _lParam: int) -> int:
		windows.append(hwnd)
		# Keep going: every window has to be looked at, not just the first.
		return 1

	EnumWindows(collect, 0)
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


def _isDrawnWindow(hwnd: int, drawn: dict[int, bool]) -> bool:
	"""Whether this window is one the user can actually see.

	Between them these are the conditions that separate a window on the screen
	from the many that only look like windows:

	- it has to be shown rather than hidden;
	- it must not be a tool window, the style meant for the palettes and helpers an
	  application keeps beside its real windows;
	- it has to occupy some of the screen;
	- and it must not be cloaked, which is the state Windows leaves the windows of a
	  suspended packaged application in, and the reason the application frame host
	  was offered as something to put to sleep.

	Cloaking is asked about last although it is the condition that matters most,
	because it is the only one of the four that is not a cheap look at the window:
	it is a question put to the compositor in another process and answered back.
	Every window one of the tests before it rules out is a question never asked.

	C{drawn} remembers the answers for the length of one scan. A window that owns
	others is asked about once on its own account and again for each window it
	owns, and there is no reason to pay the compositor twice over for one window.
	"""
	if hwnd in drawn:
		return drawn[hwnd]
	answer = bool(
		winUser.isWindowVisible(hwnd)
		and not winUser.getExtendedWindowStyle(hwnd) & winUser.WS_EX_TOOLWINDOW
		and _hasArea(hwnd)
		and not dwm.isCloaked(hwnd)
	)
	drawn[hwnd] = answer
	return answer


def _hasDrawnOwner(hwnd: int, drawn: dict[int, bool]) -> bool:
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
		if _isDrawnWindow(owner, drawn):
			return True
		owner = winUser.getWindow(owner, winUser.GW_OWNER)
	log.debugWarning(f"Gave up walking the owners of window {hwnd!r}")
	return False


def _isSwitchableWindow(hwnd: int, drawn: dict[int, bool]) -> bool:
	"""Whether this window is the one its application should be named after.

	That is a window the user can see which is not subordinate to another window
	the user can see.
	"""
	return _isDrawnWindow(hwnd, drawn) and not _hasDrawnOwner(hwnd, drawn)


def _processId(hwnd: int) -> int:
	return winUser.getWindowThreadProcessID(hwnd)[0]


def _title(hwnd: int) -> str:
	return winUser.getWindowText(hwnd).strip()


def _identify(processId: int, namesByProcessId: dict[int, str]) -> tuple[str, bool]:
	"""What NVDA calls this process, and whether NVDA is asleep in it.

	Both answers live on the app module, so where NVDA has made one already it is
	asked for both and neither has to be worked out. Only the app modules that
	exist are consulted: asking for one that does not would build it, and building
	an app module for every window on the system is a real cost and no help. That
	is the whole of the second answer as well, since sleep mode is a state kept on
	the app module and an application NVDA has never made one for cannot have been
	put to sleep either.

	Where there is no app module the name has to be worked out instead, and NVDA
	does that by walking a snapshot of every process on the system. Those answers
	are remembered in C{namesByProcessId}, so a process is asked about once
	however many windows it has.
	"""
	appModule = appModuleHandler.runningTable.get(processId)
	if appModule is not None:
		return appModule.appName, bool(appModule.sleepMode)
	if processId not in namesByProcessId:
		namesByProcessId[processId] = appModuleHandler.getAppNameFromProcessID(processId)
	return namesByProcessId[processId], False


def _coreWindowProcessIdsByTitle(windows: list[int]) -> dict[str, int]:
	"""The process behind each packaged application parked on the desktop, by title.

	A minimised packaged application leaves its core window among the top level
	windows, cloaked, still carrying the title its frame carries. That title is the
	only thing left tying the two together, and this is the index that lets a frame
	be looked up in it.
	"""
	byTitle: dict[str, int] = {}
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


def _hostedProcessId(hwnd: int, hostProcessId: int, coreWindows: dict[str, int]) -> int | None:
	"""The process of the packaged application this frame shows, where it can be found.

	While the application is on screen its core window is inside the frame and says
	whose the frame is outright. Once the application is minimised that core window
	has gone back to the desktop and the shared title is all there is left to go on,
	so it is looked up there instead.

	The walk over the frame's windows stops at the first core window that answers
	the question. There is only ever the one, and the windows a frame keeps under
	it are not worth walking to the end of to be told again what is already known.
	"""
	hosted: list[int] = []

	@WNDENUMPROC
	def visit(child: int, _lParam: int) -> int:
		if winUser.getClassName(child) != CORE_WINDOW_CLASS:
			# Keep going: this is not the window being looked for.
			return 1
		processId = _processId(child)
		if not processId or processId == hostProcessId:
			return 1
		hosted.append(processId)
		# Stop: the application behind the frame has been found.
		return 0

	EnumChildWindows(hwnd, visit, 0)
	if hosted:
		return hosted[0]
	return coreWindows.get(_title(hwnd))


def runningApps() -> list[RunningApp]:
	"""The applications that have a window open now, ready to be listed.

	One entry per application however many windows it has, titled after its
	frontmost one, carrying whether NVDA is asleep in it, and sorted the way the
	user reads them. NVDA is left out deliberately: its own windows, the Settings
	dialog this list is shown in among them, are switchable like any others, but
	offering NVDA as something to put to sleep would only give the user a way to
	silence NVDA's own interface.
	"""
	windows = _topLevelWindows()
	#: Whether each window looked at so far is one the user can see.
	drawn: dict[int, bool] = {}
	#: Built only if a packaged application turns up, since it costs a pass of its own.
	coreWindows: dict[str, int] | None = None
	#: The names NVDA had to work out rather than have to hand.
	namesByProcessId: dict[int, str] = {}
	found: dict[str, RunningApp] = {}

	for hwnd in windows:
		try:
			if not _isSwitchableWindow(hwnd, drawn):
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
			appName, sleeping = _identify(processId, namesByProcessId)
			# The windows come front to back, so the first one seen for an
			# application is its frontmost, and gives the title the user is most
			# likely to know it by. Every later window of the same one is nothing
			# to do but drop.
			if not appName or appName in found:
				continue
			title = _title(hwnd)
		# Deliberately anything at all: these are other processes' windows, they can
		# be closed halfway through being looked at, and one window that cannot be
		# examined is no reason to hand the user an empty list.
		except Exception:  # noqa: BLE001
			log.debugWarning(f"Error examining window {hwnd!r}", exc_info=True)
			continue
		found[appName] = RunningApp(appName, title or appName, sleeping)

	return sorted(found.values(), key=lambda app: (app.displayName.lower(), app.appName))
