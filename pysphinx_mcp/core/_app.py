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

import logging

from mcp.server.fastmcp import FastMCP

from pysphinx_mcp.core._service import DocsService

logger = logging.getLogger(__name__)


def create_app() -> FastMCP:
    """Build and return a configured ``FastMCP`` instance.

    Wiring is internal — the service owns a single ``PageFetcher`` and
    gets cleaned up when the process exits.
    """
    logger.info("Initializing Sphinx MCP...")
    service = DocsService()

    mcp = FastMCP(
        "Sphinx MCP",
        instructions="Read and search Sphinx-generated documentations. "
        "Provide a base URL to any Sphinx docs site to browse, search, "
        "and read pages using the Sphinx search index for fast lookups.",
    )

    @mcp.tool()
    async def list_pages(  # pyright: ignore[reportUnusedFunction]
        base_url: str,
    ) -> list[dict[str, str]]:
        """List all documentation pages at a Sphinx docs site.

        Parameters
        ----------
        base_url : str
            Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
        """
        return await service.list_pages(base_url)

    @mcp.tool()
    async def search_docs(  # pyright: ignore[reportUnusedFunction]
        base_url: str,
        query: str,
    ) -> list[dict[str, str]]:
        """Search documentation pages for a term. Uses the Sphinx search index.

        Parameters
        ----------
        base_url : str
            Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
        query : str
            Text to search for (case-insensitive)
        """
        return await service.search(base_url, query)

    @mcp.tool()
    async def read_page(  # pyright: ignore[reportUnusedFunction]
        base_url: str,
        page_path: str,
    ) -> str:
        """Read the full text content of a documentation page.

        Parameters
        ----------
        base_url : str
            Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
        page_path : str
            Relative path to the page (e.g. index.html, library/stdtypes.html)
        """
        return await service.read(base_url, page_path)

    @mcp.tool()
    async def list_sections(  # pyright: ignore[reportUnusedFunction]
        base_url: str,
        page_path: str,
    ) -> list[dict[str, str]]:
        """List section headings (h1-h4) within a documentation page.

        Parameters
        ----------
        base_url : str
            Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
        page_path : str
            Relative path to the page (e.g. index.html)
        """
        return await service.sections(base_url, page_path)

    logger.info("Initialized successfully: 4 tools registered.")
    return mcp
