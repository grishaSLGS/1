from openai import OpenAI

# Инициализация клиента OpenAI
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

# История сообщений (имитация чата)
chat_history = []

print("Консольный чат с нейросетью. Для выхода введите 'exit'")

while True:
    # Получение сообщения от пользователя
    user_input = input("Вы: ")
    
    if user_input.lower() == 'exit':
        print("Завершение сеанса...")
        break
    
    # Добавляем сообщение пользователя в историю
    chat_history.append({"role": "user", "content": user_input})
    
    try:
        # Отправка запроса к нейросети
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {"role": "system", "content": "Отвечай строго без форматирования: не используй **жирный**, _курсив_, ```блоки кода```. Только обычный текст."}
            ] + chat_history,
            temperature=0.7
        )
        
        # Получение и вывод ответа от нейросети
        if response.choices:
            ai_reply = response.choices[0].message.content
            print("AI:", ai_reply)
            
            # Добавляем ответ нейросети в историю
            chat_history.append({"role": "assistant", "content": ai_reply})
            
    except Exception as e:
        print("⚠️ Ошибка при обработке запроса к ИИ:", e)