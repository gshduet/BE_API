from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from core.databases import get_db
from core.authizations import get_current_user
from models.users import User
from request_schemas.posts import NoticeCreate, GuestBookCreate
from response_schemas.posts import NoticeResponse, GuestBookResponse
from crud import posts as posts_crud

post_router = APIRouter(prefix="/posts")


@post_router.post("/notices", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_notice(
    request: NoticeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    posts_crud.create_notice(
        db=db,
        request=request,
        author_name=current_user.name,
        author_google_id=current_user.google_id,
    )
    return {"message": "게시글 작성 성공"}


@post_router.get("/notices", response_model=List[NoticeResponse])
async def get_notice_list(
    db: Session = Depends(get_db),
):
    return posts_crud.get_notice_list(db=db)


@post_router.get("/notices/{notice_id}", response_model=NoticeResponse)
async def get_notice(
    notice_id: int,
    db: Session = Depends(get_db),
):
    return posts_crud.get_notice(db=db, notice_id=notice_id)


@post_router.post(
    "/guestbooks/{host_google_id}",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_guestbook(
    host_google_id: str,
    request: GuestBookCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    posts_crud.create_guestbook(
        db=db,
        request=request,
        author_name=current_user.name,
        guest_google_id=current_user.google_id,
        host_google_id=host_google_id,
    )
    return {"message": "방명록 작성 성공"}


@post_router.get("/guestbooks/{host_google_id}", response_model=List[GuestBookResponse])
async def get_guestbook_list(
    host_google_id: str,
    db: Session = Depends(get_db),
):
    return posts_crud.get_guestbook_list(db=db, host_google_id=host_google_id)


@post_router.delete(
    "/guestbooks/{host_google_id}/{guestbook_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def delete_guestbook(
    host_google_id: str,
    guestbook_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    posts_crud.delete_guestbook(
        db=db,
        host_google_id=host_google_id,
        guestbook_id=guestbook_id,
        current_user_google_id=current_user.google_id,
    )
    return {"message": "방명록이 삭제되었습니다."}
