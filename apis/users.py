from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Response, Request, status, Cookie
from sqlmodel import Session, select

from models.users import User, UserProfile
from core.databases import get_db
from core.tokenizers import create_access_token, decode_access_token
from request_schemas.users import GoogleSignupRequest, UserProfileUpdateRequest
from response_schemas.users import UserProfileResponse, UserListResponse
from core.authizations import get_current_user


user_router = APIRouter(prefix="/users")


@user_router.post("/login", response_model=dict)
async def google_login(
    request: GoogleSignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Google OAuth를 통한 로그인/회원가입을 처리하는 엔드포인트입니다.
    이미 로그인된 사용자의 경우 쿠키의 access_token을 확인하여 즉시 로그인 성공을 반환합니다.
    신규 사용자의 경우 회원가입 절차를 진행하고, 기존 사용자의 경우 로그인 시간을 업데이트합니다.
    """
    try:
        user = db.exec(select(User).where(User.email == request.email)).first()

        if not user:
            user = User(
                email=request.email,
                name=request.name,
                google_id=request.google_id,
                google_image_url=request.google_image_url,
                generation=7,
                role_level=0,
            )
            profile = UserProfile(
                google_id=request.google_id,
                bio=None,
                resume_url=None,
                portfolio_url=[],
                tech_stack=[],
            )
            db.add(user)
            db.add(profile)

        user.last_login_at = datetime.now()
        db.commit()
        db.refresh(user)

        token_body = {
            "email": user.email,
            "name": user.name,
            "google_id": user.google_id,
            "google_image_url": user.google_image_url,
            "generation": user.generation,
        }

        access_token = create_access_token(data=token_body)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            domain="jgtower.com",
            path="/",
            max_age=30 * 24 * 60 * 60,
        )

        return {"message": "로그인 성공"}

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다.",
        )


@user_router.get("/all", response_model=list[UserListResponse])
async def get_all_users(
    db: Session = Depends(get_db),
):
    users = db.exec(select(User)).all()
    return users


@user_router.get("/profile/{google_id}", response_model=UserProfileResponse)
async def get_user_profile(
    google_id: str,
    db: Session = Depends(get_db),
):
    profile = db.exec(
        select(UserProfile).where(UserProfile.google_id == google_id)
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 사용자의 프로필을 찾을 수 없습니다.",
        )

    return profile


@user_router.patch("/profile/{google_id}", response_model=UserProfileResponse)
async def update_user_profile(
    google_id: str,
    profile_update: UserProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    if current_user.google_id != google_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 프로필을 수정할 권한이 없습니다.",
        )

    db_profile = db.exec(
        select(UserProfile).where(UserProfile.google_id == google_id)
    ).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")

    update_data = profile_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_profile, field, value)

    try:
        db.commit()
        db.refresh(db_profile)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="프로필 업데이트 중 오류가 발생했습니다.",
        )

    return db_profile
