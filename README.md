# pysphinx_mcp

MCP server for browsing, searching, and reading Sphinx documentation sites.

[![PyPI](https://img.shields.io/pypi/v/pysphinx_mcp)](https://pypi.org/project/pysphinx_mcp)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/github/license/vmphase/pysphinx_mcp)](LICENSE)

## Tools

- `list_pages(base_url)`: all pages on a docs site
- `read_page(base_url, page_path)`: page content as clean text
- `search_docs(base_url, query)`: full-text search via Sphinx search index
- `list_sections(base_url, page_path)`: heading structure (h1-h4) of a page
- `get_api_signature(base_url, object_path)`: signature, parameters, and docstring for a class or function

## Install

```
pip install -U pysphinx_mcp
```

## Usage

### As an MCP server

Register with any MCP host:

```json
{
    "mcpServers": {
        "sphinx-docs": {
            "command": "python",
            "args": ["-m", "pysphinx_mcp"]
        }
    }
}
```

Or run directly:

```
python -m pysphinx_mcp
```

### As a library

Each tool is an async function, import and call from your own code:

```python
from pysphinx_mcp import search_docs, read_page, get_api_signature

async def main():
    results = await search_docs(
        "https://docs.python.org/3/",
        "async await",
    )

    content = await read_page(
        "https://docs.python.org/3/",
        "library/asyncio.html",
    )

    signature = await get_api_signature(
        "https://docs.python.org/3/",
        "asyncio.gather",
    )

```

### Composing with other servers

Import the `FastMCP` instance for mounting or wrapping:

```python
from pysphinx_mcp import mcp

parent_server.mount(mcp)
```
