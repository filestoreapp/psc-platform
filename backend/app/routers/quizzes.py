from fastapi import APIRouter

router = APIRouter()

@router.get("/quizzes")
async def list_quizzes():
    return []
