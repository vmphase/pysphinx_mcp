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

import msgspec


class PageInfo(msgspec.Struct):
    """A single page discovered in a Sphinx docs site."""

    path: str
    """Page path relative to the docs base URL, e.g. ``api/foo.html``."""

    title: str
    """Page title, as shown in the site's nav/search index."""


class Section(msgspec.Struct):
    """A heading found within a page."""

    level: str
    """Heading level, e.g. ``"1"``-``"4"`` for h1-h4."""

    text: str
    """Rendered heading text."""

    id: str
    """The heading's HTML anchor id, usable as a URL fragment."""


class ApiSignature(msgspec.Struct):
    """A parsed API entry (function, method, or class) from a docs page."""

    name: str
    """Short name of the object, e.g. ``"read"``."""

    qualified_name: str
    """Fully qualified dotted path, e.g. ``"pysphinx_mcp.DocsService.read"``."""

    type: str
    """Kind of object, e.g. ``"function"``, ``"method"``, or ``"class"``."""

    signature: str
    """Rendered call signature, e.g. ``"(base_url: str, page_path: str) -> str"``."""

    parameters: list[str]
    """Parameter names/descriptions as extracted from the signature."""

    docstring: str
    """The object's docstring text, as rendered in the docs."""

    version_added: str | None = None
    """Version the object was introduced in, if the docs record one."""
