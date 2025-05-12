# file: src/app.py
"""
Main application wiring together ingestion, processing, storage, and submission.
"""
import asyncio
import signal
import logging
from datetime import datetime, timezone
from typing import Optional

from api.client import APIClient
from api.models import Transcript
from queue.queue import AsyncQueue
from processing.summarizer import summarize_transcript
from processing.extractor import extract_structured_data
from processing.analyzer import analyze_transcript
from storage.db import save_raw_transcript, save_processed_result, init_db

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Configuration parameters
API_KEY = "candidate-api-key-587e61ac"
BASE_URL = "https://relaxing-needed-vulture.ngrok-free.app/api"
CONCURRENCY = 20
QUEUE_MAXSIZE = 1000

async def worker(name: int, client: APIClient, work_q: AsyncQueue, dlq: AsyncQueue) -> None:
    """
    Worker task: pull Transcript, process, store, and submit result.
    """
    while True:
        transcript: Optional[Transcript] = await work_q.get()
        if transcript is None:
            work_q.task_done()
            break

        tid = transcript.transcript_id
        try:
            # Store raw transcript
            await save_raw_transcript(transcript.dict())

            # Processing pipeline
            summary = await summarize_transcript(transcript)
            structured = extract_structured_data(transcript)
            analysis = await analyze_transcript(transcript)

            # Prepare processed result dict
            result = {
                "transcript_id": tid,
                "summary": summary,
                "structured_data": structured.dict(),
                "analysis": analysis.dict(),
                "processing_timestamp": datetime.now(timezone.utc).isoformat()
            }

            # Store processed result
            await save_processed_result(result)

            # Submit to external API
            await client.submit_processed(result)
            logger.info(f"Worker {name} processed and submitted {tid}")

        except Exception as e:
            logger.exception(f"Error in worker {name} processing {tid}, sending to DLQ")
            await dlq.put(transcript)
        finally:
            work_q.task_done()

async def main() -> None:
    # Initialize DB
    await init_db()

    # Initialize client and authenticate
    client = APIClient(API_KEY, BASE_URL)
    await client.authenticate()

    # Queues for work and dead letters
    work_queue = AsyncQueue(maxsize=QUEUE_MAXSIZE)
    dlq = AsyncQueue()

    # Start transcript stream producer
    async def producer() -> None:
        async for transcript in client.stream_transcripts():
            await work_queue.put(transcript)
            logger.debug(f"Enqueued {transcript.transcript_id}")

    producer_task = asyncio.create_task(producer())

    # Start worker pool
    workers = [asyncio.create_task(worker(i, client, work_queue, dlq)) for i in range(CONCURRENCY)]

    # Graceful shutdown handling
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    logger.info("Shutdown signal received, terminating workers...")

    # Signal workers to stop
    for _ in workers:
        await work_queue.put(None)

    await asyncio.gather(*workers)
    producer_task.cancel()

    # Handle DLQ items
    if not dlq.empty():
        count = 0
        while not dlq.empty():
            await dlq.get()
            count += 1
        logger.warning(f"{count} transcripts in DLQ")

if __name__ == "__main__":
    asyncio.run(main())
s