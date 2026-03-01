import json
from typing import AsyncGenerator, Any
from fastapi.responses import StreamingResponse


class SSEStream:
    
    @staticmethod
    def format(data: Any, event: str = "message") -> str:
        if not isinstance(data, str):
            data = json.dumps(data) if isinstance(data, dict) else data.model_dump_json()
        return f"event: {event}\ndata: {data}\n\n"

    @staticmethod
    def done(data: Any = "[DONE]") -> str:
        return SSEStream.format(data, event="done")

    @classmethod
    def response(cls, generator: AsyncGenerator, headers: dict = {}) -> StreamingResponse:
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                **headers
            }
        )