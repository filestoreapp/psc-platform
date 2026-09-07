from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import Subject, ExamType
from app.routers.admin import verify_admin_key

router = APIRouter()

# ---------- Public: List Subjects ----------
@router.get("/subjects", response_model=List[dict])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).order_by(Subject.name))
    subjects = result.scalars().all()
    return [{"id": s.id, "name": s.name, "description": s.description} for s in subjects]

# ---------- Public: List Exam Types ----------
@router.get("/exam-types", response_model=List[dict])
async def list_exam_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExamType).order_by(ExamType.name))
    exam_types = result.scalars().all()
    return [{"id": e.id, "name": e.name, "description": e.description} for e in exam_types]

# ---------- Admin: Create Subject ----------
@router.post("/admin/subjects", status_code=201, dependencies=[Depends(verify_admin_key)])
async def create_subject(name: str, description: str = None, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Subject).where(Subject.name == name))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Subject already exists")
    subject = Subject(name=name, description=description)
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return {"id": subject.id, "name": subject.name, "description": subject.description}

# ---------- Admin: Create Exam Type ----------
@router.post("/admin/exam-types", status_code=201, dependencies=[Depends(verify_admin_key)])
async def create_exam_type(name: str, description: str = None, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(ExamType).where(ExamType.name == name))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Exam type already exists")
    exam_type = ExamType(name=name, description=description)
    db.add(exam_type)
    await db.commit()
    await db.refresh(exam_type)
    return {"id": exam_type.id, "name": exam_type.name, "description": exam_type.description}
