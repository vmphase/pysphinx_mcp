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

from pysphinx_mcp._version import __version__, version_info
from pysphinx_mcp.core._service import DocsService

__all__ = (
    "__version__",
    "get_api_signature",
    "list_pages",
    "list_sections",
    "read_page",
    "search_docs",
    "version_info",
)

_service = DocsService()


async def list_pages(base_url: str) -> list[dict[str, str]]:
    """List all documentation pages at a Sphinx docs site.

    Parameters
    ----------
    base_url : str
        Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
    """
    return await _service.list_pages(base_url)


async def search_docs(base_url: str, query: str) -> list[dict[str, str]]:
    """Search documentation pages for a term. Uses the Sphinx search index.

    Parameters
    ----------
    base_url : str
        Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
    query : str
        Text to search for (case-insensitive)
    """
    return await _service.search(base_url, query)


async def read_page(base_url: str, page_path: str) -> str:
    """Read the full text content of a documentation page.

    Parameters
    ----------
    base_url : str
        Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
    page_path : str
        Relative path to the page (e.g. index.html, library/stdtypes.html)
    """
    return await _service.read(base_url, page_path)


async def list_sections(base_url: str, page_path: str) -> list[dict[str, str]]:
    """List section headings (h1-h4) within a documentation page.

    Parameters
    ----------
    base_url : str
        Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
    page_path : str
        Relative path to the page (e.g. index.html)
    """
    return await _service.sections(base_url, page_path)


async def get_api_signature(
    base_url: str,
    object_path: str,
) -> dict[str, object] | None:
    """Resolve a specific class/function from autodoc-generated pages and
    return its signature, parameters and docstring (not the whole page).

    Parameters
    ----------
    base_url : str
        Root URL of the Sphinx documentation (e.g. https://docs.python.org/3/)
    object_path : str
        Fully qualified name of the object (e.g. os.path.join,
        collections.OrderedDict.popitem)
    """
    return await _service.api_signature(base_url, object_path)
