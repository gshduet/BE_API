from sqlmodel import Session, select
from fastapi import HTTPException, status

from models.quests import Quest, QuestResult
from request_schemas.quests import QuestResultCreateRequest


def get_quest(db: Session, quest_number: int) -> Quest:
    quest = db.exec(select(Quest).where(Quest.quest_number == quest_number)).first()

    if not quest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문제를 찾을 수 없습니다.",
        )

    return quest


def create_quest_result(
    db: Session,
    quest_number: int,
    request: QuestResultCreateRequest,
    user_email: str,
    user_name: str,
) -> None:
    try:
        new_result = QuestResult(
            quest_number=quest_number,
            user_email=user_email,
            user_name=user_name,
            time_taken=request.time_taken,
        )

        db.add(new_result)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="문제 해결 정보 생성 중 오류가 발생했습니다.",
        )


def get_quest_results(db: Session, quest_number: int) -> list[QuestResult]:
    from datetime import datetime, time

    today = datetime.now().date()
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)

    return db.exec(
        select(QuestResult)
        .where(
            QuestResult.quest_number == quest_number,
            QuestResult.created_at >= today_start,
            QuestResult.created_at <= today_end,
        )
        .order_by(QuestResult.time_taken.asc())
    ).all()
