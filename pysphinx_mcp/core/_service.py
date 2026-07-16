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
import logging
from functools import lru_cache
from typing import Any
from urllib.parse import urljoin

from pysphinx_mcp.core._fetcher import PageFetcher
from pysphinx_mcp.core._parser import PageParser
from pysphinx_mcp.core._search import SearchIndex
from pysphinx_mcp.types._errors import FetchError, SearchIndexError

logger = logging.getLogger(__name__)


def _normalise(base: str) -> str:
    return base.rstrip("/") + "/"


@lru_cache(maxsize=32)
def _resolve(base: str) -> str:
    return _normalise(base)


class DocsService:
    """Orchestrates fetching, parsing and searching of Sphinx docs.

    Shares a single ``PageFetcher`` — call ``close()`` to release
    the underlying HTTP session.
    """

    def __init__(self, fetcher: PageFetcher | None = None) -> None:
        self._fetcher = fetcher or PageFetcher()

    async def close(self) -> None:
        await self._fetcher.close()

    async def list_pages(self, base_url: str) -> list[dict[str, str]]:
        """Return every page discovered via the Sphinx search index."""
        base = _resolve(base_url)
        try:
            js = await self._fetcher.fetch(urljoin(base, "searchindex.js"))
            pages = self._from_index(js)
            logger.info("Listed %d page(s) for %s via search index", len(pages), base)
            return self._from_index(js)
        except (FetchError, SearchIndexError, json.JSONDecodeError) as exc:
            logger.info(
                "Search index unavailable for %s (%s) \u2014 falling back to scrape",
                base,
                exc,
            )
            return await self._scrape(base)

    async def read(self, base_url: str, page_path: str) -> str:
        """Fetch a page and return cleaned markdown-like text."""
        base = _resolve(base_url)
        if not page_path.startswith("http"):
            url = urljoin(base, page_path)
        else:
            url = page_path

        try:
            html = await self._fetcher.fetch(url)
        except FetchError as exc:
            logger.warning("Could not fetch %s: %s", url, exc)
            return f"Error: could not fetch '{url}' \u2014 {exc}"

        try:
            tree = PageParser.parse(html)
        except ValueError as exc:
            logger.warning("Could not parse %s: %s", url, exc)
            return f"Error: could not parse '{url}' \u2014 {exc}"

        logger.debug("Read page %s", url)
        return f"# {PageParser.title(tree)}\n\n{PageParser.text(tree)}"

    async def search(self, base_url: str, query: str) -> list[dict[str, str]]:
        """Search the docs search index for *query*."""
        base = _resolve(base_url)
        query_lower = query.lower()

        try:
            js = await self._fetcher.fetch(urljoin(base, "searchindex.js"))
            results = SearchIndex.from_js(js).search(query_lower)
            logger.info(
                "Search %r on %s returned %d result(s) via index",
                query,
                base,
                len(results),
            )
            return results
        except (FetchError, SearchIndexError) as exc:
            logger.info(
                "Search index unavailable for %s (%s) \u2014 falling back to page scan",
                base,
                exc,
            )

        pages = await self.list_pages(base_url)
        results: list[dict[str, str]] = []
        for p in pages:
            if await self._page_contains(base, p["path"], query_lower):
                results.append(p)
        logger.info(
            "Search %r on %s returned %d result(s) via page scan",
            query,
            base,
            len(results),
        )
        return results

    async def sections(self, base_url: str, page_path: str) -> list[dict[str, Any]]:
        """Return the h1-h4 headings of *page_path*."""
        base = _resolve(base_url)
        if not page_path.startswith("http"):
            url = urljoin(base, page_path)
        else:
            url = page_path

        try:
            tree = PageParser.parse(await self._fetcher.fetch(url))
        except (FetchError, ValueError) as exc:
            logger.warning("Could not extract sections from %s: %s", url, exc)
            return [{"error": str(exc)}]

        sections = [
            {"level": s.level, "text": s.text, "id": s.id}
            for s in PageParser.sections(tree)
        ]
        logger.debug("Extracted %d section(s) from %s", len(sections), url)
        return sections

    @staticmethod
    def _from_index(js: str) -> list[dict[str, str]]:
        idx = SearchIndex.from_js(js)
        return [
            {"path": idx.path_for(d), "title": t}
            for d, t in zip(idx.docnames, idx.titles, strict=False)
            if t
        ]

    async def _scrape(self, base: str) -> list[dict[str, str]]:
        try:
            tree = PageParser.parse(
                await self._fetcher.fetch(urljoin(base, "index.html")),
            )
        except (FetchError, ValueError) as exc:
            logger.warning("Scrape fallback failed for %s: %s", base, exc)
            return []

        seen: set[str] = set()
        result: list[dict[str, str]] = []
        for a in tree.iter("a"):
            href = a.get("href")
            if (
                not href
                or not href.endswith(".html")
                or href.startswith(("http:", "https:", "//"))
            ):
                continue

            if href in seen:
                continue

            seen.add(href)
            result.append(
                {
                    "path": href,
                    "title": str(a.text_content().strip()) or href,
                },
            )

        logger.debug("Scraped %d link(s) from %sindex.html", len(result), base)
        return result

    async def _page_contains(self, base: str, path: str, query: str) -> bool:
        try:
            tree = PageParser.parse(await self._fetcher.fetch(urljoin(base, path)))
            return query in PageParser.text(tree).lower()
        except (FetchError, ValueError):
            logger.debug("Skipping %s during page scan: %s", path, exc)
            return False
