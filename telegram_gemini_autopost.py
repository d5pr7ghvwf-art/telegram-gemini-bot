import os
from datetime import datetime
import requests
from google import genai

# Константы
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TG_CHANNEL_ID = os.environ["TG_CHANNEL_ID"]

MODEL = "gemini-3.1-flash-lite" 

# ТОП-100 ЧАСТОТНЫХ ИЕРОГЛИФОВ
CHARACTERS = [
    {"rank": 1, "char": "的", "pinyin": "de", "meaning": "притяжательная частица"},
    {"rank": 2, "char": "一", "pinyin": "yī", "meaning": "один"},
    {"rank": 3, "char": "是", "pinyin": "shì", "meaning": "быть, являться"},
    {"rank": 4, "char": "不", "pinyin": "bù", "meaning": "нет, не"},
    {"rank": 5, "char": "了", "pinyin": "le", "meaning": "показатель завершения"},
    {"rank": 6, "char": "我", "pinyin": "wǒ", "meaning": "я"},
    {"rank": 7, "char": "你", "pinyin": "nǐ", "meaning": "ты"},
    {"rank": 8, "char": "有", "pinyin": "yǒu", "meaning": "иметь"},
    {"rank": 9, "char": "他", "pinyin": "tā", "meaning": "он"},
    {"rank": 10, "char": "人", "pinyin": "rén", "meaning": "человек"},
    {"rank": 11, "char": "在", "pinyin": "zài", "meaning": "находиться, в"},
    {"rank": 12, "char": "这", "pinyin": "zhè", "meaning": "это"},
    {"rank": 13, "char": "来", "pinyin": "lái", "meaning": "приходить"},
    {"rank": 14, "char": "去", "pinyin": "qù", "meaning": "уходить"},
    {"rank": 15, "char": "大", "pinyin": "dà", "meaning": "большой"},
    {"rank": 16, "char": "小", "pinyin": "xiǎo", "meaning": "маленький"},
    {"rank": 17, "char": "多", "pinyin": "duō", "meaning": "много"},
    {"rank": 18, "char": "少", "pinyin": "shǎo", "meaning": "мало"},
    {"rank": 19, "char": "看", "pinyin": "kàn", "meaning": "смотреть"},
    {"rank": 20, "char": "说", "pinyin": "shuō", "meaning": "говорить"},
    {"rank": 21, "char": "吗", "pinyin": "ma", "meaning": "вопросительная частица"},
    {"rank": 22, "char": "好", "pinyin": "hǎo", "meaning": "хороший"},
    {"rank": 23, "char": "她", "pinyin": "tā", "meaning": "она"},
    {"rank": 24, "char": "它", "pinyin": "tā", "meaning": "это (предмет)"},
    {"rank": 25, "char": "个", "pinyin": "gè", "meaning": "счётное слово"},
    {"rank": 26, "char": "中", "pinyin": "zhōng", "meaning": "центр, в"},
    {"rank": 27, "char": "上", "pinyin": "shàng", "meaning": "верх, на"},
    {"rank": 28, "char": "下", "pinyin": "xià", "meaning": "низ, под"},
    {"rank": 29, "char": "年", "pinyin": "nián", "meaning": "год"},
    {"rank": 30, "char": "月", "pinyin": "yuè", "meaning": "месяц"},
    {"rank": 31, "char": "日", "pinyin": "rì", "meaning": "день"},
    {"rank": 32, "char": "时", "pinyin": "shí", "meaning": "час"},
    {"rank": 33, "char": "分", "pinyin": "fēn", "meaning": "минута"},
    {"rank": 34, "char": "晚", "pinyin": "wǎn", "meaning": "вечер"},
    {"rank": 35, "char": "早", "pinyin": "zǎo", "meaning": "утро"},
    {"rank": 36, "char": "爱", "pinyin": "ài", "meaning": "любить"},
    {"rank": 37, "char": "吃", "pinyin": "chī", "meaning": "есть"},
    {"rank": 38, "char": "喝", "pinyin": "hē", "meaning": "пить"},
    {"rank": 39, "char": "走", "pinyin": "zǒu", "meaning": "ходить"},
    {"rank": 40, "char": "跑", "pinyin": "pǎo", "meaning": "бежать"},
    {"rank": 41, "char": "听", "pinyin": "tīng", "meaning": "слушать"},
    {"rank": 42, "char": "写", "pinyin": "xiě", "meaning": "писать"},
    {"rank": 43, "char": "读", "pinyin": "dú", "meaning": "читать"},
    {"rank": 44, "char": "学", "pinyin": "xué", "meaning": "учить"},
    {"rank": 45, "char": "工", "pinyin": "gōng", "meaning": "работа"},
    {"rank": 46, "char": "家", "pinyin": "jiā", "meaning": "дом"},
    {"rank": 47, "char": "国", "pinyin": "guó", "meaning": "страна"},
    {"rank": 48, "char": "语", "pinyin": "yǔ", "meaning": "язык"},
    {"rank": 49, "char": "文", "pinyin": "wén", "meaning": "текст"},
    {"rank": 50, "char": "书", "pinyin": "shū", "meaning": "книга"},
    {"rank": 51, "char": "门", "pinyin": "mén", "meaning": "дверь"},
    {"rank": 52, "char": "口", "pinyin": "kǒu", "meaning": "рот"},
    {"rank": 53, "char": "手", "pinyin": "shǒu", "meaning": "рука"},
    {"rank": 54, "char": "心", "pinyin": "xīn", "meaning": "сердце"},
    {"rank": 55, "char": "水", "pinyin": "shuǐ", "meaning": "вода"},
    {"rank": 56, "char": "火", "pinyin": "huǒ", "meaning": "огонь"},
    {"rank": 57, "char": "山", "pinyin": "shān", "meaning": "гора"},
    {"rank": 58, "char": "钱", "pinyin": "qián", "meaning": "деньги"},
    {"rank": 59, "char": "车", "pinyin": "chē", "meaning": "машина"},
    {"rank": 60, "char": "路", "pinyin": "lù", "meaning": "дорога"},
    {"rank": 61, "char": "买", "pinyin": "mǎi", "meaning": "покупать"},
    {"rank": 62, "char": "卖", "pinyin": "mài", "meaning": "продавать"},
    {"rank": 63, "char": "新", "pinyin": "xīn", "meaning": "новый"},
    {"rank": 64, "char": "好", "pinyin": "hǎo", "meaning": "хорошо"},
    {"rank": 65, "char": "对", "pinyin": "duì", "meaning": "правильно"},
    {"rank": 66, "char": "错", "pinyin": "cuò", "meaning": "неправильно"},
    {"rank": 67, "char": "问", "pinyin": "wèn", "meaning": "спрашивать"},
    {"rank": 68, "char": "答", "pinyin": "dá", "meaning": "ответ"},
    {"rank": 69, "char": "请", "pinyin": "qǐng", "meaning": "просить"},
    {"rank": 70, "char": "谢", "pinyin": "xiè", "meaning": "спасибо"},
    {"rank": 71, "char": "生", "pinyin": "shēng", "meaning": "жить"},
    {"rank": 72, "char": "死", "pinyin": "sǐ", "meaning": "умереть"},
    {"rank": 73, "char": "快", "pinyin": "kuài", "meaning": "быстро"},
    {"rank": 74, "char": "慢", "pinyin": "màn", "meaning": "медленно"},
    {"rank": 75, "char": "热", "pinyin": "rè", "meaning": "горячо"},
    {"rank": 76, "char": "冷", "pinyin": "lěng", "meaning": "холодно"},
    {"rank": 77, "char": "长", "pinyin": "cháng", "meaning": "долгий"},
    {"rank": 78, "char": "短", "pinyin": "duǎn", "meaning": "короткий"},
    {"rank": 79, "char": "高", "pinyin": "gāo", "meaning": "высокий"},
    {"rank": 80, "char": "低", "pinyin": "dī", "meaning": "низкий"},
    {"rank": 81, "char": "口", "pinyin": "kǒu", "meaning": "рот"},
    {"rank": 82, "char": "目", "pinyin": "mù", "meaning": "глаз"},
    {"rank": 83, "char": "耳", "pinyin": "ěr", "meaning": "ухо"},
    {"rank": 84, "char": "头", "pinyin": "tóu", "meaning": "голова"},
    {"rank": 85, "char": "手", "pinyin": "shǒu", "meaning": "рука"},
    {"rank": 86, "char": "足", "pinyin": "zú", "meaning": "нога"},
    {"rank": 87, "char": "名", "pinyin": "míng", "meaning": "имя"},
    {"rank": 88, "char": "字", "pinyin": "zì", "meaning": "иероглиф"},
    {"rank": 89, "char": "音", "pinyin": "yīn", "meaning": "звук"},
    {"rank": 90, "char": "声", "pinyin": "shēng", "meaning": "голос"},
    {"rank": 91, "char": "海", "pinyin": "hǎi", "meaning": "море"},
    {"rank": 92, "char": "河", "pinyin": "hé", "meaning": "река"},
    {"rank": 93, "char": "桥", "pinyin": "qiáo", "meaning": "мост"},
    {"rank": 94, "char": "土", "pinyin": "tǔ", "meaning": "земля"},
    {"rank": 95, "char": "金", "pinyin": "jīn", "meaning": "золото"},
    {"rank": 96, "char": "木", "pinyin": "mù", "meaning": "дерево"},
    {"rank": 97, "char": "风", "pinyin": "fēng", "meaning": "ветер"},
    {"rank": 98, "char": "雨", "pinyin": "yǔ", "meaning": "дождь"},
    {"rank": 99, "char": "天", "pinyin": "tiān", "meaning": "небо"},
    {"rank": 100, "char": "地", "pinyin": "dì", "meaning": "земля"},
]

def get_current_char_index() -> int:
    now = datetime.now()
    total_intervals = (now.hour * 60 + now.minute) // 5
    return total_intervals % len(CHARACTERS)

def get_structural_analysis(char: str, pinyin: str, meaning: str) -> str:
    prompt = f"""
Разбор китайского иероглифа {char} ({pinyin}, {meaning}):

1. Части иероглифа (ключи/радикалы):
   - Какие части входят
   - Значение каждой части

2. Как образовался иероглиф:
   - Логика сочетания частей
   - Историческое происхождение (если известно)

3. Примеры (3-5):
   - Фраза с иероглифом
   - Перевод
   - Пиньинь

4. Факты:
   - Число черт
   - Уровень HSK (если есть)
   - Грамматическая роль

Чётко, кратко, без эмодзи.
"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text or ""

def format_telegram_post(char_data: dict, analysis: str) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    time_str = datetime.now().strftime("%H:%M")
    rank = char_data['rank']
    
    analysis = analysis.replace("*", "")
    
    post = f"""
ИЕРОГЛИФ #{rank} из 100

{char_data['char']}  {char_data['pinyin']}
{char_data['meaning']}

{analysis}

—
{today} {time_str} | #{rank} по частотности
"""
    return post.strip()

def send_to_telegram(text: str) -> None:
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
    char_index = get_current_char_index()
    char_data = CHARACTERS[char_index]
    
    print(f"Разбор: {char_data['char']} (#{char_data['rank']})")
    
    analysis = get_structural_analysis(
        char_data['char'],
        char_data['pinyin'],
        char_data['meaning']
    )
    
    post = format_telegram_post(char_data, analysis)
    send_to_telegram(post)
    
    print("✅ Отправлено")

if __name__ == "__main__":
    main()
