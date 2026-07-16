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

from curl_cffi.requests import AsyncSession

from pysphinx_mcp.types._errors import FetchError


class PageFetcher:
    """Async HTTP client that fetches Sphinx documentation pages.

    Shares a single ``curl_cffi`` session with Chrome impersonation
    to avoid CDN blocks.  Instantiate once and reuse.
    """

    def __init__(self) -> None:
        self._session: Any = None

    async def _get_session(self) -> Any:
        if self._session is None:
            self._session = AsyncSession(impersonate="chrome")
        return self._session

    async def fetch(self, url: str, *, timeout: float = 30.0) -> str:
        """GET *url* and return the response body as text."""
        session: Any = await self._get_session()
        try:
            resp: Any = await session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            raise FetchError(str(exc)) from exc

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None
