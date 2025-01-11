from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from core.databases import get_redis


async def add_to_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
    client_id: str = None,
) -> None:
    """일반 채팅방에 클라이언트를 추가합니다.

    Redis hash 자료구조를 사용하여 특정 room_id에 client_id를 추가합니다.
    이미 존재하는 클라이언트의 경우 값이 덮어씌워집니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 채팅방 ID
        client_id (str): 추가할 클라이언트 ID

    Returns:
        None

    Example:
        >>> await add_to_room(redis, "room_123", "client_456")
    """
    await redis.hset(settings.rooms_key_template.format(room_id=room_id), client_id, "")


async def remove_from_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
    client_id: str = None,
) -> None:
    """일반 채팅방에서 클라이언트를 제거합니다.

    지정된 room_id의 hash에서 client_id를 삭제합니다.
    존재하지 않는 client_id에 대해서는 아무 동작도 하지 않습니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 채팅방 ID
        client_id (str): 제거할 클라이언트 ID

    Returns:
        None

    Example:
        >>> await remove_from_room(redis, "room_123", "client_456")
    """
    await redis.hdel(settings.rooms_key_template.format(room_id=room_id), client_id)


async def get_room_clients(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
) -> list[str]:
    """일반 채팅방의 모든 클라이언트 목록을 조회합니다.

    지정된 room_id에 있는 모든 client_id들을 리스트로 반환합니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 채팅방 ID

    Returns:
        list[str]: 채팅방에 있는 모든 클라이언트 ID 리스트

    Example:
        >>> clients = await get_room_clients(redis, "room_123")
        >>> print(clients)
        ['client_1', 'client_2', 'client_3']
    """
    return list(await redis.hkeys(settings.rooms_key_template.format(room_id=room_id)))


async def add_to_meeting_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
    title: str | None = None,
    client_id: str = None,
) -> None:
    """미팅룸에 클라이언트를 추가하고, 필요한 경우 미팅룸 제목을 설정합니다.

    Redis hash 자료구조를 사용하여 미팅룸 정보를 관리합니다.
    title이 제공된 경우 미팅룸의 제목도 함께 설정됩니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 미팅룸 ID
        title (str, optional): 미팅룸 제목. 없으면 기존 제목 유지
        client_id (str): 추가할 클라이언트 ID

    Returns:
        None

    Example:
        >>> await add_to_meeting_room(redis, "meeting_123", "프로젝트 회의", "client_456")
    """
    if title:
        await redis.hset(
            settings.meeting_room_key_template.format(room_id=room_id), "title", title
        )
    await redis.hset(
        settings.meeting_room_key_template.format(room_id=room_id), client_id, ""
    )


async def remove_from_meeting_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
    client_id: str = None,
) -> None:
    """미팅룸에서 클라이언트를 제거합니다.

    지정된 미팅룸의 hash에서 client_id를 삭제합니다.
    존재하지 않는 client_id에 대해서는 아무 동작도 하지 않습니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 미팅룸 ID
        client_id (str): 제거할 클라이언트 ID

    Returns:
        None

    Example:
        >>> await remove_from_meeting_room(redis, "meeting_123", "client_456")
    """
    await redis.hdel(
        settings.meeting_room_key_template.format(room_id=room_id), client_id
    )


async def get_meeting_room_clients(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
) -> list[str]:
    """미팅룸의 모든 클라이언트 목록을 조회합니다.

    지정된 미팅룸의 모든 client_id들을 리스트로 반환합니다.
    'title' 필드는 제외하고 클라이언트 ID만 반환합니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 미팅룸 ID

    Returns:
        list[str]: 미팅룸에 있는 모든 클라이언트 ID 리스트

    Example:
        >>> clients = await get_meeting_room_clients(redis, "meeting_123")
        >>> print(clients)
        ['client_1', 'client_2', 'client_3']
    """
    data = await redis.hgetall(
        settings.meeting_room_key_template.format(room_id=room_id)
    )
    return [key for key in data.keys() if key != "title"]


async def get_meeting_room_title(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
) -> str | None:
    """미팅룸의 제목을 조회합니다.

    지정된 미팅룸의 title 필드 값을 반환합니다.
    title이 설정되지 않은 경우 None을 반환합니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 대상 미팅룸 ID

    Returns:
        str | None: 미팅룸 제목 또는 None

    Example:
        >>> title = await get_meeting_room_title(redis, "meeting_123")
        >>> print(title)
        '프로젝트 회의'
    """
    return await redis.hget(
        settings.meeting_room_key_template.format(room_id=room_id), "title"
    )


async def delete_meeting_room(
    redis: Redis = Depends(get_redis),
    room_id: str = None,
) -> None:
    """미팅룸을 완전히 삭제합니다.

    지정된 미팅룸의 모든 정보(제목, 클라이언트 목록 등)를 삭제합니다.
    존재하지 않는 미팅룸에 대해서는 아무 동작도 하지 않습니다.

    Args:
        redis (Redis): Redis 연결 객체
        room_id (str): 삭제할 미팅룸 ID

    Returns:
        None

    Example:
        >>> await delete_meeting_room(redis, "meeting_123")
    """
    await redis.delete(settings.meeting_room_key_template.format(room_id=room_id))


async def get_all_meeting_rooms(redis: Redis = Depends(get_redis)) -> list[dict]:
    """모든 활성 미팅룸의 정보를 조회합니다.

    현재 존재하는 모든 미팅룸의 정보를 리스트로 반환합니다.
    각 미팅룸 정보는 room_id, title, clients를 포함합니다.

    Args:
        redis (Redis): Redis 연결 객체

    Returns:
        list[dict]: 미팅룸 정보 리스트. 각 딕셔너리는 다음 키를 포함:
            - room_id (str): 미팅룸 ID
            - title (str | None): 미팅룸 제목
            - clients (list[str]): 참가자 ID 리스트

    Example:
        >>> rooms = await get_all_meeting_rooms(redis)
        >>> print(rooms)
        [
            {
                'room_id': 'meeting_123',
                'title': '프로젝트 회의',
                'clients': ['client_1', 'client_2']
            },
            ...
        ]
    """
    room_keys = await redis.keys("meeting_room:*")
    rooms = []
    for room_key in room_keys:
        room_id = room_key.split(":")[-1]
        clients = await get_meeting_room_clients(redis, room_id)
        title = await get_meeting_room_title(redis, room_id)
        rooms.append({"room_id": room_id, "title": title, "clients": clients})
    return rooms


async def set_client_info(
    redis: Redis = Depends(get_redis),
    client_id: str = None,
    info: dict = None,
) -> None:
    """클라이언트의 상세 정보를 설정합니다.

    Redis hash에 클라이언트의 정보를 저장합니다.
    기존에 정보가 있다면 새로운 정보로 덮어씌워집니다.

    Args:
        redis (Redis): Redis 연결 객체
        client_id (str): 대상 클라이언트 ID
        info (dict): 저장할 클라이언트 정보

    Returns:
        None

    Example:
        >>> await set_client_info(redis, "client_123", {"name": "홍길동", "status": "online"})
    """
    await redis.hset(
        settings.client_key_template.format(client_id=client_id), mapping=info
    )


async def get_client_info(
    redis: Redis = Depends(get_redis),
    client_id: str = None,
) -> dict:
    """클라이언트의 모든 저장된 정보를 조회합니다.

    Args:
        redis (Redis): Redis 연결 객체
        client_id (str): 대상 클라이언트 ID

    Returns:
        dict: 클라이언트 정보를 담은 딕셔너리

    Example:
        >>> info = await get_client_info(redis, "client_123")
        >>> print(info)
        {'name': '홍길동', 'status': 'online'}
    """
    return await redis.hgetall(settings.client_key_template.format(client_id=client_id))


async def delete_client_info(
    redis: Redis = Depends(get_redis),
    client_id: str = None,
) -> None:
    """클라이언트의 모든 저장된 정보를 삭제합니다.

    Args:
        redis (Redis): Redis 연결 객체
        client_id (str): 삭제할 클라이언트 ID

    Returns:
        None

    Example:
        >>> await delete_client_info(redis, "client_123")
    """
    await redis.delete(settings.client_key_template.format(client_id=client_id))
