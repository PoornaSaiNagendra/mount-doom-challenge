"""
Queue abstraction using asyncio.Queue.
"""
import asyncio
from typing import Any, Optional

class AsyncQueue:
    """
    Wrapper around asyncio.Queue to manage back-pressure and graceful shutdown.
    """
    def __init__(self, maxsize: int = 0):
        self._queue = asyncio.Queue(maxsize=maxsize)

    async def put(self, item: Any) -> None:
        """
        Put an item into the queue; waits if full.
        """
        await self._queue.put(item)

    async def get(self) -> Any:
        """
        Retrieve and remove an item from the queue.
        """
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()

    async def join(self) -> None:
        await self._queue.join()

    def empty(self) -> bool:
        return self._queue.empty()

    def full(self) -> bool:
        return self._queue.full()
