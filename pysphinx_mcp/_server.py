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

from mcp.server.fastmcp import FastMCP

from pysphinx_mcp.core._service import DocsService

_service = DocsService()

mcp = FastMCP(
    "Sphinx Docs Reader",
    instructions="Read and search Sphinx-generated docs."
    "Provide a base URL to any Sphinx docs site to browse, search, "
    "and read pages using the Sphinx search index for fast lookups.",
)


async def list_pages(base_url: str) -> list[dict[str, str]]:
    return await _service.list_pages(base_url)


async def search_docs(base_url: str, query: str) -> list[dict[str, str]]:
    return await _service.search(base_url, query)


async def read_page(base_url: str, page_path: str) -> str:
    return await _service.read(base_url, page_path)


async def list_sections(base_url: str, page_path: str) -> list[dict[str, str]]:
    return await _service.sections(base_url, page_path)


async def get_api_signature(
    base_url: str,
    object_path: str,
) -> dict[str, object] | None:
    return await _service.api_signature(base_url, object_path)


mcp.tool()(list_pages)
mcp.tool()(search_docs)
mcp.tool()(read_page)
mcp.tool()(list_sections)
mcp.tool()(get_api_signature)
