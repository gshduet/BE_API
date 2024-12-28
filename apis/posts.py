from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.databases import get_db
from core.authizations import get_current_user
from models.posts import Notice, GuestBook
from models.users import User
from request_schemas.posts import NoticeCreate
from response_schemas.posts import NoticeResponse

post_router = APIRouter(prefix="/posts")


@post_router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
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


@post_router.get("/", response_model=List[NoticeResponse])
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
    notices = db.exec(select(Notice).where(Notice.is_deleted == False)).all()

    return notices


@post_router.get("/{post_id}", response_model=NoticeResponse)
async def get_notice(
    post_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 게시글의 상세 정보를 조회하는 엔드포인트입니다.

    URL 경로에서 전달받은 게시글 ID를 기반으로 해당 게시글의 정보를 조회합니다.
    삭제되지 않은 게시글만 조회 가능하며, 존재하지 않는 게시글 ID가 전달된 경우 404 에러를 반환합니다.
    조회된 게시글은 NoticeResponse 모델 형식으로 변환되어 반환됩니다.

    Args:
        post_id (int): 조회할 게시글의 ID
        db (Session): 데이터베이스 세션

    Returns:
        NoticeResponse: 조회된 게시글 정보

    Raises:
        HTTPException: 게시글을 찾을 수 없는 경우 404 에러 발생
    """
    notice = db.exec(
        select(Notice).where(Notice.id == post_id, Notice.is_deleted == False)
    ).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return notice
