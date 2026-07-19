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

from typing import Any

import msgspec

from pysphinx_mcp.core.utils import EXTRACT_RE
from pysphinx_mcp.types.errors import SearchIndexError


class SearchIndex:
    """Wraps the parsed content of a Sphinx ``searchindex.js`` file."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._raw = data

    @classmethod
    def from_js(cls, content: str) -> SearchIndex:
        """Parse a ``searchindex.js`` payload."""
        match = EXTRACT_RE.search(content)
        if not match:
            raise SearchIndexError(
                "could not locate Search.setIndex() in searchindex.js"
            )

        try:
            return cls(msgspec.json.decode(match.group(1)))
        except msgspec.ValidationError as exc:
            raise SearchIndexError(str(exc)) from exc

    @property
    def docnames(self) -> list[str]:
        """Document names, in index order."""
        return list(self._raw.get("docnames", []))

    @property
    def titles(self) -> list[str]:
        """Document titles, in the same order as ``docnames``."""
        return list(self._raw.get("titles", []))

    def path_for(self, docname: str) -> str:
        """Return the HTML path for a given document name."""
        if docname in ("", "index"):
            return "index.html"
        return f"{docname}.html"

    def search(self, query: str) -> list[dict[str, str]]:
        """Return ``{"path", "title"}`` hits whose indexed term contains ``query``."""
        needle = query.lower()
        if not needle:
            return []

        terms: dict[str, int | list[int]] = self._raw.get("terms", {})
        matched: set[int] = set()

        for term, ids in terms.items():
            if needle not in term.lower():
                continue
            matched.update(ids if isinstance(ids, list) else (ids,))

        return [
            {"path": self.path_for(self.docnames[i]), "title": self.titles[i]}
            for i in sorted(matched)
            if i < len(self.docnames) and i < len(self.titles) and self.titles[i]
        ]
