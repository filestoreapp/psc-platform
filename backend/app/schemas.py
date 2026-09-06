from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NewsItemCreate(BaseModel):
    title: str
    body: str
    hashtags: Optional[str] = None
    source_url: Optional[str] = None
    media_url: Optional[str] = None
    subject_ids: List[int] = []
    exam_type_ids: List[int] = []
    status: str = "draft"
    scheduled_for: Optional[datetime] = None

class NewsItemResponse(BaseModel):
    id: int
    title: str
    body: str
    hashtags: Optional[str]
    source_url: Optional[str]
    media_url: Optional[str]
    status: str
    published_at: Optional[datetime]
    scheduled_for: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    subjects: List[str] = []
    exam_types: List[str] = []
    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: Optional[str] = None
    order_index: int = 0

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    quiz_type: str = "daily"
    linked_news_item_id: Optional[int] = None
    time_per_question_seconds: int = 10
    questions: List[QuestionCreate]

class QuizAttemptSubmit(BaseModel):
    student_name: str
    answers: List[dict]
