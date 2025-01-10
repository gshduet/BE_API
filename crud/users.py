from sqlmodel import Session, select, update
from fastapi import HTTPException, status
from datetime import datetime

from models.users import User, UserProfile
from request_schemas.users import GoogleSignupRequest, UserProfileUpdateRequest


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def create_new_user(db: Session, user_data: GoogleSignupRequest) -> User:
    try:
        user = User(
            email=user_data.email,
            name=user_data.name,
            google_id=user_data.google_id,
            google_image_url=user_data.google_image_url,
            generation=7,
            role_level=0,
        )
        profile = UserProfile(
            google_id=user_data.google_id,
            bio=None,
            resume_url=None,
            portfolio_url=[],
            tech_stack=[],
        )

        db.add(user)
        db.add(profile)
        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 생성 중 오류가 발생했습니다.",
        )


def update_last_login(db: Session, user: User) -> User:
    try:
        user.last_login_at = datetime.now()
        db.commit()
        db.refresh(user)
        return user

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 시간 업데이트 중 오류가 발생했습니다.",
        )


def get_all_users(db: Session) -> list[User]:
    return db.exec(select(User.name, User.google_id, User.generation)).all()


def get_user_profile(db: Session, google_id: str) -> UserProfile:
    profile = db.exec(
        select(UserProfile).where(UserProfile.google_id == google_id)
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 사용자의 프로필을 찾을 수 없습니다.",
        )

    return profile


def update_user_profile(
    db: Session, google_id: str, profile_update: UserProfileUpdateRequest
) -> UserProfile:
    try:
        stmt = (
            update(UserProfile)
            .where(UserProfile.google_id == google_id)
            .values(**profile_update.model_dump(exclude_unset=True))
            .returning(UserProfile)
        )

        result = db.exec(stmt)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 사용자의 프로필을 찾을 수 없습니다.",
            )

        db.commit()

        return result

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 업데이트 중 오류가 발생했습니다.",
        )
