from typing import cast

from redis import Redis
from redis.exceptions import RedisError

from app.config import settings


redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60


def is_limited(username: str) -> bool:
    try:
        attempts = int(cast(str | None, redis_client.get(_key(username))) or 0)
    except (RedisError, ValueError):
        return False
    return attempts >= MAX_FAILURES


def record_failure(username: str) -> None:
    try:
        key = _key(username)
        attempts = redis_client.incr(key)
        if attempts == 1:
            redis_client.expire(key, WINDOW_SECONDS)
    except RedisError:
        return


def clear_failures(username: str) -> None:
    try:
        redis_client.delete(_key(username))
    except RedisError:
        return


def _key(username: str) -> str:
    return f"ai-billing:login-failed:{username.lower()}"
