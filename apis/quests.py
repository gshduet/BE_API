from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from core.databases import get_db
from core.authizations import get_current_user
from models.users import User
from request_schemas.quests import QuestResultCreateRequest
from response_schemas.quests import QuestResponse, QuestResultResponse
from crud import quests as quests_crud

quest_router = APIRouter(prefix="/quests")


@quest_router.get("/{quest_number}", response_model=QuestResponse)
async def get_quest(
    quest_number: int,
    db: Session = Depends(get_db),
):
    return quests_crud.get_quest(db=db, quest_number=quest_number)


@quest_router.post(
    "/results/{quest_number}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_quest_result(
    quest_number: int,
    request: QuestResultCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    quests_crud.create_quest_result(
        db=db,
        quest_number=quest_number,
        request=request,
        user_email=current_user.email,
        user_name=current_user.name,
    )
    return {"message": "문제 해결 정보 생성 성공"}


@quest_router.get("/results/{quest_number}", response_model=List[QuestResultResponse])
async def get_quest_results(
    quest_number: int,
    db: Session = Depends(get_db),
):
    return quests_crud.get_quest_results(db=db, quest_number=quest_number)
