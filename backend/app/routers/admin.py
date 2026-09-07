from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
import os

from app.database import get_db
from app.models import NewsItem, Subject, ExamType
from app.schemas import NewsItemCreate, NewsItemUpdate, NewsItemResponse
from app.services.telegram import send_telegram_message, format_post_for_telegram

router = APIRouter()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev_admin_key_123")

async def verify_admin_key(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key"
        )

# ------------------------
# Helper to convert NewsItem to response with subject/exam names
# ------------------------
def news_item_to_response(news: NewsItem) -> NewsItemResponse:
    return NewsItemResponse(
        id=news.id,
        title=news.title,
        body=news.body,
        hashtags=news.hashtags,
        source_url=news.source_url,
        media_url=news.media_url,
        status=news.status,
        published_at=news.published_at,
        scheduled_for=news.scheduled_for,
        created_at=news.created_at,
        updated_at=news.updated_at,
        subjects=[s.name for s in news.subjects],
        exam_types=[e.name for e in news.exam_types]
    )

# ------------------------
# Admin: List all news items (any status)
# ------------------------
@router.get("/news", response_model=List[NewsItemResponse], dependencies=[Depends(verify_admin_key)])
async def admin_list_news(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).order_by(NewsItem.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    news_list = result.scalars().unique().all()
    return [news_item_to_response(n) for n in news_list]

# ------------------------
# Admin: Get single news item
# ------------------------
@router.get("/news/{news_id}", response_model=NewsItemResponse, dependencies=[Depends(verify_admin_key)])
async def admin_get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).where(NewsItem.id == news_id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(404, "News item not found")
    return news_item_to_response(news)

# ------------------------
# Admin: Create news item
# ------------------------
@router.post("/news", response_model=NewsItemResponse, status_code=201, dependencies=[Depends(verify_admin_key)])
async def admin_create_news(payload: NewsItemCreate, db: AsyncSession = Depends(get_db)):
    # Fetch subjects and exam types
    subjects = []
    if payload.subject_ids:
        subj_result = await db.execute(select(Subject).where(Subject.id.in_(payload.subject_ids)))
        subjects = list(subj_result.scalars().all())
    exam_types = []
    if payload.exam_type_ids:
        exam_result = await db.execute(select(ExamType).where(ExamType.id.in_(payload.exam_type_ids)))
        exam_types = list(exam_result.scalars().all())

    news = NewsItem(
        title=payload.title,
        body=payload.body,
        hashtags=payload.hashtags,
        source_url=payload.source_url,
        media_url=payload.media_url,
        status=payload.status,
        scheduled_for=payload.scheduled_for,
        subjects=subjects,
        exam_types=exam_types
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)

    # Reload with relationships
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).where(NewsItem.id == news.id)
    result = await db.execute(query)
    news = result.scalar_one()
    return news_item_to_response(news)

# ------------------------
# Admin: Update news item
# ------------------------
@router.put("/news/{news_id}", response_model=NewsItemResponse, dependencies=[Depends(verify_admin_key)])
async def admin_update_news(news_id: int, payload: NewsItemUpdate, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).where(NewsItem.id == news_id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(404, "News item not found")

    update_data = payload.dict(exclude_unset=True)
    # Handle relationship updates separately
    if 'subject_ids' in update_data:
        subj_result = await db.execute(select(Subject).where(Subject.id.in_(update_data.pop('subject_ids'))))
        news.subjects = list(subj_result.scalars().all())
    if 'exam_type_ids' in update_data:
        exam_result = await db.execute(select(ExamType).where(ExamType.id.in_(update_data.pop('exam_type_ids'))))
        news.exam_types = list(exam_result.scalars().all())

    for key, value in update_data.items():
        setattr(news, key, value)

    await db.commit()
    # Refresh
    result = await db.execute(query)
    news = result.scalar_one()
    return news_item_to_response(news)

# ------------------------
# Admin: Delete news item
# ------------------------
@router.delete("/news/{news_id}", status_code=204, dependencies=[Depends(verify_admin_key)])
async def admin_delete_news(news_id: int, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).where(NewsItem.id == news_id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(404, "News item not found")
    await db.delete(news)
    await db.commit()
    return None

# ------------------------
# Admin: Publish news item (and send to Telegram)
# ------------------------
@router.post("/news/{news_id}/publish", response_model=NewsItemResponse, dependencies=[Depends(verify_admin_key)])
async def admin_publish_news(news_id: int, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).where(NewsItem.id == news_id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(404, "News item not found")

    # Update status and publish time
    news.status = "published"
    news.published_at = datetime.utcnow()
    await db.commit()

    # Prepare Telegram message
    # Assuming the website URL will be something like https://yourdomain.com/news/{id}
    # For now, use a placeholder
    link = f"https://yourdomain.com/news/{news.id}"
    telegram_text = format_post_for_telegram(news.title, news.hashtags, link)

    # Send to Telegram (best-effort; log errors but don't fail the publish)
    try:
        await send_telegram_message(telegram_text)
        print(f"Telegram message sent for news {news.id}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

    # Refresh
    result = await db.execute(query)
    news = result.scalar_one()
    return news_item_to_response(news)
