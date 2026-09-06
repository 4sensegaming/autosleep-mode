"""
This tool generates NVDA extensions.

Builders:

- NVDAAddon: Creates a .nvda-addon zip file. Requires the `excludePatterns` environment variable.
- NVDAManifest: Creates the manifest.ini file.
- NVDATranslatedManifest: Creates the manifest.ini file with only translated information.
- md2html: Build HTML from Markdown

The following environment variables are required to create the manifest:

- addon_info: .typing.AddonInfo
- brailleTables: .typings.BrailleTables
- symbolDictionaries: .typings.SymbolDictionaries

The following environment variables are required to build the HTML:

- moFile: str | pathlib.Path | None
- mdExtensions: list[str]
- addon_info: .typings.AddonInfo

"""

from SCons.Node.FS import Base as FSNode
from SCons.Script import Environment, Builder

from .addon import createAddonBundleFromPath
from .manifests import generateManifest, generateTranslatedManifest
from .docs import md2html


#: What SCons hands an action for its targets and for its sources: file or
#: directory nodes, whose path and abspath are the names of those on disk.
type Nodes = list[FSNode]


# Each builder below is given a pair of named functions rather than the lambdas
# these replace, because a lambda cannot carry annotations and what SCons passes
# an action would go unstated. An action reports success by returning nothing,
# which is what the "and None" trailing each of those lambdas was arranging by
# hand and what a function with no return statement does on its own. The second
# of each pair is the line printed while the target is built.


def _buildAddon(target: Nodes, source: Nodes, env: Environment) -> None:
	createAddonBundleFromPath(source[0].abspath, target[0].abspath, env["excludePatterns"])


def _describeAddon(target: Nodes, source: Nodes, env: Environment) -> str:
	return f"Generating Addon {target[0]}"


def _buildManifest(target: Nodes, source: Nodes, env: Environment) -> None:
	generateManifest(
		source[0].abspath,
		target[0].abspath,
		addon_info=env["addon_info"],
		brailleTables=env["brailleTables"],
		symbolDictionaries=env["symbolDictionaries"],
	)


def _describeManifest(target: Nodes, source: Nodes, env: Environment) -> str:
	return f"Generating manifest {target[0]}"


def _buildTranslatedManifest(target: Nodes, source: Nodes, env: Environment) -> None:
	generateTranslatedManifest(
		source[1].abspath,
		target[0].abspath,
		mo=source[0].abspath,
		addon_info=env["addon_info"],
		brailleTables=env["brailleTables"],
		symbolDictionaries=env["symbolDictionaries"],
	)


def _describeTranslatedManifest(target: Nodes, source: Nodes, env: Environment) -> str:
	return f"Generating translated manifest {target[0]}"


def _buildHtml(target: Nodes, source: Nodes, env: Environment) -> None:
	# Held in a name rather than read twice: a language whose mo file is missing
	# passes None here, and only a name is narrow enough for the checker to see
	# that the attribute is read on the branch where there is one.
	moFile = env["moFile"]
	md2html(
		source[0].path,
		target[0].path,
		moFile=moFile.path if moFile else None,
		mdExtensions=env["mdExtensions"],
		addon_info=env["addon_info"],
	)


def _describeHtml(target: Nodes, source: Nodes, env: Environment) -> str:
	return f"Generating {target[0]}"


def generate(env: Environment):
	env.SetDefault(excludePatterns=tuple())

	addonAction = env.Action(_buildAddon, _describeAddon)
	# Builders are registered through Append rather than by assigning into
	# env["BUILDERS"]: SCons documents the two as equivalent, and Append says what
	# is meant without going through a subscript whose value the environment
	# declares as possibly None. BUILDERS holds a dictionary that installs each
	# builder as a method of the environment as it is added, so appending one is
	# what makes env.NVDAAddon and the rest callable below.
	env.Append(
		BUILDERS={
			"NVDAAddon": Builder(
				action=addonAction,
				suffix=".nvda-addon",
				src_suffix="/"
			)
		}
	)

	env.SetDefault(brailleTables={})
	env.SetDefault(symbolDictionaries={})

	manifestAction = env.Action(_buildManifest, _describeManifest)
	env.Append(
		BUILDERS={
			"NVDAManifest": Builder(
				action=manifestAction,
				suffix=".ini",
				src_suffix=".ini.tpl"
			)
		}
	)

	translatedManifestAction = env.Action(_buildTranslatedManifest, _describeTranslatedManifest)
	env.Append(
		BUILDERS={
			"NVDATranslatedManifest": Builder(
				action=translatedManifestAction,
				suffix=".ini",
				src_suffix=".ini.tpl"
			)
		}
	)

	env.SetDefault(mdExtensions = {})

	mdAction = env.Action(_buildHtml, _describeHtml)
	env.Append(
		BUILDERS={
			"md2html": env.Builder(
				action=mdAction,
				suffix=".html",
				src_suffix=".md",
			)
		}
	)


def exists():
	return True
