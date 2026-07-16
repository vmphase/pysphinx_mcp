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

import json
import re
from typing import Any, ClassVar

from pysphinx_mcp.types._errors import SearchIndexError


class SearchIndex:
    """Wraps the parsed content of a Sphinx ``searchindex.js`` file."""

    _extract_re: ClassVar[re.Pattern[str]] = re.compile(
        r"Search\.setIndex\((\{.*\})\)\s*;?\s*$",
        re.DOTALL,
    )

    def __init__(self, data: dict[str, Any]) -> None:
        self._raw = data

    @classmethod
    def from_js(cls, content: str) -> SearchIndex:
        match = cls._extract_re.search(content)
        if not match:
            raise SearchIndexError(
                "could not locate Search.setIndex() in searchindex.js",
            )
        try:
            return cls(json.loads(match.group(1)))
        except json.JSONDecodeError as exc:
            raise SearchIndexError(str(exc)) from exc

    @property
    def docnames(self) -> list[str]:
        return list(self._raw.get("docnames", []))

    @property
    def titles(self) -> list[str]:
        return list(self._raw.get("titles", []))

    def path_for(self, docname: str) -> str:
        if docname in ("", "index"):
            return "index.html"
        return f"{docname}.html"

    def search(self, query: str) -> list[dict[str, str]]:
        q = query.lower()
        if not q:
            return []

        terms: dict[str, int | list[int]] = self._raw.get("terms", {})
        matched: set[int] = set()

        for term, ids in terms.items():
            if q in term.lower():
                if isinstance(ids, int):
                    matched.add(ids)
                else:
                    matched.update(ids)

        docnames = self.docnames
        titles = self.titles
        return [
            {"path": self.path_for(docnames[i]), "title": titles[i]}
            for i in sorted(matched)
            if i < len(titles) and titles[i]
        ]
