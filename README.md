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

## Install

```
pip install -U pysphinx_mcp
```

## Usage

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

Use `--log-level` to control logging verbosity (default: `INFO`):

```
python -m pysphinx_mcp --log-level DEBUG
```
