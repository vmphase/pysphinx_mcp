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

import re
from typing import Any, ClassVar

from lxml import html as lxhtml

from pysphinx_mcp.types import Section

_BLOCK_TAGS: frozenset[str] = frozenset(
    {
        "p",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "tr",
        "td",
        "th",
        "pre",
        "blockquote",
        "dl",
        "dd",
        "dt",
        "ul",
        "ol",
        "section",
        "article",
    },
)

_REMOVE_XPATH: str = (
    "//*[@role='navigation'] | //nav | //header | //footer | //aside | "
    "//*[contains(@class,'sidebar')] | //*[contains(@class,'sphinxsidebar')] | "
    "//*[contains(@class,'related')] | //*[@id='sidebar'] | //script | //style"
)


class PageParser:
    """Static methods for parsing Sphinx HTML pages with lxml.

    All lxml-related parameters are typed as ``Any`` because the
    ``lxml.html`` type stubs are incomplete (every attribute access
    returns ``Unknown`` under strict mode).  The runtime contract is
    still an ``lxml.html.HtmlElement``.
    """

    _title_re: ClassVar[re.Pattern[str]] = re.compile(r"\s*\u2014\s*.+$")

    @staticmethod
    def parse(html: str) -> Any:
        """Parse raw HTML into an lxml tree."""
        tree = lxhtml.fromstring(html)  # pyright: ignore[reportUnknownMemberType]
        if tree is None:
            raise ValueError("lxml.fromstring returned None")
        return tree

    @staticmethod
    def remove_chrome(tree: Any) -> Any:
        """Remove navigation, sidebar, footer etc. from the tree (in-place)."""
        for el in tree.xpath(_REMOVE_XPATH):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
        return tree

    @classmethod
    def title(cls, tree: Any) -> str:
        """Extract the document title from ``<title>`` or first ``<h1>``."""
        title_el = tree.xpath(".//title")
        if title_el and title_el[0].text:
            return cls._title_re.sub("", title_el[0].text.strip()).strip()
        h1 = tree.xpath(".//h1")
        if h1 and h1[0].text:
            return h1[0].text.strip()
        return ""

    @classmethod
    def text(cls, tree: Any) -> str:
        """Return cleaned plain-text of the page body."""
        tree = cls.remove_chrome(tree)
        root = cls._find_content_root(tree)
        parts: list[str] = []
        cls._walk_text(root, parts)
        raw = " ".join(parts)
        raw = re.sub(r"[ \t]+", " ", raw)
        return re.sub(r"\n{3,}", "\n\n", raw).strip()

    @staticmethod
    def _find_content_root(tree: Any) -> Any:
        for xp in (
            './/div[@role="main"]',
            './/div[@class="document"]',
            './/div[contains(@class,"body")]',
            ".//body",
        ):
            candidates = tree.xpath(xp)
            if candidates:
                return candidates[0]
        return tree

    @staticmethod
    def _walk_text(el: Any, parts: list[str]) -> None:
        tag = el.tag if isinstance(el.tag, str) else ""

        if el.text:
            t = el.text.strip()
            if t:
                parts.append(t)

        for child in el:
            child_tag = child.tag if isinstance(child.tag, str) else ""
            if child_tag == "br":
                parts.append("\n")
            else:
                PageParser._walk_text(child, parts)
            if child.tail:
                t = child.tail.strip()
                if t:
                    parts.append(t)

        if tag in _BLOCK_TAGS:
            parts.append("\n")

    @staticmethod
    def sections(tree: Any) -> list[Section]:
        """Extract h1-h4 headings as ``Section`` objects."""
        tree = PageParser.remove_chrome(tree)
        result: list[Section] = []
        for el in tree.iter("h1", "h2", "h3", "h4"):
            text = str(el.text_content().strip())
            if text:
                result.append(
                    Section(
                        level=str(el.tag),
                        text=text,
                        id=str(el.get("id", "")),
                    ),
                )
        return result
