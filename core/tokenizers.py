from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
from fastapi import HTTPException, status

from core.config import settings


def create_access_token(data: dict[str, Any]) -> str:
    """
    JWT 액세스 토큰을 생성합니다.
    PyJWT를 사용하여 토큰을 생성하며, 만료 시간을 포함한 페이로드를 인코딩합니다.
    """
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + timedelta(days=30)})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    JWT 토큰을 디코딩합니다.
    토큰이 유효하지 않거나 만료된 경우 예외를 발생시킵니다.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다."
        )
