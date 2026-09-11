# Autosleep Mode: the one thing the Desktop Window Manager has to be asked
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

import ctypes
from ctypes.wintypes import DWORD, HWND

DWMWA_CLOAKED = 14

_dwmapi = ctypes.WinDLL("dwmapi")
_DwmGetWindowAttribute = _dwmapi.DwmGetWindowAttribute
_DwmGetWindowAttribute.argtypes = (HWND, DWORD, ctypes.c_void_p, DWORD)
_DwmGetWindowAttribute.restype = ctypes.c_long

_S_OK = 0


def isCloaked(hwnd: int) -> bool:
	cloaked = DWORD()
	result = _DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
	if result != _S_OK:
		return False
	return bool(cloaked.value)
