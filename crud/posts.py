from sqlmodel import Session, select
from fastapi import HTTPException, status

from models.posts import Notice, GuestBook
from request_schemas.posts import NoticeCreate, GuestBookCreate


def create_notice(
    db: Session, request: NoticeCreate, author_name: str, author_google_id: str
) -> None:
    try:
        new_post = Notice(
            title=request.title,
            content=request.content,
            author_name=author_name,
            author_google_id=author_google_id,
        )

        db.add(new_post)
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 작성 중 오류가 발생했습니다.",
        )


def get_notice_list(db: Session):
    return db.exec(
        select(Notice)
        .where(Notice.is_deleted == False)
        .order_by(Notice.created_at.desc())
    ).all()


def get_notice(db: Session, notice_id: int):
    notice = db.exec(
        select(Notice).where(Notice.id == notice_id, Notice.is_deleted == False)
    ).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return notice


def create_guestbook(
    db: Session,
    request: GuestBookCreate,
    author_name: str,
    guest_google_id: str,
    host_google_id: str,
) -> None:
    try:
        new_guestbook = GuestBook(
            content=request.content,
            author_name=author_name,
            guest_google_id=guest_google_id,
            host_google_id=host_google_id,
            is_secret=request.is_secret,
        )

        db.add(new_guestbook)
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="방명록 작성 중 오류가 발생했습니다.",
        )


def get_guestbook_list(db: Session, host_google_id: str):
    return db.exec(
        select(GuestBook)
        .where(
            GuestBook.host_google_id == host_google_id,
            GuestBook.is_deleted == False,
        )
        .order_by(GuestBook.created_at.desc())
    ).all()


def delete_guestbook(
    db: Session, host_google_id: str, guestbook_id: int, current_user_google_id: str
) -> None:
    guestbook = db.exec(
        select(GuestBook).where(
            GuestBook.id == guestbook_id,
            GuestBook.host_google_id == host_google_id,
            GuestBook.is_deleted == False,
        )
    ).first()

    if not guestbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="방명록을 찾을 수 없습니다.",
        )

    if (
        current_user_google_id != guestbook.guest_google_id
        and current_user_google_id != host_google_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="방명록을 삭제할 권한이 없습니다.",
        )

    try:
        guestbook.soft_delete()
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="방명록 삭제 중 오류가 발생했습니다.",
        )
