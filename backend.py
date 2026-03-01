# backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Разрешаем запросы с вашего HTML
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # потом замените на конкретный адрес
    allow_methods=["*"],
    allow_headers=["*"],
)

# ВСТАВЬТЕ СВОЙ API-КЛЮЧ СЮДА 👇
DEEPSEEK_API_KEY = "sk-b55cc0587ce2454da6f86a1432f9da3a"  # замените на ваш ключ

class ChatRequest(BaseModel):
    messages: list
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 500
    stream: bool = False

class Message(BaseModel):
    role: str
    content: str

@app.post("/chat")
async def chat(request: dict):
    """Просто возвращает то, что получил"""
    print("🔥 Получен запрос от фронтенда!")
    print("Данные:", request)
    return {"reply": "Привет от бэкенда! Я работаю."}
async def chat(request: ChatRequest):
    """Принимает историю сообщений, отправляет в DeepSeek, возвращает ответ"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": request.model,
                "messages": request.messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": request.stream
            },
            timeout=30.0
        )
    
    if response.status_code == 200:
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        return {"reply": reply}
    else:
        return {"reply": "Извините, что-то пошло не так. Попробуйте ещё раз."}

@app.get("/health")
async def health():

    return {"status": "ok"}
