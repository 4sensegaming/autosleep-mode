
import gettext
import re
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

from .typings import AddonInfo


#: An href pointing at a markdown file next to this one, with any fragment it carries.
#: Anything with a scheme in front of it is somebody else's document and is left alone.
RELATIVE_MD_LINK = re.compile(r'(href="(?!\w+:)[^"]+)\.md(#[^"]*)?"')



def md2html(
		source: str | Path,
		dest: str | Path,
		*,
		moFile: str | Path|None,
		mdExtensions: list[str],
		addon_info: AddonInfo
	):
	if isinstance(source, str):
		source = Path(source)
	if isinstance(dest, str):
		dest = Path(dest)
	if isinstance(moFile, str):
		moFile = Path(moFile)

	try:
		with moFile.open("rb") as f:
			_ = gettext.GNUTranslations(f).gettext
	except Exception:
		summary = addon_info["addon_summary"]
	else:
		summary = _(addon_info["addon_summary"])
	version = addon_info["addon_version"]
	title = f"{summary} {version}"
	lang = source.parent.name.replace("_", "-")
	headerDic = {
		'[[!meta title="': "# ",
		'"]]': " #",
	}
	with source.open("r", encoding="utf-8") as f:
		mdText = f.read()
	for k, v in headerDic.items():
		mdText = mdText.replace(k, v, 1)
	# GitHub renders these very markdown files as well, and slugs its heading anchors
	# without stripping diacritics, so the toc extension is asked to keep them too.
	# A link such as (#nastavení) would otherwise have to be spelt one way for GitHub
	# and another for the html shipped with the add-on. Configuration for an extension
	# that is not loaded is ignored, so this stays inert if toc is taken out again.
	htmlText = markdown.markdown(
		mdText,
		extensions=mdExtensions,
		extension_configs={"toc": {"slugify": slugify_unicode}},
	)
	# The readmes link to one another by their markdown names, which is what GitHub
	# needs. Here it is the generated html that sits next to them, so the links follow.
	htmlText = RELATIVE_MD_LINK.sub(lambda m: f'{m[1]}.html{m[2] or ""}"', htmlText)
	# Optimization: build resulting HTML text in one go instead of writing parts separately.
	docText = "\n".join(
		(
			"<!DOCTYPE html>",
			f'<html lang="{lang}">',
			"<head>",
			'<meta charset="UTF-8">',
			'<meta name="viewport" content="width=device-width, initial-scale=1.0">',
			'<link rel="stylesheet" type="text/css" href="../style.css" media="screen">',
			f"<title>{title}</title>",
			"</head>\n<body>",
			htmlText,
			"</body>\n</html>",
		)
	)
	with dest.open("w", encoding="utf-8") as f:
		f.write(docText) # type: ignore
