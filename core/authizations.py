from typing import Annotated

from fastapi import Depends, HTTPException, status, Cookie
from sqlmodel import Session, select

from core.databases import get_db
from core.tokenizers import decode_access_token
from models.users import User


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> User:
    """
    현재 인증된 사용자의 정보를 조회하는 의존성 함수입니다.

    쿠키에서 JWT 액세스 토큰을 추출하고 검증한 후, 토큰에 포함된 사용자 UUID를 사용하여
    데이터베이스에서 해당 사용자의 정보를 조회합니다.

    토큰이 유효하지 않거나, 만료되었거나, 사용자를 찾을 수 없는 경우 401 Unauthorized 예외를 발생시킵니다.

    Args:
        access_token: 쿠키에서 추출한 JWT 액세스 토큰
        db: SQLAlchemy 데이터베이스 세션

    Returns:
        User: 인증된 사용자 객체

    Raises:
        HTTPException: 인증에 실패하거나 사용자를 찾을 수 없는 경우
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="인증되지 않은 요청입니다."
        )

    try:
        payload = decode_access_token(access_token)
        google_id = payload.get("sub")

        if not google_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 정보입니다.",
            )

        user = db.exec(select(User).where(User.google_id == google_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
            )

        return user

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 처리 중 오류가 발생했습니다.",
        )
