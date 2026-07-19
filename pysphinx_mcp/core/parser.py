"""MIT License

Copyright (c) 2026 vmphase

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from lxml import html as lxhtml

from pysphinx_mcp.core.utils import (
    API_KIND_TAGS,
    BLOCK_TAGS,
    COLLAPSE_BLANK_LINES_RE,
    COLLAPSE_SPACES_RE,
    CONTENT_ROOT_XPATHS,
    HEADING_TAGS,
    REMOVE_XPATH,
    TITLE_SUFFIX_RE,
)
from pysphinx_mcp.types import ApiSignature, Section


class PageParser:
    """Extracts text, sections, and API signatures from rendered Sphinx HTML."""

    @staticmethod
    def parse(html: str) -> lxhtml.HtmlElement:
        """Parse raw HTML into an lxml tree."""
        tree = lxhtml.fromstring(html)  # pyright: ignore[reportUnknownMemberType]
        if tree is None:
            raise ValueError("lxml.fromstring returned None")
        return tree

    @staticmethod
    def title(tree: lxhtml.HtmlElement) -> str:
        """Extract the document title from ``<title>`` or the first ``<h1>``."""
        if title := tree.findtext(".//title"):
            return TITLE_SUFFIX_RE.sub("", title.strip()).strip()
        return (tree.findtext(".//h1") or "").strip()

    @staticmethod
    def sections(tree: lxhtml.HtmlElement) -> list[Section]:
        """Extract h1-h4 headings as ``Section`` objects."""
        tree = PageParser.remove_chrome(tree)
        return [
            Section(level=str(el.tag), text=text, id=str(el.get("id", "")))
            for el in tree.iter(*HEADING_TAGS)
            if (text := el.text_content().strip())
        ]

    @staticmethod
    def text(tree: lxhtml.HtmlElement) -> str:
        """Return cleaned plain-text of the page body."""
        tree = PageParser.remove_chrome(tree)
        root = PageParser._find_content_root(tree)
        parts: list[str] = []

        PageParser._walk_text(root, parts)
        return PageParser._normalize_whitespace(" ".join(parts))

    @staticmethod
    def api_signature(
        tree: lxhtml.HtmlElement, object_path: str
    ) -> ApiSignature | None:
        """Extract a single API signature (function/class/method/...) by its anchor id."""
        heading = next(iter(tree.xpath(f"//dt[@id='{object_path}']")), None)
        if heading is None:
            return None

        description = heading.getnext()
        if description is None or description.tag != "dd":
            return None

        return ApiSignature(
            name=object_path.split(".")[-1],
            qualified_name=object_path,
            type=PageParser._api_kind(heading),
            signature=heading.text_content().strip(),
            parameters=[
                stripped
                for el in heading.xpath(".//*[contains(@class, 'sig-param')]")
                if (stripped := el.text_content().strip())
            ],
            docstring=PageParser._description_text(description),
            version_added=PageParser._version_added(description),
        )

    @staticmethod
    def remove_chrome(tree: lxhtml.HtmlElement) -> lxhtml.HtmlElement:
        """Remove navigation, sidebar, footer, etc. from the tree in place."""
        for element in tree.xpath(REMOVE_XPATH):
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
        return tree

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        text = COLLAPSE_SPACES_RE.sub(" ", text)
        text = COLLAPSE_BLANK_LINES_RE.sub("\n\n", text)
        return text.strip()

    @staticmethod
    def _find_content_root(tree: lxhtml.HtmlElement) -> lxhtml.HtmlElement:
        return next(
            (root for xpath in CONTENT_ROOT_XPATHS for root in tree.xpath(xpath)),
            tree,
        )

    @staticmethod
    def _walk_text(el: lxhtml.HtmlElement, parts: list[str]) -> None:
        tag = el.tag if isinstance(el.tag, str) else ""

        if el.text and (stripped := el.text.strip()):
            parts.append(stripped)

        for child in el:
            child_tag = child.tag if isinstance(child.tag, str) else ""
            if child_tag == "br":
                parts.append("\n")
            else:
                PageParser._walk_text(child, parts)

            if child.tail and (stripped_tail := child.tail.strip()):
                parts.append(stripped_tail)

        if tag in BLOCK_TAGS:
            parts.append("\n")

    @staticmethod
    def _api_kind(heading: lxhtml.HtmlElement) -> str:
        parent = heading.getparent()
        classes: list[str] = (
            parent.get("class", "").split() if parent is not None else []
        )
        return next((c for c in classes if c in API_KIND_TAGS), "unknown")

    @staticmethod
    def _version_added(description: lxhtml.HtmlElement) -> str | None:
        return next(
            (
                stripped
                for el in description.xpath(".//*[contains(@class, 'versionadded')]")
                if (stripped := el.text_content().strip())
            ),
            None,
        )

    @staticmethod
    def _description_text(description: lxhtml.HtmlElement) -> str:
        for nested in description.xpath(".//dl"):
            parent = nested.getparent()
            if parent is not None:
                parent.remove(nested)

        parts: list[str] = []
        PageParser._walk_text(description, parts)
        return PageParser._normalize_whitespace(" ".join(parts))
