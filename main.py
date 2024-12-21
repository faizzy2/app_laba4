import telebot
import requests
import json
import datetime
from math import ceil
from API import API_KEY, TG_TOKEN

bot = telebot.TeleBot(TG_TOKEN)
currents_city = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}, этот бот нужен для получения погоды по городу. Ты можешь выбрать город с помощью /change_city.")
    currents_city[message.from_user.id] = "Москва"
    print(currents_city[message.from_user.id], message.from_user.id)

@bot.message_handler(commands=['change_city'])
def change_city(message):
    msg = bot.send_message(message.chat.id, f"Введите город, погоду которого, вы хотели бы узнавать. Текущий город - {currents_city[message.from_user.id]}")
    bot.register_next_step_handler(msg, save_city)

def save_city(message):
    user_id = message.from_user.id
    currents_city[user_id] = message.text

@bot.message_handler(commands=['weather'])
def weather(message):
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={currents_city[message.from_user.id]}&lang=ru&units=metric&appid={API_KEY}")
        response.raise_for_status()
        data = response.json()
        city = data["name"]
        cur_temp = data["main"]["temp"]
        cur_feels_like_temp = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        bot.send_message(message.chat.id,
                         f"Погода в городе {city} на момент {datetime.datetime.now().strftime('%H:%M %d.%m.%Y')}:\n"
                         f"Температура: {cur_temp}°C ощущается как {cur_feels_like_temp}°C\n"
                         f"Влажность: {humidity}%\n"
                         f"Давление: {ceil(pressure / 1.333)} мм.рт.ст\n"
                         f"Скорость ветра: {wind} м/с\n")
    except:
        bot.send_message(message.chat.id, "Проверьте название города.")

@bot.message_handler(commands=['weather_tomorrow'])
def weather_tomorrow(message):
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={currents_city[message.from_user.id]}&lang=ru&cnt=8&units=metric&appid={API_KEY}")
        response.raise_for_status()
        data = response.json()
        city = data['city']['name']
        for item in data['list']:
            date_time = item['dt_txt']
            temperature = item['main']['temp']
            feels_like_temp = item['main']['feels_like']
            pressure = item['main']['pressure']
            humidity = item['main']['humidity']
            wind = item['wind']['speed']

            bot.send_message(message.chat.id,
                            f"Погода в городе {city} на момент {date_time}:\n"
                            f"Температура: {temperature}°C ощущается как {feels_like_temp}°C\n"
                            f"Влажность: {humidity}%\n"
                            f"Давление: {ceil(pressure / 1.333)} мм.рт.ст\n"
                            f"Скорость ветра: {wind} м/с\n")
    except:
        bot.send_message(message.chat.id, "Проверьте название города.")

bot.polling(none_stop=True)