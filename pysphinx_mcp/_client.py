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

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Self

from curl_cffi.requests import AsyncSession

from pysphinx_mcp.types._errors import DocsClientError


class AsyncDocsClient:
    """Async HTTP client with a lock-guarded session."""

    def __init__(self) -> None:
        self._session: AsyncSession[Any] | None = None
        self._lock = asyncio.Lock()

    async def _ensure_session(self) -> AsyncSession[Any]:
        """Return the shared session, creating it under a lock if needed."""
        if self._session is not None:
            return self._session
        async with self._lock:
            if self._session is None:
                self._session = AsyncSession(impersonate="chrome")
        return self._session

    async def fetch_text(self, url: str, *, timeout: float = 30.0) -> str:
        """Fetch *url* and return the response body as text.

        Raises ``DocsClientError`` for any network, timeout, or
        non-2xx response.
        """
        session = await self._ensure_session()
        try:
            resp = await session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            raise DocsClientError(str(exc)) from exc

    async def close(self) -> None:
        """Close the underlying session, if one was opened."""
        if self._session is None:
            return
        await self._session.close()
        self._session = None

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[Self]:
        """Yield ``self``, closing the session on exit even if an error occurs."""
        try:
            yield self
        finally:
            await self.close()
