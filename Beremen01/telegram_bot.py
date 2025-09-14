import os
import requests
from flask import Flask, request, jsonify

# Telegram Bot Token (получите у @BotFather)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://your-domain.com/webhook')

def set_webhook():
    """Устанавливает webhook для Telegram Bot"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {
        'url': WEBHOOK_URL,
        'allowed_updates': ['message']
    }
    
    response = requests.post(url, data=data)
    return response.json()

def send_message(chat_id, text):
    """Отправляет сообщение пользователю"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, data=data)
    return response.json()

def create_webapp_button():
    """Создает кнопку для запуска Web App"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    commands = [
        {
            "command": "start",
            "description": "Запустить приложение для беременных"
        }
    ]
    
    response = requests.post(url, json={'commands': commands})
    return response.json()

if __name__ == "__main__":
    print("🤖 Настройка Telegram Bot...")
    
    # Создаем команды
    result = create_webapp_button()
    print("📋 Команды созданы:", result)
    
    # Устанавливаем webhook
    result = set_webhook()
    print("🔗 Webhook установлен:", result)
    
    print("✅ Настройка завершена!")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
