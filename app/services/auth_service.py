from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.repositories import user_repository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logging import logger
from app.core.redis import redis_client


LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_TTL_SECONDS = 15 * 60


def _login_failure_key(username: str) -> str:
    return f"auth:login:failed:{username.lower()}"


def _is_login_limited(username: str) -> bool:
    try:
        attempts = redis_client.get(_login_failure_key(username))
    except RedisError:
        logger.warning("LOGIN_RATE_LIMIT_UNAVAILABLE username=<redacted>")
        return False
    return int(attempts or 0) >= LOGIN_FAILURE_LIMIT


def _record_login_failure(username: str) -> None:
    try:
        key = _login_failure_key(username)
        attempts = redis_client.incr(key)
        if attempts == 1:
            redis_client.expire(key, LOGIN_FAILURE_TTL_SECONDS)
    except RedisError:
        logger.warning("LOGIN_RATE_LIMIT_UNAVAILABLE username=<redacted>")


def _clear_login_failures(username: str) -> None:
    try:
        redis_client.delete(_login_failure_key(username))
    except RedisError:
        logger.warning("LOGIN_RATE_LIMIT_UNAVAILABLE username=<redacted>")


def register(db: Session, data: RegisterRequest) -> User:
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if user_repository.get_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_repository.create(
        db,
        username=data.username,
        email=data.email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
    )
    logger.info("REGISTER user_id=%d", user.id)
    return user


def login(db: Session, data: LoginRequest) -> TokenResponse:
    if _is_login_limited(data.username):
        logger.warning("LOGIN_BLOCKED username=<redacted>")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts",
        )

    user = user_repository.get_by_username(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        _record_login_failure(data.username)
        logger.warning("LOGIN_FAILED username=<redacted>")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        logger.warning("LOGIN_BLOCKED user_id=%d", user.id)
        raise HTTPException(status_code=403, detail="Account is disabled")

    _clear_login_failures(data.username)
    token = create_access_token(subject=str(user.id), role=user.role.value)
    logger.info("LOGIN_SUCCESS user_id=%d", user.id)
    return TokenResponse(access_token=token)
