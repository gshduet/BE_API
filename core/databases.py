from typing import Generator, AsyncGenerator

from redis.asyncio import Redis
from sqlmodel import Session, create_engine

from core.config import settings


engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
)

redis_client = Redis(
    host=settings.aws_elasticache_endpoint,
    port=settings.aws_elasticache_port,
    decode_responses=True,
    socket_timeout=settings.redis_socket_timeout,
    socket_connect_timeout=settings.redis_socket_connect_timeout,
    retry_on_timeout=settings.redis_retry_on_timeout,
    max_connections=settings.redis_max_connections,
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


async def get_redis() -> AsyncGenerator[Redis, None]:
    try:
        await redis_client.ping()
        yield redis_client
    finally:
        await redis_client.close()
