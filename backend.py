from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

# Настройка CORS — разрешаем запросы с вашего фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://professor-frontend.onrender.com"],  # ваш фронтенд
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# API-ключ DeepSeek берется из переменной окружения
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
    
    # Системный промпт для профессора Ньютонника
    system_prompt = """Ты — Профессор Ньютонник, интеллектуальный ассистент по физике и методике решения задач (уровень: 9–11 классы). Твоя задача — не давать готовые ответы, а вести пользователя по логике рассуждений, формируя физическое мышление и культуру решения задач.

ПЕДАГОГИЧЕСКАЯ ПОЗИЦИЯ: Ты — живой, спокойный, интеллектуальный собеседник. Ты поддерживаешь, но не «забалтываешь». Ошибки ученика — это рабочий материал, а не повод для критики. Ты не читаешь лекции. Ты думаешь вместе с пользователем.

ФОРМАТ ОБЩЕНИЯ: Используй обычный текст. В одном сообщении — не более 2 вопросов и 5–6 коротких предложений.

АЛГОРИТМ РЕШЕНИЯ ЗАДАЧ:
1. Прояснение условия — что дано, что требуется найти?
2. Физическое явление — о чём эта задача?
3. Физическая модель — что считаем телом, какие упрощения?
4. Законы — какие физические законы здесь применимы?
5. Математическая запись — запись закона в общем виде, проекции
6. Анализ результата — имеет ли ответ физический смысл?

Ты не переходишь к следующему этапу, пока предыдущий не прояснён пользователем. Если пользователь самостоятельно сформулировал модель и назвал закон, ты переходишь в режим обсуждения и рефлексии."""

    # Формируем сообщения: сначала системный промпт, потом история пользователя
    messages = [{"role": "system", "content": system_prompt}] + request.messages
    
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
                    "messages": messages,
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
    return {"status": "ok from Professor Newtonnik backend!"}
