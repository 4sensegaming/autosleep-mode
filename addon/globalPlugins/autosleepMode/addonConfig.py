# Autosleep Mode: configuration handling
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2 or later.
# See the file COPYING.txt for more details.

"""Every setter writes only a value that differs from the stored one, and returns whether it did."""

from collections.abc import Iterable

import config

CONF_SECTION = "autosleepMode"

confspec = {
	"apps": "string_list(default=list())",
	"addManuallySleptApps": "boolean(default=False)",
	"removeManuallyWokenApps": "boolean(default=False)",
}


def initialize():
	config.conf.spec[CONF_SECTION] = confspec


def normalize(appName: str) -> str:
	return appName.strip().lower()


def _getBool(key: str) -> bool:
	try:
		return bool(config.conf[CONF_SECTION][key])
	except (KeyError, TypeError):
		return False


def _setBool(key: str, value: bool) -> bool:
	if _getBool(key) == value:
		return False
	config.conf[CONF_SECTION][key] = value
	return True


def getApps() -> list[str]:
	try:
		return list(config.conf[CONF_SECTION]["apps"])
	except (KeyError, TypeError):
		return []


def setApps(apps: Iterable[str]) -> bool:
	apps = list(apps)
	if apps == getApps():
		return False
	config.conf[CONF_SECTION]["apps"] = apps
	return True


def getAddManuallySleptApps() -> bool:
	return _getBool("addManuallySleptApps")


def setAddManuallySleptApps(value: bool) -> bool:
	return _setBool("addManuallySleptApps", value)


def getRemoveManuallyWokenApps() -> bool:
	return _getBool("removeManuallyWokenApps")


def setRemoveManuallyWokenApps(value: bool) -> bool:
	return _setBool("removeManuallyWokenApps", value)


def isListed(appName: str) -> bool:
	wanted = normalize(appName)
	return any(normalize(listed) == wanted for listed in getApps())


def addApp(appName: str) -> bool:
	apps = getApps()
	wanted = normalize(appName)
	if any(normalize(listed) == wanted for listed in apps):
		return False
	return setApps(sorted(apps + [appName], key=normalize))


def removeApp(appName: str) -> bool:
	wanted = normalize(appName)
	return setApps([listed for listed in getApps() if normalize(listed) != wanted])
