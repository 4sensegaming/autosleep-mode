# Autosleep Mode: the one thing the Desktop Window Manager has to be asked
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""Whether a window is cloaked, which is the question ``IsWindowVisible`` cannot answer.

Since Windows 8 a window can be shown as far as the window manager is concerned
and still be drawn nowhere: the compositor cloaks it instead of hiding it. Windows
does this to the windows of a packaged application it has suspended and to those
of a virtual desktop other than the one in use, and it is the reason a plain
visibility test finds windows belonging to applications the user closed long ago.

NVDA has no binding for the library that answers this, so this module makes its
own. It is the only piece of Windows this add-on has to reach for itself.
"""

import ctypes
from ctypes.wintypes import DWORD, HWND

#: ``DwmGetWindowAttribute``'s attribute number for the cloaked state. The value
#: that comes back says which of Windows' reasons for cloaking applies; that it
#: is not zero is all this add-on cares about.
DWMWA_CLOAKED = 14

_dwmapi = ctypes.WinDLL("dwmapi")
# The return value is deliberately typed as a plain long rather than as an
# HRESULT: ctypes turns a failing HRESULT into an exception, and a window whose
# state cannot be established is not an error worth raising here.
_DwmGetWindowAttribute = _dwmapi.DwmGetWindowAttribute
_DwmGetWindowAttribute.argtypes = (HWND, DWORD, ctypes.c_void_p, DWORD)
_DwmGetWindowAttribute.restype = ctypes.c_long

#: The one success code; every other value leaves the output untouched.
_S_OK = 0


def isCloaked(hwnd: int) -> bool:
	"""Whether the window manager is keeping this window off the screen.

	A window the call cannot be answered for counts as not cloaked. That is the
	forgiving way round: it leaves such a window in the list of running
	applications, where the user can see it and ignore it, rather than dropping
	an application they are actually using.
	"""
	cloaked = DWORD()
	result = _DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
	if result != _S_OK:
		return False
	return bool(cloaked.value)
