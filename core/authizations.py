from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select

from core.databases import get_db
from core.tokenizers import decode_access_token
from models.users import User


async def get_current_user(
    request_obj: Request,
    db: Session = Depends(get_db),
) -> User:
    try:
        access_token = request_obj.cookies.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증되지 않은 요청입니다.",
            )

        payload = decode_access_token(access_token)
        google_id = payload.get("google_id")

        if not google_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="유효하지 않은 인증 정보입니다.",
            )

        user = db.exec(select(User).where(User.google_id == google_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="유효하지 않은 인증 정보입니다.",
            )

        return user

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 처리 중 오류가 발생했습니다.",
        )
