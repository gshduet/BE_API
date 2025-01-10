from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from core.databases import get_redis


async def add_to_room(
    redis: Redis = Depends(get_redis), room_id: str = None, client_id: str = None
) -> None:
    await redis.hset(settings.rooms_key_template.format(room_id=room_id), client_id, "")


async def remove_from_room(
    redis: Redis = Depends(get_redis), room_id: str = None, client_id: str = None
) -> None:
    await redis.hdel(settings.rooms_key_template.format(room_id=room_id), client_id)


async def get_room_clients(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> list[str]:
    return list(await redis.hkeys(settings.rooms_key_template.format(room_id=room_id)))


async def add_to_meeting_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
    title: str | None = None,
    client_id: str = None,
) -> None:
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
    await redis.hdel(
        settings.meeting_room_key_template.format(room_id=room_id), client_id
    )


async def get_meeting_room_clients(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> list[str]:
    data = await redis.hgetall(
        settings.meeting_room_key_template.format(room_id=room_id)
    )
    return [key for key in data.keys() if key != "title"]


async def get_meeting_room_title(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> str | None:
    return await redis.hget(
        settings.meeting_room_key_template.format(room_id=room_id), "title"
    )


async def delete_meeting_room(
    redis: Redis = Depends(get_redis), room_id: str = None
) -> None:
    await redis.delete(settings.meeting_room_key_template.format(room_id=room_id))


async def get_all_meeting_rooms(redis: Redis = Depends(get_redis)) -> list[dict]:
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
    await redis.hset(
        settings.client_key_template.format(client_id=client_id), mapping=info
    )


async def get_client_info(
    redis: Redis = Depends(get_redis), client_id: str = None
) -> dict:
    return await redis.hgetall(settings.client_key_template.format(client_id=client_id))


async def delete_client_info(
    redis: Redis = Depends(get_redis), client_id: str = None
) -> None:
    await redis.delete(settings.client_key_template.format(client_id=client_id))
