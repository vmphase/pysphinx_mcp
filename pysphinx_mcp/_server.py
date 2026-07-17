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

import pysphinx_mcp

mcp = FastMCP(
    "Sphinx Docs Reader",
    instructions="Read and search Sphinx-generated documentation sites. "
    "Provide a base URL to any Sphinx docs site to browse, search, "
    "and read pages using the Sphinx search index for fast lookups.",
)

mcp.tool()(pysphinx_mcp.list_pages)
mcp.tool()(pysphinx_mcp.search_docs)
mcp.tool()(pysphinx_mcp.read_page)
mcp.tool()(pysphinx_mcp.list_sections)
mcp.tool()(pysphinx_mcp.get_api_signature)
