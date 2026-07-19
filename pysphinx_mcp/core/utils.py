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

BLOCK_TAGS: frozenset[str] = frozenset(
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
HEADING_TAGS: tuple[str, ...] = ("h1", "h2", "h3", "h4")
API_KIND_TAGS: frozenset[str] = frozenset(
    {
        "function",
        "class",
        "method",
        "property",
        "staticmethod",
        "classmethod",
        "attribute",
    },
)

REMOVE_XPATH: str = (
    "//*[@role='navigation'] | //nav | //header | //footer | //aside | "
    "//*[contains(@class,'sidebar')] | //*[contains(@class,'sphinxsidebar')] | "
    "//*[contains(@class,'related')] | //*[@id='sidebar'] | //script | //style"
)
CONTENT_ROOT_XPATHS: tuple[str, ...] = (
    './/div[@role="main"]',
    './/div[@class="document"]',
    './/div[contains(@class,"body")]',
    ".//body",
)

TITLE_SUFFIX_RE = re.compile(r"\s*\u2014\s*.+$")
COLLAPSE_SPACES_RE = re.compile(r"[ \t]+")
COLLAPSE_BLANK_LINES_RE = re.compile(r"\n{3,}")

EXTRACT_RE: re.Pattern[str] = re.compile(
    r"Search\.setIndex\((\{.*\})\)\s*;?\s*$",
    re.DOTALL,
)
