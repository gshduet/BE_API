from pydantic import BaseModel


class MeetingRoomCreate(BaseModel):
    room_id: str
    title: str
    client_id: str


class RoomJoin(BaseModel):
    room_id: str
    client_id: str


class RoomLeave(BaseModel):
    room_id: str
    client_id: str
