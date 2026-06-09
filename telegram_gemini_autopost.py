import os
from datetime import datetime
import requests
from google import genai
import csv
from io import StringIO

# Константы
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TG_CHANNEL_ID = os.environ["TG_CHANNEL_ID"]

MODEL = "gemini-3.5-flash"

# URL с полным списком иероглифов по частотности (9000+ иероглифов)
HANZIDB_URL = "https://raw.githubusercontent.com/ruddfawcett/hanziDB.csv/master/hanziDB.csv"

def load_chinese_characters_from_url() -> list:
    """Загружает список иероглифов из hanziDB.csv (9000+ иероглифов по частотности)"""
    print("📥 Загрузка списка иероглифов из hanziDB...")
    
    try:
        response = requests.get(HANZIDB_URL, timeout=30)
        response.raise_for_status()
        
        # Парсим CSV
        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)
        
        characters = []
        for row in reader:
            # hanziDB.csv структура: rank, char, frequency, pinyin, meanings
            if len(row) >= 5:
                try:
                    rank = int(row[0])
                    char = row[1]
                    frequency = float(row[2]) if row[2] else 0
                    pinyin = row[3] if row[3] else ""
                    meanings = row[4] if row[4] else ""
                    
                    characters.append({
                        "rank": rank,
                        "char": char,
                        "frequency": frequency,
                        "pinyin": pinyin,
                        "meaning": meanings
                    })
                except (ValueError, IndexError):
                    continue
        
        print(f"✅ Загружено {len(characters)} иероглифов")
        return characters
    
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        # Если не удалось загруть — используем минимальный список
        return [
            {"rank": 1, "char": "的", "frequency": 0.0, "pinyin": "de", "meaning": "притяжательная частица"},
            {"rank": 2, "char": "一", "frequency": 0.0, "pinyin": "yī", "meaning": "один"},
            {"rank": 3, "char": "是", "frequency": 0.0, "pinyin": "shì", "meaning": "быть, являться"},
            {"rank": 4, "char": "不", "frequency": 0.0, "pinyin": "bù", "meaning": "нет, не"},
            {"rank": 5, "char": "了", "frequency": 0.0, "pinyin": "le", "meaning": "показатель завершения"},
        ]

def get_current_char_index(characters: list) -> int:
    """Определяет индекс иероглифа по времени (каждые 5 минут новый)"""
    now = datetime.now()
    # Учитываем минуты: (час * 60 + минуты) / 5
    total_intervals = (now.hour * 60 + now.minute) // 5
    return total_intervals % len(characters)

def get_structural_analysis(char: str, pinyin: str, meaning: str) -> str:
    """Генерирует структурный разбор по графемам через Gemini"""
    prompt = f"""
Подробный разбор китайского иероглифа {char} (пиньинь: {pinyin}, значение: {meaning}):

1. Графемы (ключи/радикалы):
   - Назови все графемы, из которых состоит иероглиф
   - Для каждой графемы: смысл, значение, роль в иероглифе
   - Укажи номер радикала (если есть)

2. Логика сочетания графем:
   - Как графемы сочетаются (смысл + фонетика? лево + право? верх + ниж?)
   - Дай 2-3 версии логики формирования иероглифа
   - Историческое происхождение (если известно)

3. Примеры использования (5-7 примеров):
   - Фразы с иероглифом
   - Перевод фраз на русский
   - Пиньинь для каждой фразы
   - Контекст использования

4. Дополнительная информация:
   - Число черт (ударений)
   - Категория иероглифа (простой/сложный/комбинированный)
   - Уровень HSK (если есть)
   - Частотность (rank в списке)
   - Грамматическая роль
   - Синонимы/антонимы (если есть)

Формат: чёткий, структурированный, без лишних эмодзи. Используй разделители и подзаголовки.
"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text or ""

def format_telegram_post(char_data: dict, analysis: str) -> str:
    """Формирует красивый пост для Telegram"""
    today = datetime.now().strftime("%d.%m.%Y")
    time_str = datetime.now().strftime("%H:%M")
    rank = char_data['rank']
    frequency = char_data.get('frequency', 0)
    
    post = f"""
╔═══════════════════════════════════════════╗
║           📚 КИТАЙСКИЙ ИЕРОГЛИФ           ║
║          Разбор по частотности            ║
╠═══════════════════════════════════════════╣

🔢 Rank #{rank} из 9000+ частотных иероглифов
{char_data['char']} — {char_data['pinyin']} — {char_data['meaning']}
Частотность: {frequency:.6f}%

═══════════════════════════════════════════

{analysis}

═══════════════════════════════════════════
📅 {today} | 🕐 {time_str}
🔡 #{rank} по частотности в современном китайском
"""
    return post.strip()

def send_to_telegram(text: str) -> None:
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": TG_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=30
    )
    response.raise_for_status()

def main():
    """Главная функция"""
    # Загружаем список иероглифов
    characters = load_chinese_characters_from_url()
    
    # Получаем текущий индекс
    char_index = get_current_char_index(characters)
    char_data = characters[char_index]
    
    print(f"📖 Разбор иероглифа Rank #{char_data['rank']}: {char_data['char']}")
    
    # Получаем структурный разбор
    analysis = get_structural_analysis(
        char_data['char'],
        char_data['pinyin'],
        char_data['meaning']
    )
    
    # Формируем пост
    post = format_telegram_post(char_data, analysis)
    
    # Отправляем в Telegram
    send_to_telegram(post)
    
    print("✅ Пост успешно отправлен!")

if __name__ == "__main__":
    main()
