from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import HTTPException, status

from core.config import settings


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + timedelta(days=30)})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다."
        )
