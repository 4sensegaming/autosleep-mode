# Autosleep Mode: finding the applications that are running
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

import ctypes
from ctypes.wintypes import RECT
from typing import NamedTuple

import appModuleHandler
import globalVars
import winUser
from logHandler import log
from winBindings.user32 import WNDENUMPROC, EnumChildWindows, EnumWindows, GetWindowRect

from . import dwm

APP_FRAME_CLASS = "ApplicationFrameWindow"
CORE_WINDOW_CLASS = "Windows.UI.Core.CoreWindow"
MAX_OWNER_DEPTH = 32


class RunningApp(NamedTuple):
	appName: str
	displayName: str
	sleeping: bool


def _topLevelWindows() -> list[int]:
	windows: list[int] = []

	@WNDENUMPROC
	def collect(hwnd: int, _lParam: int) -> int:
		windows.append(hwnd)
		return 1

	EnumWindows(collect, 0)
	return windows


def _hasArea(hwnd: int) -> bool:
	rect = RECT()
	if not GetWindowRect(hwnd, ctypes.byref(rect)):
		return False
	return rect.right > rect.left and rect.bottom > rect.top


def _isDrawnWindow(hwnd: int, drawn: dict[int, bool]) -> bool:
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
	"""Only a drawn owner counts: Visual Basic 6 applications own every form by an invisible window."""
	owner = winUser.getWindow(hwnd, winUser.GW_OWNER)
	for _step in range(MAX_OWNER_DEPTH):
		if not owner:
			return False
		if _isDrawnWindow(owner, drawn):
			return True
		owner = winUser.getWindow(owner, winUser.GW_OWNER)
	log.debugWarning(f"Gave up walking the owners of window {hwnd!r}")
	return False


def _isSwitchableWindow(hwnd: int, drawn: dict[int, bool]) -> bool:
	return _isDrawnWindow(hwnd, drawn) and not _hasDrawnOwner(hwnd, drawn)


def _processId(hwnd: int) -> int:
	return winUser.getWindowThreadProcessID(hwnd)[0]


def _title(hwnd: int) -> str:
	return winUser.getWindowText(hwnd).strip()


def _identify(processId: int, namesByProcessId: dict[int, str]) -> tuple[str, bool]:
	"""The app name, and whether NVDA is asleep in it."""
	appModule = appModuleHandler.runningTable.get(processId)
	if appModule is not None:
		return appModule.appName, bool(appModule.sleepMode)
	if processId not in namesByProcessId:
		namesByProcessId[processId] = appModuleHandler.getAppNameFromProcessID(processId)
	return namesByProcessId[processId], False


def _coreWindowProcessIdsByTitle(windows: list[int]) -> dict[str, int]:
	byTitle: dict[str, int] = {}
	for hwnd in windows:
		if winUser.getClassName(hwnd) != CORE_WINDOW_CLASS:
			continue
		title = _title(hwnd)
		processId = _processId(hwnd)
		if title and processId:
			byTitle.setdefault(title, processId)
	return byTitle


def _hostedProcessId(hwnd: int, hostProcessId: int, coreWindows: dict[str, int]) -> int | None:
	hosted: list[int] = []

	@WNDENUMPROC
	def visit(child: int, _lParam: int) -> int:
		if winUser.getClassName(child) != CORE_WINDOW_CLASS:
			return 1
		processId = _processId(child)
		if not processId or processId == hostProcessId:
			return 1
		hosted.append(processId)
		return 0

	EnumChildWindows(hwnd, visit, 0)
	if hosted:
		return hosted[0]
	return coreWindows.get(_title(hwnd))


def runningApps() -> list[RunningApp]:
	windows = _topLevelWindows()
	drawn: dict[int, bool] = {}
	coreWindows: dict[str, int] | None = None
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
				processId = _hostedProcessId(hwnd, processId, coreWindows) or processId
			if not processId or processId == globalVars.appPid:
				continue
			appName, sleeping = _identify(processId, namesByProcessId)
			if not appName or appName in found:
				continue
			title = _title(hwnd)
		except Exception:  # noqa: BLE001
			log.debugWarning(f"Error examining window {hwnd!r}", exc_info=True)
			continue
		found[appName] = RunningApp(appName, title or appName, sleeping)

	return sorted(found.values(), key=lambda app: (app.displayName.lower(), app.appName))
