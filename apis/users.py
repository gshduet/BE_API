from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlmodel import Session

from core.databases import get_db
from core.tokenizers import create_access_token
from core.authizations import get_current_user
from models.users import User
from crud.users import (
    get_user_by_email,
    create_new_user,
    update_last_login,
    get_all_users,
    get_user_profile as get_profile,
    update_user_profile,
)
from request_schemas.users import GoogleSignupRequest, UserProfileUpdateRequest
from response_schemas.users import UserProfileResponse, UserListResponse


user_router = APIRouter(prefix="/users")


@user_router.post("/login", response_model=dict)
async def google_login(
    request: GoogleSignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user = get_user_by_email(db, request.email)

        if not user:
            user = create_new_user(db, request)

        update_last_login(db, user)

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

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다.",
        )


@user_router.get("/all", response_model=list[UserListResponse])
async def get_users_list(
    db: Session = Depends(get_db),
):
    return get_all_users(db)


@user_router.get("", response_model=list[UserListResponse])
async def get_users_list_v2(
    db: Session = Depends(get_db),
):
    return get_all_users(db)


@user_router.get("/profile/{google_id}", response_model=UserProfileResponse)
async def get_user_profile(
    google_id: str,
    db: Session = Depends(get_db),
):
    return get_profile(db, google_id)


@user_router.patch("/profile/{google_id}", response_model=UserProfileResponse)
async def update_user_profile_endpoint(
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

    try:
        updated_profile = update_user_profile(db, google_id, profile_update)
        return updated_profile

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 업데이트 중 오류가 발생했습니다.",
        )
