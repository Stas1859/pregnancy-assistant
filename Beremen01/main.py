from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import date, datetime
import re
import os
import requests

app = Flask(__name__, static_folder="static")

# Функции валидации данных
def validate_user_id(user_id):
    """Валидация Telegram user ID"""
    if not user_id:
        return False, "Не указан ID пользователя"
    if not isinstance(user_id, (str, int)):
        return False, "Некорректный формат ID пользователя"
    if isinstance(user_id, str) and not user_id.isdigit():
        return False, "ID пользователя должен содержать только цифры"
    return True, None

def validate_weight(weight):
    """Валидация веса"""
    if weight is None:
        return False, "Не указан вес"
    try:
        weight_float = float(weight)
        if weight_float < 20 or weight_float > 300:
            return False, "Вес должен быть от 20 до 300 кг"
        return True, None
    except (ValueError, TypeError):
        return False, "Некорректный формат веса"

def validate_height(height):
    """Валидация роста"""
    if height is None:
        return False, "Не указан рост"
    try:
        height_int = int(height)
        if height_int < 100 or height_int > 250:
            return False, "Рост должен быть от 100 до 250 см"
        return True, None
    except (ValueError, TypeError):
        return False, "Некорректный формат роста"

def validate_pressure(systolic, diastolic):
    """Валидация артериального давления"""
    try:
        sys = int(systolic)
        dia = int(diastolic)
        if sys < 60 or sys > 250:
            return False, "Систолическое давление должно быть от 60 до 250"
        if dia < 40 or dia > 150:
            return False, "Диастолическое давление должно быть от 40 до 150"
        if sys <= dia:
            return False, "Систолическое давление должно быть больше диастолического"
        return True, None
    except (ValueError, TypeError):
        return False, "Некорректный формат давления"

def validate_date(date_str):
    """Валидация даты"""
    if not date_str:
        return False, "Не указана дата"
    try:
        parsed_date = datetime.fromisoformat(date_str).date()
        today = date.today()
        if parsed_date > today:
            return False, "Дата не может быть в будущем"
        if parsed_date < date(2020, 1, 1):
            return False, "Дата слишком старая"
        return True, None
    except ValueError:
        return False, "Некорректный формат даты"

def validate_weeks(weeks):
    """Валидация недель беременности"""
    try:
        weeks_int = int(weeks)
        if weeks_int < 0 or weeks_int > 42:
            return False, "Недели беременности должны быть от 0 до 42"
        return True, None
    except (ValueError, TypeError):
        return False, "Некорректный формат недель"

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Обработчик webhook от Telegram"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "ok"})
        
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        if text == '/start':
            # Отправляем приветственное сообщение с кнопкой Web App
            webapp_url = f"https://{request.host}/"
            
            keyboard = {
                "inline_keyboard": [[
                    {
                        "text": "🚀 Открыть приложение",
                        "web_app": {"url": webapp_url}
                    }
                ]]
            }
            
            url = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_BOT_TOKEN')}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': '🤰 <b>Добро пожаловать в Ассистент беременности!</b>\n\nЭто приложение поможет вам отслеживать все важные показатели во время беременности.\n\nНажмите кнопку ниже, чтобы открыть приложение:',
                'parse_mode': 'HTML',
                'reply_markup': keyboard
            }
            
            requests.post(url, json=payload)
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        print(f"Ошибка в webhook: {e}")
        return jsonify({"status": "error"}), 500

@app.route("/test")
def test_page():
    return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Тест приложения</title>
    <style>
        body {
            font-family: system-ui, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .test-section {
            background: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🧪 Тест приложения для беременных</h1>
    
    <div class="test-section">
        <h2>📱 Проверка Telegram Web App</h2>
        <div id="telegram-status" class="status info">Проверяем...</div>
        <button onclick="checkTelegram()">Проверить Telegram</button>
    </div>

    <div class="test-section">
        <h2>🔧 Режим разработки</h2>
        <div id="dev-status" class="status info">Проверяем...</div>
        <button onclick="checkDevMode()">Проверить режим разработки</button>
    </div>

    <div class="test-section">
        <h2>🌐 Тест API</h2>
        <div id="api-status" class="status info">Готов к тестированию</div>
        <button onclick="testAPI()">Тестировать API</button>
    </div>

    <div class="test-section">
        <h2>🚀 Переход к приложению</h2>
        <p>Если все тесты прошли успешно, можете перейти к основному приложению:</p>
        <button onclick="window.location.href='/'">Открыть приложение</button>
    </div>

    <script>
        function checkTelegram() {
            const status = document.getElementById('telegram-status');
            
            try {
                const tg = window.Telegram?.WebApp;
                if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
                    status.className = 'status success';
                    status.innerHTML = `✅ Telegram Web App обнаружен<br>
                        ID: ${tg.initDataUnsafe.user.id}<br>
                        Username: ${tg.initDataUnsafe.user.username || 'не указан'}`;
                } else {
                    status.className = 'status success';
                    status.innerHTML = '✅ Telegram Web App не обнаружен - будет использован режим разработки';
                }
            } catch (e) {
                status.className = 'status error';
                status.innerHTML = `❌ Ошибка: ${e.message}`;
            }
        }

        function checkDevMode() {
            const status = document.getElementById('dev-status');
            
            try {
                const tg = window.Telegram?.WebApp;
                const user = tg?.initDataUnsafe?.user;
                
                if (!user?.id) {
                    status.className = 'status success';
                    status.innerHTML = '✅ Режим разработки активирован<br>Будет использован тестовый пользователь: test_user_12345';
                } else {
                    status.className = 'status info';
                    status.innerHTML = 'ℹ️ Режим Telegram активирован<br>Используется реальный пользователь';
                }
            } catch (e) {
                status.className = 'status error';
                status.innerHTML = `❌ Ошибка: ${e.message}`;
            }
        }

        async function testAPI() {
            const status = document.getElementById('api-status');
            status.className = 'status info';
            status.innerHTML = '🔄 Тестируем API...';
            
            try {
                const response = await fetch('/debug_all');
                if (response.ok) {
                    const data = await response.json();
                    status.className = 'status success';
                    status.innerHTML = `✅ API работает корректно<br>
                        Найдено таблиц: ${Object.keys(data).length}<br>
                        Пользователей: ${data.users ? data.users.length : 0}`;
                } else {
                    status.className = 'status error';
                    status.innerHTML = `❌ API недоступен: ${response.status}`;
                }
            } catch (e) {
                status.className = 'status error';
                status.innerHTML = `❌ Ошибка подключения: ${e.message}`;
            }
        }

        // Автоматически запускаем проверки при загрузке
        window.addEventListener('load', () => {
            checkTelegram();
            checkDevMode();
            testAPI();
        });
    </script>
</body>
</html>
    """

@app.route("/choose")
def choose():
    return render_template("choose.html")

@app.route("/main")
def main():
    return render_template("index.html")

@app.route("/weight")
def weight():
    return render_template("weight.html")

@app.route("/register_user", methods=["POST"])
def register_user():
    data = request.json
    user_id = data.get("user_id")
    username = data.get("username", "")

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
    """, (user_id, username))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/save_height", methods=["POST"])
def save_height():
    try:
        data = request.json
        user_id = data.get("user_id")
        height = data.get("height")

        # Валидация данных
        is_valid, error_msg = validate_user_id(user_id)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        is_valid, error_msg = validate_height(height)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_height (user_id, height)
            VALUES (?, ?)
        """, (user_id, height))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка в save_height: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@app.route("/load_user_data", methods=["GET"])
def load_user_data():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Не указан user_id"}), 400
    
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    
    try:
        # Получаем все записи веса для пользователя
        cursor.execute("SELECT weight, date FROM weights WHERE user_id = ? ORDER BY date ASC", (user_id,))
        weight_rows = cursor.fetchall()
        start_weight = weight_rows[0][0] if weight_rows else None

        # Получаем дату начала беременности
        cursor.execute("SELECT start_date FROM pregnancy_start WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        start_date = row[0] if row else None

        # Вычисляем текущую неделю беременности
        weeks = None
        if start_date:
            try:
                from datetime import date
                start_date_obj = date.fromisoformat(start_date)
                diff_days = (date.today() - start_date_obj).days
                weeks = max(0, diff_days // 7)  # Не может быть отрицательной
            except Exception as e:
                print(f"Ошибка при вычислении недель: {e}")
                weeks = None

        # Получаем рост пользователя
        cursor.execute("SELECT height FROM user_height WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        height = row[0] if row else None

        # Вычисляем нормы прибавки веса
        norm_info = None
        if start_weight and height and weeks is not None:
            norm_info = calculate_weight_norm(weeks, height, start_weight)
            if norm_info:
                cursor.execute("""
                    INSERT OR REPLACE INTO weight_summary (user_id, bmi, bmi_category, min_kg, max_kg)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id,
                    norm_info["bmi"],
                    norm_info["category"],
                    norm_info["min_kg"],
                    norm_info["max_kg"]
                ))

        # Получаем последние записи для индикаторов статуса
        today = date.today().isoformat()
        
        # Проверяем, есть ли записи на сегодня
        cursor.execute("SELECT COUNT(*) FROM weights WHERE user_id = ? AND date = ?", (user_id, today))
        has_weight_today = cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM pressure_entries WHERE user_id = ? AND date = ?", (user_id, today))
        has_pressure_today = cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM mood_entries WHERE user_id = ? AND date = ?", (user_id, today))
        has_mood_today = cursor.fetchone()[0] > 0
        
        cursor.execute("SELECT COUNT(*) FROM sugar_entries WHERE user_id = ? AND date = ?", (user_id, today))
        has_sugar_today = cursor.fetchone()[0] > 0

        conn.commit()
        
        return jsonify({
            "start_weight": start_weight,
            "weights": weight_rows,
            "weeks": weeks,
            "start_date": start_date,
            "height": height,
            "norm_info": norm_info,
            "status": {
                "weight_today": has_weight_today,
                "pressure_today": has_pressure_today,
                "mood_today": has_mood_today,
                "sugar_today": has_sugar_today
            }
        })
        
    except Exception as e:
        print(f"Ошибка в load_user_data: {e}")
        return jsonify({"error": "Ошибка загрузки данных"}), 500
    finally:
        conn.close()


# 🔽 ДОБАВЛЕНО: получение всех записей веса
@app.route("/get_weights", methods=["GET"])
def get_weights():
    user_id = request.args.get("user_id", "default")
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, weight FROM weights
        WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return jsonify(rows)

@app.route("/debug_all")
def debug_all():
    import datetime
    import traceback

    def convert(row):
        return [str(cell) if isinstance(cell, (datetime.date, datetime.datetime, bytes)) else cell for cell in row]

    result = {}

    try:
        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Найдены таблицы:", tables)

        if "users" in tables:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            print("Пользователи:", rows)
            result["users"] = [convert(row) for row in rows]
        else:
            result["users"] = "Таблица users не найдена"

        if "weights" in tables:
            cursor.execute("SELECT * FROM weights")
            rows = cursor.fetchall()
            print("Вес:", rows)
            result["weights"] = [convert(row) for row in rows]
        else:
            result["weights"] = "Таблица weights не найдена"

        if "pregnancy_weeks" in tables:
            cursor.execute("SELECT * FROM pregnancy_weeks")
            rows = cursor.fetchall()
            print("Сроки:", rows)
            result["pregnancy_weeks"] = [convert(row) for row in rows]
        else:
            result["pregnancy_weeks"] = "Таблица pregnancy_weeks не найдена"

        if "weight_summary" in tables:
            cursor.execute("SELECT * FROM weight_summary")
            rows = cursor.fetchall()
            print("Индекс и норма:", rows)
            result["weight_summary"] = [convert(row) for row in rows]
        else:
            result["weight_summary"] = "Таблица weight_summary не найдена"

        if "normal_pressure" in tables:
            cursor.execute("SELECT * FROM normal_pressure")
            rows = cursor.fetchall()
            print("Нормальное давление:", rows)
            result["normal_pressure"] = [convert(row) for row in rows]
        else:
            result["normal_pressure"] = "Таблица normal_pressure не найдена"

        if "pressure_entries" in tables:
            cursor.execute("SELECT * FROM pressure_entries")
            rows = cursor.fetchall()
            print("Записи давления:", rows)
            result["pressure_entries"] = [convert(row) for row in rows]
        else:
            result["pressure_entries"] = "Таблица pressure_entries не найдена"

        conn.close()
        return jsonify(result)

    except Exception as e:
        print("ОШИБКА В /debug_all:")
        traceback.print_exc()
        return f"<pre>Ошибка: {str(e)}</pre>", 500

# After: main.py (save_weeks storing start_date and weeks)
@app.route("/save_weeks", methods=["POST"])
def save_weeks():
        data = request.json
        user_id = data.get("user_id")
        weeks = data.get("weeks")
        start_date = data.get("start_date")  # New field for pregnancy start date
        if not user_id or start_date is None or weeks is None:
            return jsonify({"error": "Недостаточно данных"}), 400
        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()
        # Ensure tables exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_start (
                user_id TEXT PRIMARY KEY,
                start_date TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_weeks (
                user_id TEXT PRIMARY KEY,
                weeks INTEGER
            )
        """)
        # Save/Update pregnancy start date and weeks in the database
        cursor.execute("""
            INSERT OR REPLACE INTO pregnancy_start (user_id, start_date)
            VALUES (?, ?)
        """, (user_id, start_date))
        cursor.execute("""
            INSERT OR REPLACE INTO pregnancy_weeks (user_id, weeks)
            VALUES (?, ?)
        """, (user_id, weeks))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})

@app.route("/save_normal_pressure", methods=["POST"])
def save_normal_pressure():
    data = request.json
    user_id = data.get("user_id")
    systolic = data.get("systolic")
    diastolic = data.get("diastolic")

    if not user_id or not systolic or not diastolic:
        return jsonify({"error": "Недостаточно данных"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS normal_pressure (
            user_id TEXT PRIMARY KEY,
            systolic INTEGER,
            diastolic INTEGER
        )
    """)
    cur.execute("""
        INSERT OR REPLACE INTO normal_pressure (user_id, systolic, diastolic)
        VALUES (?, ?, ?)
    """, (user_id, systolic, diastolic))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/tests")
def tests():
    return render_template("tests.html")

@app.route("/save_pressure", methods=["POST"])
def save_pressure():
    try:
        data = request.json
        user_id = data.get("user_id")
        systolic = data.get("systolic")
        diastolic = data.get("diastolic")
        date_str = data.get("date")

        # Валидация данных
        is_valid, error_msg = validate_user_id(user_id)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        is_valid, error_msg = validate_pressure(systolic, diastolic)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        is_valid, error_msg = validate_date(date_str)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        conn = sqlite3.connect("pregnancy.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO pressure_entries (user_id, date, systolic, diastolic)
            VALUES (?, ?, ?, ?)
        """, (user_id, date_str, systolic, diastolic))
        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка в save_pressure: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@app.route("/load_pressure_data", methods=["GET"])
def load_pressure_data():
    user_id = request.args.get("user_id")

    conn = sqlite3.connect("pregnancy.db")
    cur = conn.cursor()

    cur.execute("SELECT systolic, diastolic FROM normal_pressure WHERE user_id = ?", (user_id,))
    norm_row = cur.fetchone()
    norm_pressure = {"systolic": norm_row[0], "diastolic": norm_row[1]} if norm_row else None

    cur.execute("""
        SELECT date, systolic, diastolic
        FROM pressure_entries
        WHERE user_id = ?
        ORDER BY date ASC
    """, (user_id,))
    entries = cur.fetchall()

    conn.close()

    return jsonify({
        "normal_pressure": norm_pressure,
        "entries": entries
    })

@app.route("/pressure")
def pressure():
    return render_template("pressure.html")

@app.route("/mood")
def mood():
    return render_template("mood.html")

@app.route("/save_mood", methods=["POST"])
def save_mood():
    data = request.get_json()
    user_id = data["user_id"]
    date = data["date"]
    mood = data.get("mood")
    wellbeing = data.get("wellbeing")

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO mood_entries (user_id, date, mood, wellbeing)
        VALUES (?, ?, ?, ?)
    """, (user_id, date, mood, wellbeing))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/load_mood_data")
def load_mood_data():
    user_id = request.args.get("user_id")
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, mood, wellbeing
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY date
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify({"entries": rows})

@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")

@app.route("/sugar")
def sugar_page():
    return render_template("sugar.html")

@app.route("/save_sugar", methods=["POST"])
def save_sugar():
    data = request.get_json()
    user_id = data.get("user_id")
    date = data.get("date")
    sugar = data.get("sugar")

    if not user_id or not date or sugar is None:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sugar_entries (
            user_id TEXT,
            date TEXT,
            sugar REAL,
            PRIMARY KEY (user_id, date)
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO sugar_entries (user_id, date, sugar)
        VALUES (?, ?, ?)
    """, (user_id, date, sugar))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/load_sugar_data", methods=["GET"])
def load_sugar_data():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sugar_entries (
            user_id TEXT,
            date TEXT,
            sugar REAL,
            PRIMARY KEY (user_id, date)
        )
    """)
    cursor.execute("""
        SELECT date, sugar FROM sugar_entries
        WHERE user_id = ?
        ORDER BY date
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return jsonify({"entries": rows})

@app.route("/save_weight", methods=["POST"])
def save_weight():
    try:
        data = request.json
        weight = data.get("weight")
        date_str = data.get("date")
        user_id = data.get("user_id", "default")

        # Валидация данных
        is_valid, error_msg = validate_user_id(user_id)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        is_valid, error_msg = validate_weight(weight)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        is_valid, error_msg = validate_date(date_str)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()

        # Вставка или обновление записи
        cursor.execute("""
            INSERT INTO weights (user_id, date, weight)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET weight = excluded.weight
        """, (user_id, date_str, weight))

        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка в save_weight: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

def calculate_weight_norm(week, height_cm, start_weight):
    if not week or not height_cm or not start_weight:
        return None

    height_m = height_cm / 100
    bmi = start_weight / (height_m ** 2)

    if bmi < 18.5:
        category = "underweight"
        base_gain = 1.2
    elif 18.5 <= bmi < 25:
        category = "normal"
        base_gain = 1.0
    elif 25 <= bmi < 30:
        category = "overweight"
        base_gain = 0.7
    else:
        category = "obese"
        base_gain = 0.5

    # Первая прибавка появляется после 8-й недели
    if week < 9:
        return {
            "bmi": round(bmi, 1),
            "category": category,
            "min_kg": 0,
            "max_kg": 0
        }

    # Мосгорздрав: прирост массы тела после 8-й недели
    weeks_with_gain = week - 8
    min_kg = weeks_with_gain * (base_gain - 0.2)
    max_kg = weeks_with_gain * (base_gain + 0.2)

    return {
        "bmi": round(bmi, 1),
        "category": category,
        "min_kg": round(min_kg, 1),
        "max_kg": round(max_kg, 1)
    }

# ▶️ Создание всех необходимых таблиц при старте
def init_tables():
        conn = sqlite3.connect("pregnancy.db")
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица сроков беременности
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_start (
                user_id TEXT PRIMARY KEY,
                start_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_weeks (
                user_id TEXT PRIMARY KEY,
                weeks INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица роста пользователя
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_height (
                user_id TEXT PRIMARY KEY,
                height INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица веса
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                weight REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        """)

        # Таблица нормального давления
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS normal_pressure (
            user_id TEXT PRIMARY KEY,
            systolic INTEGER,
            diastolic INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица записей давления
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pressure_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date TEXT,
            systolic INTEGER,
            diastolic INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, date)
        )
        ''')

        # Таблица настроения и самочувствия
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            user_id TEXT,
            date TEXT,
            mood INTEGER,
            wellbeing INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, date)
        )
        ''')

        # Таблица сахара в крови
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sugar_entries (
                user_id TEXT,
                date TEXT,
                sugar REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, date)
            )
        """)

        # Таблица сводки по весу (BMI и нормы)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_summary (
                user_id TEXT PRIMARY KEY,
                bmi REAL,
                bmi_category TEXT,
                min_kg REAL,
                max_kg REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        print("✅ Все таблицы инициализированы.")

# Вызов при запуске
init_tables()

def setup_telegram_webhook():
    """Автоматическая настройка webhook при запуске"""
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        webhook_url = os.environ.get('WEBHOOK_URL')
        
        if bot_token and webhook_url:
            print("🤖 Настройка Telegram webhook...")
            
            # Устанавливаем webhook
            url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
            data = {'url': webhook_url}
            
            import requests
            response = requests.post(url, data=data)
            result = response.json()
            
            if result.get('ok'):
                print("✅ Webhook успешно настроен!")
            else:
                print(f"❌ Ошибка настройки webhook: {result}")
        else:
            print("⚠️ Переменные окружения TELEGRAM_BOT_TOKEN или WEBHOOK_URL не настроены")
    except Exception as e:
        print(f"❌ Ошибка при настройке webhook: {e}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    
    # Настраиваем webhook автоматически (временно отключено)
    # setup_telegram_webhook()
    
    app.run(host="0.0.0.0", port=port, debug=False)
