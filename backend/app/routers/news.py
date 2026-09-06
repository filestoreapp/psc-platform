from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import NewsItem
from app.schemas import NewsItemResponse

router = APIRouter()

@router.get("/news", response_model=list[NewsItemResponse])
async def list_news(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    query = select(NewsItem).where(NewsItem.status == "published").order_by(NewsItem.published_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
