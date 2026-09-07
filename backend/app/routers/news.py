from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import NewsItem, Subject, ExamType
from app.schemas import NewsItemResponse

router = APIRouter()

@router.get("/news", response_model=list[NewsItemResponse])
async def list_news(
    skip: int = 0,
    limit: int = 20,
    subject: str = Query(None, description="Filter by subject name"),
    exam_type: str = Query(None, description="Filter by exam type name"),
    db: AsyncSession = Depends(get_db)
):
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).where(NewsItem.status == "published")

    if subject:
        query = query.join(NewsItem.subjects).where(Subject.name == subject)
    if exam_type:
        query = query.join(NewsItem.exam_types).where(ExamType.name == exam_type)

    query = query.order_by(NewsItem.published_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    news = result.scalars().unique().all()
    return news

@router.get("/news/{news_id}", response_model=NewsItemResponse)
async def get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).options(
        selectinload(NewsItem.subjects),
        selectinload(NewsItem.exam_types)
    ).where(NewsItem.id == news_id, NewsItem.status == "published")
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(404, "News item not found")
    return news
