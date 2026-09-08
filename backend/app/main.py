from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import news, quizzes, admin, test, subjects_exams

app = FastAPI(title="PSC Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api/v1", tags=["news"])
app.include_router(quizzes.router, prefix="/api/v1", tags=["quizzes"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(subjects_exams.router, prefix="/api/v1", tags=["subjects-exams"])
app.include_router(test.router, prefix="/api/v1", tags=["test"])

@app.get("/")
async def root():
    return {"message": "PSC Platform API running"}
