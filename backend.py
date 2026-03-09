from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Настройка CORS — разрешаем запросы только с вашего фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://professor-frontend.onrender.com"],  # замените на ваш адрес
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ВАШ API-КЛЮЧ DEEPSEEK (вставьте свой)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# Модель данных для входящего запроса
class ChatRequest(BaseModel):
    messages: list
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 500

# Явная обработка OPTIONS-запросов (preflight)
@app.options("/chat")
async def options_chat():
    return {"allow": "POST, OPTIONS"}

# Основной обработчик сообщений
@app.post("/chat")
async def chat(request: ChatRequest):
    """Принимает историю сообщений, отправляет в DeepSeek, возвращает ответ"""
    
    try:
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
                    "max_tokens": request.max_tokens
                },
                timeout=30.0
            )
        
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return {"reply": reply}
        else:
            return {"reply": f"Ошибка DeepSeek API: {response.status_code}"}
    
    except Exception as e:
        return {"reply": f"Ошибка на сервере: {str(e)}"}

# Проверка работоспособности
@app.get("/health")
async def health():
    return {"status": "ok"}



