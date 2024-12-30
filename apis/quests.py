from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.databases import get_db
from core.authizations import get_current_user
from models.users import User
from models.quests import Quest, QuestResult
from request_schemas.quests import QuestResultCreateRequest
from response_schemas.quests import QuestResponse, QuestResultResponse

quest_router = APIRouter(prefix="/quests")


@quest_router.get("/{quest_number}", response_model=QuestResponse)
async def get_quest(
    quest_number: int,
    db: Session = Depends(get_db),
):
    quest = db.exec(select(Quest).where(Quest.quest_number == quest_number)).first()

    if not quest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문제를 찾을 수 없습니다.",
        )

    return quest


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
    new_result = QuestResult(
        quest_number=quest_number,
        user_email=current_user.email,
        user_name=current_user.name,
        time_taken=request.time_taken,
    )

    try:
        db.add(new_result)
        db.commit()
        db.refresh(new_result)

        return {"message": "문제 해결 정보 생성 성공"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="문제 해결 정보 생성 중 오류가 발생했습니다.",
        )


@quest_router.get("/results/{quest_number}", response_model=List[QuestResultResponse])
async def get_quest_results(
    quest_number: int,
    db: Session = Depends(get_db),
):
    results = db.exec(
        select(QuestResult)
        .where(QuestResult.quest_number == quest_number)
        .order_by(QuestResult.time_taken.asc())
    ).all()
    return results
