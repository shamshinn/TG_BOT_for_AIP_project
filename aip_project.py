import telebot
import requests
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot("7577651406:AAF2eIvZFmyzRF8ZcLacY92NKwTsBrvNd3I")
api = "5aa88eac6f3139d8023526ee7c493dc9"
user_city = {}  # Словарь для хранения выбранного города для каждого пользователя

def create_city_buttons():
    """
    Создает клавиатуру с кнопками популярных городов и действий.
    
    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопками для выбора города и выполнения действий.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
    for city in cities:
        markup.add(KeyboardButton(city))
    markup.add(KeyboardButton("Начать заново"))
    markup.add(KeyboardButton("Очистить чат"))
    markup.add(KeyboardButton("Прогноз на 5 дней"))
    markup.add(KeyboardButton("Узнать влажность"))
    markup.add(KeyboardButton("Прогноз на 1 день"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    """
    Обрабатывает команду /start, отправляя приветственное сообщение и клавиатуру.

    Аргументы:
        message (telebot.types.Message): Объект сообщения телеграма.
    """
    markup = create_city_buttons()
    bot.send_message(
        message.chat.id, 
        "Привет! Выбери город из списка или введи название своего города:", 
        reply_markup=markup
    )

@bot.message_handler(content_types=["text"])
def handle_message(message):
    """
    Обрабатывает текстовые сообщения пользователя, выполняя соответствующие действия: 
    выбор города, очистка чата, получение прогноза погоды и т.д.

    Аргументы:
        message (telebot.types.Message): Объект сообщения телеграма.
    """
    global user_city

    if message.text.strip().lower() == "начать заново":
        start(message)
        return

    if message.text.strip().lower() == "очистить чат":
        clear_chat(message)
        return

    if message.text.strip().lower() == "прогноз на 5 дней":
        city = user_city.get(message.chat.id, None)
        if city:
            send_forecast(message, city)
        else:
            bot.reply_to(message, "Сначала выберите город!")
        return

    if message.text.strip().lower() == "узнать влажность":
        city = user_city.get(message.chat.id, None)
        if city:
            send_humidity(message, city)
        else:
            bot.reply_to(message, "Сначала выберите город!")
        return

    if message.text.strip().lower() == "прогноз на 1 день":
        city = user_city.get(message.chat.id, None)
        if city:
            get_weather_details(message, city)
        else:
            bot.reply_to(message, "Сначала выберите город!")
        return

    city = message.text.strip().capitalize()
    user_city[message.chat.id] = city
    bot.reply_to(message, f"Город {city} выбран. Вы можете узнать влажность или прогноз погоды.")

def clear_chat(message):
    """
    Очищает чат, удаляя последние сообщения.

    Аргументы:
        message (telebot.types.Message): Объект сообщения телеграма.
    """
    for msg_id in range(message.message_id, max(0, message.message_id - 100), -1):
        try:
            bot.delete_message(message.chat.id, msg_id)
        except Exception:
            pass
    bot.send_message(message.chat.id, "Чат очищен.", reply_markup=create_city_buttons())

def get_weather_details(message, city):
    """
    Получает и отправляет текущую погоду для указанного города.

    Аргументы:
        message (telebot.types.Message): Объект сообщения телеграма.
        city (str): Название города.
    """
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric")
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        clouds = data["clouds"]["all"]
        weather = (
            f"Температура: {temp}°C\n"
            f"Облачность: {clouds}%"
        )
        bot.reply_to(message, weather)

        image = "aip1.png" if temp > 5.0 else "aip2.png"
        file = open("./" + image, "rb")
        bot.send_photo(message.chat.id, file)
    else:
        bot.reply_to(message, f"Город '{city}' не найден. Попробуйте снова.")

def send_forecast(message, city):
    """
    Получает и отправляет прогноз погоды на 5 дней для указанного города.

    Аргументы:
        message (telebot.types.Message): Объект сообщения телеграма.
        city (str): Название города.
    """
    res = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api}&units=metric")
    if res.status_code == 200:
        data = json.loads(res.text)
        forecast = "Прогноз погоды на 5 дней:\n"
        for item in data["list"][:5]:
            forecast += (
                f"Дата: {item['dt_txt']}\n"
                f"Температура: {item['main']['temp']}°C\n"
                f"Облачность: {item['clouds']['all']}%\n\n"
            )
        bot.reply_to(message, forecast)
    else:
        bot.reply_to(message, "Не удалось получить прогноз. Проверьте город.")

def send_humidity(message, city):
    """
    Получает и отправляет текущую влажность для указанного города.

    Аргументы:
        message (telebot.types.Message): Объект сообщения телеграма.
        city (str): Название города.
    """
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric")
    if res.status_code == 200:
        data = json.loads(res.text)
        humidity = data["main"]["humidity"]
        bot.reply_to(message, f"Влажность в городе {city}: {humidity}%")
    else:
        bot.reply_to(message, f"Город '{city}' не найден. Попробуйте снова.")


