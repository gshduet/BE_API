from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.databases import get_db
from core.authizations import get_current_user
from models.posts import Notice, GuestBook
from models.users import User
from request_schemas.posts import NoticeCreate, GuestBookCreate
from response_schemas.posts import NoticeResponse, GuestBookResponse

post_router = APIRouter(prefix="/posts")


@post_router.post("/notices", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_notice(
    request: NoticeCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    새로운 게시글을 작성하는 엔드포인트입니다.

    로그인된 사용자만 접근할 수 있으며, 게시글 작성에 필요한 제목과 내용을 전달받아 새로운 게시글을 생성합니다.
    작성자 정보는 현재 로그인된 사용자의 정보를 자동으로 설정합니다.

    Args:
        request (NoticeCreate): 게시글 생성에 필요한 제목과 내용이 담긴 요청 객체
        current_user (User): 현재 로그인된 사용자 정보
        db (Session): 데이터베이스 세션

    Returns:
        dict: 게시글 작성 성공 메시지

    Raises:
        HTTPException: 게시글 작성 중 데이터베이스 오류가 발생한 경우
    """
    try:
        # 새 게시글 생성
        new_post = Notice(
            title=request.title,
            content=request.content,
            author_name=current_user.name,
            author_google_id=current_user.google_id,
        )

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return {"message": "게시글 작성 성공"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 작성 중 오류가 발생했습니다.",
        )


@post_router.get("/notices", response_model=List[NoticeResponse])
async def get_notice_list(
    db: Session = Depends(get_db),
):
    """
    전체 게시글 목록을 조회하는 엔드포인트입니다.

    삭제되지 않은 모든 게시글을 조회하여 반환합니다. 게시글은 작성일시 순으로 정렬되어 반환됩니다.
    각 게시글에는 제목, 내용, 작성자 정보, 작성일시 등의 정보가 포함됩니다.

    Args:
        db (Session): 데이터베이스 세션

    Returns:
        List[NoticeResponse]: 게시글 목록. 각 게시글은 NoticeResponse 모델 형식으로 반환됩니다.
    """
    notices = db.exec(
        select(Notice)
        .where(Notice.is_deleted == False)
        .order_by(Notice.created_at.desc())
    ).all()

    return notices


@post_router.get("/notices/{notice_id}", response_model=NoticeResponse)
async def get_notice(
    notice_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 게시글의 상세 정보를 조회하는 엔드포인트입니다.

    URL 경로에서 전달받은 게시글 ID를 기반으로 해당 게시글의 정보를 조회합니다.
    삭제되지 않은 게시글만 조회 가능하며, 존재하지 않는 게시글 ID가 전달된 경우 404 에러를 반환합니다.
    조회된 게시글은 NoticeResponse 모델 형식으로 변환되어 반환됩니다.

    Args:
        notice_id (int): 조회할 게시글의 ID
        db (Session): 데이터베이스 세션

    Returns:
        NoticeResponse: 조회된 게시글 정보

    Raises:
        HTTPException: 게시글을 찾을 수 없는 경우 404 에러 발생
    """
    notice = db.exec(
        select(Notice).where(Notice.id == notice_id, Notice.is_deleted == False)
    ).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return notice


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
    """
    새로운 방명록을 작성하는 엔드포인트입니다.

    로그인된 사용자만 접근할 수 있으며, 방명록 내용과 대상 사용자의 google_id를 전달받아 새로운 방명록을 생성합니다.
    작성자 정보는 현재 로그인된 사용자의 정보를 자동으로 설정하며, 비밀 방명록 여부를 선택할 수 있습니다.

    Args:
        host_google_id (str): 방명록을 작성할 대상 사용자의 google_id
        request (GuestBookCreate): 방명록 생성에 필요한 내용과 대상 사용자 정보가 담긴 요청 객체
        current_user (User): 현재 로그인된 사용자 정보
        db (Session): 데이터베이스 세션

    Returns:
        dict: 방명록 작성 성공 메시지

    Raises:
        HTTPException: 방명록 작성 중 데이터베이스 오류가 발생한 경우
    """
    try:
        new_guestbook = GuestBook(
            content=request.content,
            author_name=current_user.name,
            guest_google_id=current_user.google_id,
            host_google_id=host_google_id,
            is_secret=request.is_secret,
        )

        db.add(new_guestbook)
        db.commit()
        db.refresh(new_guestbook)

        return {"message": "방명록 작성 성공"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="방명록 작성 중 오류가 발생했습니다.",
        )


@post_router.get("/guestbooks/{host_google_id}", response_model=List[GuestBookResponse])
async def get_guestbook_list(
    host_google_id: str,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 방명록 목록을 조회하는 엔드포인트입니다.

    URL 경로에서 전달받은 host_google_id를 기반으로 해당 사용자에게 작성된 모든 방명록을 조회합니다.
    삭제되지 않은 방명록만 조회되며, 작성일시 순으로 정렬되어 반환됩니다.
    각 방명록에는 내용, 작성자 이름, 작성일시 등의 정보가 포함됩니다.

    Args:
        host_google_id (str): 방명록을 조회할 대상 사용자의 google_id
        db (Session): 데이터베이스 세션

    Returns:
        List[GuestBookResponse]: 방명록 목록. 각 방명록은 GuestBookResponse 모델 형식으로 반환됩니다.
    """
    guestbooks = db.exec(
        select(GuestBook)
        .where(
            GuestBook.host_google_id == host_google_id,
            GuestBook.is_deleted == False,
        )
        .order_by(GuestBook.created_at.desc())
    ).all()
    return guestbooks


@post_router.get(
    "/guestbooks/{host_google_id}/{guestbook_id}", response_model=GuestBookResponse
)
async def get_guestbook(
    host_google_id: str,
    guestbook_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 방명록의 상세 정보를 조회하는 엔드포인트입니다.

    URL 경로에서 전달받은 방명록 ID를 기반으로 해당 방명록의 정보를 조회합니다.
    삭제되지 않은 방명록만 조회 가능하며, 존재하지 않는 방명록 ID가 전달된 경우 404 에러를 반환합니다.
    조회된 방명록은 GuestBookResponse 모델 형식으로 변환되어 반환됩니다.

    Args:
        host_google_id (str): 방명록을 조회할 대상 사용자의 google_id
        guestbook_id (int): 조회할 방명록의 ID
        db (Session): 데이터베이스 세션

    Returns:
        GuestBookResponse: 조회된 방명록 정보

    Raises:
        HTTPException: 방명록을 찾을 수 없는 경우 404 에러 발생
    """
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

    return guestbook
