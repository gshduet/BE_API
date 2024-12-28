from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlmodel import Session, select

from models.users import User
from core.databases import get_db
from core.tokenizers import create_access_token
from request_schemas.users import GoogleSignupRequest


user_router = APIRouter(prefix="/users")


@user_router.post("/login/google", response_model=dict)
async def google_login(
    request: GoogleSignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Google OAuth를 통한 로그인/회원가입을 처리하는 엔드포인트입니다.

    클라이언트로부터 전달받은 Google 계정 정보를 바탕으로 신규 회원가입 또는 로그인을 수행합니다.
    기존 회원인 경우 마지막 로그인 시간을 업데이트하고, 신규 회원인 경우 회원 정보를 저장합니다.
    인증에 성공하면 JWT 액세스 토큰을 생성하여 쿠키에 저장합니다.

    Args:
        request (GoogleSignupRequest): Google 계정 정보가 담긴 요청 객체
        response (Response): FastAPI Response 객체
        db (Session): 데이터베이스 세션

    Returns:
        dict: 로그인 성공 메시지

    Raises:
        HTTPException: 회원가입 처리 중 오류가 발생한 경우
    """
    user = db.exec(select(User).where(User.google_id == request.google_id)).first()

    if not user:
        user = User(
            email=request.email,
            name=request.name,
            google_id=request.google_id,
            last_login_at=datetime.now(),
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="회원가입 처리 중 오류가 발생했습니다."
            )
    else:
        user.last_login_at = datetime.now()
        db.commit()

    access_token = create_access_token(data={"sub": user.google_id})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # secure=True,
        samesite="lax",
    )

    return {"message": "로그인 성공"}
