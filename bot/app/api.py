import base64
from openai import OpenAI
import os
from dotenv import load_dotenv
from bot.config import OPEN_AI

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPEN_AI
)

def creat_category(image_path, text, title):
    import base64

    # если фото нет — просто пропускаем
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        image_part = [
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }}
        ]
    else:
        image_part = []  # без изображения

    prompt = f"""
Ты — искусственный интеллект, который анализирует жалобы пользователей.

Дано:
- Заголовок: "{title}"
- Описание: "{text}"

Если есть фото — оно передано отдельно.
Твоя задача — определить категорию жалобы:

1. CRITICAL — если жалоба очень важная (коррупция, злоупотребление властью, серьёзное нарушение закона);
2. SECONDARY — если жалоба обычная (бытовые, мелкие проблемы, недовольство, не серьёзные нарушение закона );
3. SPAM — если жалоба не имеет смысла, реклама, шутка, оффтоп.

Выведи только одно слово: CRITICAL, SECONDARY или SPAM.
"""

    completion = client.chat.completions.create(
        model="qwen/qwen2.5-vl-32b-instruct:free",
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}] + image_part
            }
        ]
    )

    return completion.choices[0].message.content.strip().upper()
