from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from core.databases import get_redis


async def add_to_room(
    redis: Redis = Depends(get_redis), room_id: str = None, client_id: str = None
) -> None:
    """방에 클라이언트를 추가하는 함수입니다."""
    await redis.hset(settings.rooms_key_template.format(room_id=room_id), client_id, "")


async def remove_from_room(
    redis: Redis = Depends(get_redis), room_id: str = None, client_id: str = None
) -> None:
    """방에서 클라이언트를 제거하는 함수입니다."""
    await redis.hdel(settings.rooms_key_template.format(room_id=room_id), client_id)


async def get_room_clients(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> list[str]:
    """방에 있는 모든 클라이언트 목록을 반환하는 함수입니다."""
    return list(await redis.hkeys(settings.rooms_key_template.format(room_id=room_id)))


async def add_to_meeting_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
    title: str | None = None,
    client_id: str = None,
) -> None:
    """미팅룸에 클라이언트를 추가하고 제목을 설정하는 함수입니다."""
    if title:
        await redis.hset(
            settings.meeting_room_key_template.format(room_id=room_id), "title", title
        )
    await redis.hset(
        settings.meeting_room_key_template.format(room_id=room_id), client_id, ""
    )


async def remove_from_meeting_room(
    redis: Redis = Depends(get_redis), room_id: str = None, client_id: str = None
) -> None:
    """미팅룸에서 클라이언트를 제거하는 함수입니다."""
    await redis.hdel(
        settings.meeting_room_key_template.format(room_id=room_id), client_id
    )


async def get_meeting_room_clients(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> list[str]:
    """미팅룸의 모든 클라이언트 목록을 반환하는 함수입니다."""
    data = await redis.hgetall(
        settings.meeting_room_key_template.format(room_id=room_id)
    )
    return [key for key in data.keys() if key != "title"]


async def get_meeting_room_title(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> str | None:
    """미팅룸의 제목을 반환하는 함수입니다."""
    return await redis.hget(
        settings.meeting_room_key_template.format(room_id=room_id), "title"
    )


async def delete_meeting_room(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> None:
    """미팅룸을 삭제하는 함수입니다."""
    await redis.delete(settings.meeting_room_key_template.format(room_id=room_id))


async def get_all_meeting_rooms(redis: Redis = Depends(get_redis)) -> list[dict]:
    """모든 미팅룸의 정보를 반환하는 함수입니다."""
    room_keys = await redis.keys("meeting_room:*")
    rooms = []
    for room_key in room_keys:
        room_id = room_key.split(":")[-1]
        clients = await get_meeting_room_clients(redis, room_id)
        title = await get_meeting_room_title(redis, room_id)
        rooms.append({"room_id": room_id, "title": title, "clients": clients})
    return rooms


async def set_client_info(
    redis: Redis = Depends(get_redis), client_id: str = None, info: dict = None
) -> None:
    """클라이언트 정보를 설정하는 함수입니다."""
    await redis.hset(
        settings.client_key_template.format(client_id=client_id), mapping=info
    )


async def get_client_info(
    redis: Redis = Depends(get_redis), client_id: str = None
) -> dict:
    """클라이언트 정보를 반환하는 함수입니다."""
    return await redis.hgetall(settings.client_key_template.format(client_id=client_id))


async def delete_client_info(
    redis: Redis = Depends(get_redis), client_id: str = None
) -> None:
    """클라이언트 정보를 삭제하는 함수입니다."""
    await redis.delete(settings.client_key_template.format(client_id=client_id))
