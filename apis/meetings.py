from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from redis.asyncio import Redis

from crud.meetings import (
    add_to_meeting_room,
    remove_from_meeting_room,
    get_all_meeting_rooms,
    get_meeting_room_clients,
    delete_meeting_room,
)
from request_schemas.meetings import MeetingRoomCreate, RoomJoin, RoomLeave
from core.databases import get_redis

meetings_router = APIRouter(prefix="/meetingroom")


@meetings_router.post(
    "/create", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def create_meeting_room(
    request: MeetingRoomCreate, redis: Redis = Depends(get_redis)
):
    """
    새로운 미팅룸을 Redis에 생성하는 엔드포인트입니다.

    URL: /meetingroom/create

    Args:
        request (MeetingRoomCreate): 미팅룸 생성 요청 정보
        redis (Redis): Redis 클라이언트 인스턴스

    Returns:
        dict: 성공 메시지
    """
    try:
        await add_to_meeting_room(
            redis, request.room_id, request.title, request.client_id
        )
        return {"message": "미팅룸 생성 성공"}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis에서 미팅룸 생성 중 오류가 발생했습니다.",
        )


@meetings_router.get("/list", response_model=List[dict])
async def get_meeting_rooms(redis: Redis = Depends(get_redis)):
    """
    Redis에서 모든 미팅룸의 정보를 조회하는 엔드포인트입니다.

    URL: /meetingroom/list

    Args:
        redis (Redis): Redis 클라이언트 인스턴스

    Returns:
        List[dict]: 미팅룸 목록
    """
    try:
        return await get_all_meeting_rooms(redis)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis에서 미팅룸 조회 중 오류가 발생했습니다.",
        )


@meetings_router.post("/join", response_model=dict, status_code=status.HTTP_201_CREATED)
async def join_meeting_room(request: RoomJoin, redis: Redis = Depends(get_redis)):
    """
    미팅룸 입장을 Redis에서 수행하는 엔드포인트입니다.

    URL: /meetingroom/join

    Args:
        request (RoomJoin): 클라이언트와 미팅룸 ID 정보
        redis (Redis): Redis 클라이언트 인스턴스

    Returns:
        dict: 성공 메시지
    """
    try:
        await add_to_meeting_room(redis, request.room_id, None, request.client_id)
        return {"message": "미팅룸 입장 성공"}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis에서 미팅룸 입장 처리 중 오류가 발생했습니다.",
        )


@meetings_router.post(
    "/leave", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def leave_meeting_room(request: RoomLeave, redis: Redis = Depends(get_redis)):
    """
    미팅룸 퇴장을 Redis에서 수행하며, 모든 인원이 나가면 미팅룸을 삭제합니다.

    URL: /meetingroom/leave

    Args:
        request (RoomLeave): 클라이언트와 미팅룸 ID 정보
        redis (Redis): Redis 클라이언트 인스턴스

    Returns:
        dict: 성공 메시지
    """
    try:
        # 클라이언트를 미팅룸에서 제거
        await remove_from_meeting_room(request.room_id, request.client_id)

        # 남은 클라이언트 확인
        remaining_clients = await get_meeting_room_clients(request.room_id)
        if not remaining_clients:
            # 남은 클라이언트가 없으면 미팅룸 삭제
            await delete_meeting_room(request.room_id)
            return {"message": "미팅룸 퇴장 성공 및 미팅룸 삭제"}

        return {"message": "미팅룸 퇴장 성공"}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis에서 미팅룸 퇴장 처리 중 오류가 발생했습니다.",
        )
