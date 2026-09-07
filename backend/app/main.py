from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import news, quizzes, admin, test

app = FastAPI(title="PSC Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(news.router, prefix="/api/v1", tags=["news"])
app.include_router(quizzes.router, prefix="/api/v1", tags=["quizzes"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(test.router, prefix="/api/v1", tags=["test"])

@app.get("/")
async def root():
    return {"message": "PSC Platform API running"}
