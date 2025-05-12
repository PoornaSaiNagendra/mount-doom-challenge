import aiohttp
import asyncio
import json
import logging
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import AsyncGenerator, Dict, Any, Optional

from .models import Transcript, ProcessedResult

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class APIClient:
    """
    Asynchronous client for interacting with the Mordor transcripts API.
    Handles authentication, streaming transcripts, and submitting processed results.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://relaxing-needed-vulture.ngrok-free.app/api",
        max_retries: int = 3,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
        self.max_retries = max_retries
        self.timeout = timeout

    async def authenticate(self) -> None:
        """
        Obtain a Bearer token using the API key.
        """
        auth_url = f"{self.base_url}/auth"
        payload = {"api_key": self.api_key}

        for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(min=1, max=10),
            retry=retry_if_exception_type(aiohttp.ClientError),
        ):
            with attempt:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(auth_url, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        self.token = data.get("token")
                        if not self.token:
                            raise RuntimeError("Authentication succeeded but token missing in response")
                        self.headers["Authorization"] = f"Bearer {self.token}"
                        logger.info("Authentication succeeded")
                        return

        raise RuntimeError("Failed to authenticate after retries")

    async def stream_transcripts(self) -> AsyncGenerator[Transcript, None]:
        """
        Connect to the streaming endpoint and yield Transcript objects line by line.
        """
        if not self.token:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        url = f"{self.base_url}/v1/transcripts/stream"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None)) as session:
            async with session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                async for raw in resp.content:
                    if not raw:
                        continue
                    try:
                        data = json.loads(raw.decode())
                        yield Transcript.parse_obj(data)
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.error(f"Failed to parse transcript: {e}")
                        continue

    async def submit_processed(
        self, result: ProcessedResult
    ) -> Dict[str, Any]:
        """
        Submit a processed result JSON back to the API, with retries on transient failures.
        """
        if not self.token:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        url = f"{self.base_url}/v1/transcripts/process"
        payload = result.dict()

        for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(min=1, max=10),
            retry=retry_if_exception_type(aiohttp.ClientError),
        ):
            with attempt:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    async with session.post(url, headers=self.headers, json=payload) as resp:
                        resp.raise_for_status()
                        response_data = await resp.json()
                        logger.info(f"Submitted result for {result.transcript_id}")
                        return response_data

        raise RuntimeError(f"Failed to submit result for {result.transcript_id} after retries")

    async def get_stats(self) -> Dict[str, Any]:
        """
        Fetch processing statistics from the API.
        """
        if not self.token:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        url = f"{self.base_url}/v1/stats"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                logger.info("Fetched stats")
                return data

    async def health_check(self) -> bool:
        """
        Check the health endpoint; return True if status OK.
        """
        url = f"{self.base_url}/v1/health"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as resp:
                    return resp.status == 200
        except aiohttp.ClientError:
            return False
