
import gettext
from functools import partial

from .typings import AddonInfo, BrailleTables, SymbolDictionaries
from .utils import format_nested_section


# Every template and manifest below is opened with newline="", so its line endings
# are carried through untouched instead of being translated to those of whichever
# platform ran the build: the templates are CRLF, and the manifests generated from
# them stay that way. The deprecated codecs.open these calls replace did the same,
# by working in binary underneath.



def generateManifest(
		source: str,
		dest: str,
		addon_info: AddonInfo,
		brailleTables: BrailleTables,
		symbolDictionaries: SymbolDictionaries,
	):
	# Prepare the root manifest section
	with open(source, "r", encoding="utf-8", newline="") as f:
		manifest_template = f.read()
	manifest = manifest_template.format(**addon_info)
	# Add additional manifest sections such as custom braile tables
	# Custom braille translation tables
	if brailleTables:
		manifest += format_nested_section("brailleTables", brailleTables)

	# Custom speech symbol dictionaries
	if symbolDictionaries:
		manifest += format_nested_section("symbolDictionaries", symbolDictionaries)

	with open(dest, "w", encoding="utf-8", newline="") as f:
		f.write(manifest)


def generateTranslatedManifest(
		source: str,
		dest: str,
		*,
		mo: str,
		addon_info: AddonInfo,
		brailleTables: BrailleTables,
		symbolDictionaries: SymbolDictionaries,
	):
	with open(mo, "rb") as f:
		_ = gettext.GNUTranslations(f).gettext
	vars: dict[str, str] = {}
	for var in ("addon_summary", "addon_description", "addon_changelog"):
		vars[var] = _(addon_info[var])
	with open(source, "r", encoding="utf-8", newline="") as f:
		manifest_template = f.read()
	manifest = manifest_template.format(**vars)

	_format_section_only_with_displayName = partial(
		format_nested_section,
		include_only_keys = ("displayName",),
		_ = _,
	)

	# Add additional manifest sections such as custom braile tables
	# Custom braille translation tables
	if brailleTables:
		manifest += _format_section_only_with_displayName("brailleTables", brailleTables)

	# Custom speech symbol dictionaries
	if symbolDictionaries:
		manifest += _format_section_only_with_displayName("symbolDictionaries", symbolDictionaries)

	with open(dest, "w", encoding="utf-8", newline="") as f:
		f.write(manifest)
