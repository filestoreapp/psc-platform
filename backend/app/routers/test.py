from fastapi import APIRouter
from app.services.telegram import send_telegram_message, format_post_for_telegram

router = APIRouter()

@router.post("/test/telegram")
async def test_telegram():
    msg = format_post_for_telegram("Test Heading", "#Test #PSC", "https://example.com")
    await send_telegram_message(msg)
    return {"status": "sent"}
