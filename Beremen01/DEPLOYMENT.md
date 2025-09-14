# 🚀 Развертывание приложения в Telegram

## 📋 Пошаговая инструкция

### 1. 🤖 Создание Telegram Bot

1. Откройте Telegram и найдите `@BotFather`
2. Отправьте команду `/newbot`
3. Введите имя бота: `Pregnancy Assistant`
4. Введите username: `pregnancy_assistant_bot` (должен заканчиваться на `_bot`)
5. **Сохраните токен** - он будет выглядеть как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. 🌐 Развертывание на Replit

1. **Загрузите код на Replit:**
   - Создайте новый проект в Replit
   - Загрузите все файлы проекта
   - Убедитесь, что файл `.replit` настроен правильно

2. **Настройте переменные окружения:**
   - В Replit перейдите в раздел "Secrets" (🔒)
   - Добавьте переменную `TELEGRAM_BOT_TOKEN` со значением вашего токена
   - Добавьте переменную `WEBHOOK_URL` со значением `https://your-replit-url.replit.app/webhook`

3. **Запустите приложение:**
   - Нажмите кнопку "Run" в Replit
   - Скопируйте URL вашего приложения (например: `https://pregnancy-app.replit.app`)

### 3. 🔗 Настройка Webhook

1. **Установите webhook:**
   ```bash
   python telegram_bot.py
   ```

2. **Или вручную через API:**
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-replit-url.replit.app/webhook
   ```

### 4. 📱 Настройка Web App в Telegram

1. Отправьте BotFather команду `/newapp`
2. Выберите вашего бота
3. Введите название: `Pregnancy Assistant`
4. Введите описание: `Приложение для отслеживания беременности`
5. Загрузите иконку (512x512px)
6. Введите URL: `https://your-replit-url.replit.app`

### 5. ✅ Проверка работы

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Нажмите кнопку "🚀 Открыть приложение"
4. Приложение должно открыться в Telegram

## 🔧 Альтернативные варианты развертывания

### Heroku
```bash
# Создайте Procfile
echo "web: python main.py" > Procfile

# Добавьте переменные окружения
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set WEBHOOK_URL=https://your-app.herokuapp.com/webhook
```

### Railway
```bash
# Создайте railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

## 🐛 Устранение неполадок

### Webhook не работает
- Проверьте, что URL доступен из интернета
- Убедитесь, что токен бота правильный
- Проверьте логи в Replit

### Приложение не открывается
- Убедитесь, что Web App настроен в BotFather
- Проверьте, что URL приложения правильный
- Убедитесь, что приложение работает локально

### Ошибки в логах
- Проверьте переменные окружения
- Убедитесь, что все зависимости установлены
- Проверьте подключение к базе данных

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи в Replit
2. Убедитесь, что все переменные окружения настроены
3. Проверьте доступность URL приложения
