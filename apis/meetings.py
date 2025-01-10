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
    try:
        await remove_from_meeting_room(redis, request.room_id, request.client_id)

        remaining_clients = await get_meeting_room_clients(redis, request.room_id)

        if not remaining_clients:
            await delete_meeting_room(redis, request.room_id)

            return {"message": "미팅룸 퇴장 성공 및 미팅룸 삭제"}

        return {"message": "미팅룸 퇴장 성공"}

    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis에서 미팅룸 퇴장 처리 중 오류가 발생했습니다.",
        )
