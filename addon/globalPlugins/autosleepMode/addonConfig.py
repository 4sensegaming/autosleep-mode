# Autosleep Mode: configuration handling
# Copyright (C) 2026 Lukáš Hosnedl
# This file is covered by the GNU General Public License, version 2.
# See the file COPYING.txt for more details.

"""Configuration specification, defaults and small accessor helpers.

The specification is registered with NVDA so that the values are typed, validated,
honoured by configuration profiles and written out whenever NVDA saves its own
configuration. Nothing here ever calls ``config.conf.save()``: a change reaches
the disk only when NVDA itself saves, on request or on exit, exactly like every
other NVDA setting.

Every read goes to NVDA's live configuration rather than to a cached copy, so a
profile switch takes effect immediately with no further bookkeeping. All of this
belongs on NVDA's main thread.
"""

from typing import List

import config

#: The key of our section inside NVDA's configuration.
CONF_SECTION = "autosleepMode"

#: Configuration specification (types and defaults).
confspec = {
	# The application names, as NVDA reports them, whose windows put NVDA to sleep.
	"apps": "string_list(default=list())",
	# Whether switching sleep mode on by hand also adds that application to `apps`.
	"addManuallySleptApps": "boolean(default=False)",
	# Whether switching sleep mode off by hand also takes that application out of `apps`.
	# Independent of the option above: either may be on without the other, and the
	# add-on has no reason to care whether they agree.
	"removeManuallyWokenApps": "boolean(default=False)",
}


def initialize():
	"""Register the configuration specification with NVDA. Main thread only."""
	config.conf.spec[CONF_SECTION] = confspec


def normalize(appName: str) -> str:
	"""Return the form of an application name used for comparisons.

	NVDA already lowercases the names it derives from an executable, but a name
	typed into a configuration file by hand or supplied by an app module's
	``getAppNameFromHost`` need not be, so matching is case insensitive.
	"""
	return appName.strip().lower()


def getApps() -> List[str]:
	"""The application names that should be put to sleep, as stored.

	A copy is returned: the list NVDA hands back is the one it caches, and
	mutating it in place would change the setting behind the configuration
	manager's back.
	"""
	try:
		return list(config.conf[CONF_SECTION]["apps"])
	except (KeyError, TypeError):
		return []


def setApps(apps):
	"""Replace the list of application names to put to sleep."""
	config.conf[CONF_SECTION]["apps"] = list(apps)


def getAddManuallySleptApps() -> bool:
	"""Whether an application slept by hand joins the list automatically."""
	try:
		return config.conf[CONF_SECTION]["addManuallySleptApps"]
	except (KeyError, TypeError):
		return False


def setAddManuallySleptApps(value: bool):
	config.conf[CONF_SECTION]["addManuallySleptApps"] = value


def getRemoveManuallyWokenApps() -> bool:
	"""Whether an application woken by hand leaves the list automatically."""
	try:
		return config.conf[CONF_SECTION]["removeManuallyWokenApps"]
	except (KeyError, TypeError):
		return False


def setRemoveManuallyWokenApps(value: bool):
	config.conf[CONF_SECTION]["removeManuallyWokenApps"] = value


def isListed(appName: str) -> bool:
	"""Whether this application should be put to sleep."""
	wanted = normalize(appName)
	return any(normalize(listed) == wanted for listed in getApps())


def addApp(appName: str):
	"""Add an application to the list, unless it is already there."""
	if isListed(appName):
		return
	setApps(sorted(getApps() + [appName], key=normalize))


def removeApp(appName: str):
	"""Take an application off the list, if it is on it.

	Nothing is written when it is not, so that this cannot mark the configuration
	as changed on an application the user never listed.
	"""
	if not isListed(appName):
		return
	wanted = normalize(appName)
	setApps([listed for listed in getApps() if normalize(listed) != wanted])
