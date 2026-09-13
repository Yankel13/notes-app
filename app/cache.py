import json
import redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
)

CACHE_TTL = 60

def get_cached_note(note_id: int) -> dict | None:
    data = redis_client.get(f"note:{note_id}")
    return json.loads(data) if data else None

def set_cached_note(note_id: int, data: dict) -> None:
    redis_client.setex(f"note:{note_id}", CACHE_TTL, json.dumps(data, default=str))

def invalidate_note(note_id: int) -> None:
    redis_client.delete(f"note:{note_id}")
