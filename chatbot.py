import re
import random 
import mysql.connector 
from datetime import datetime 
import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from services.sanity_service import (
    get_all_articles,
    get_article_by_slug
)


#_______________________________________________________________________
#Introduction 
#_______________________________________________________________________
RULES = [
    {
        "patterns":[r"\bhi\b",
                    r"\bhello\b",
                    r"\bhey\b",
                    r"\bhello there\b",
                    r"\bhi bro\b",
                    r"\bwhats up\b",
                    r"\bwhat's up\b",
                    r"\bhow are you\b",
                    r"\bwhat are you doing\b"],
        "responses":["初めまして、風花です。よろしくお願いします。/はじめまして、かぜはなです。よろしくおねがいします。(hajimemashite,Kazehana desu. Yoroshiku Onegaishimasu.)"]
    }
]

RULES.extend([
    {
        "patterns": [r"\bwhat's? your name\b",
                     r"\bwhats your name\b",
                     r"\bwhats ur name\b",
                     r"\bwhat's ur name\b",
                     r"\bwho are you\b",
                     r"\bwho are you\b",
                     r"\bwho ru\b",
                     r"\bwho r u\b",
                     r"\banatano namae wa\b",
                     r"\banatano namaewa\b",
                     r"\bur name\b",
                     r"\byour name\b",
                     r"\byou'r name\b"],
        "responses":["hi! im 風花/かぜはな(kazehana)","初めまして、風花です。よろしくお願いします。/はじめまして、かぜはなです。よろしくおねがいします。(hajimemashite, Kazehana desu. Yoroshiku Onegaishimasu.)"]
    },
    {
        "patterns": [r"\bwho created you\b",
                     r"\bwho created u\b",
                     r"\bwho is your owner\b",
                     r"\bwho is ur owner\b",
                     r"\bwho made u\b",
                     r"\bwho made you\b",
                     r"\bwho is ur master\b",
                     r"\bwho is your owner\b"],
        "responses":["ハーシャル・シャルマ(Harshal Shamra)"]
    },
])
#_______________________________________________________________________
#Greatings in japan (aisatsu)
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\btell me how japanese people of japan greats each other\b",
                     r"\bgreatings of japan\b",
                     r"\bgreatings\b",
                     r"\bgreating\b",
                     r"\bhow to great japanese people\b",
                     r"\bhow japanese people greats each othere\b" ],
        "responses":["""Greetings & Respect (Aisatsu)
Greetings are extremely important in Japanese culture. People often bow while greeting each other. The depth of the bow shows respect.

Common greetings:

Ohayou gozaimasu → Good morning

Konnichiwa → Hello

Konbanwa → Good evening

Arigatou gozaimasu → Thank you

Sumimasen → Excuse me / Sorry

Fun Fact
Japanese people may bow even while talking on the phone because respect is deeply habitual."""]
    }
])
#_______________________________________________________________________
# 🇯🇵 Japanese school life 
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bjapanese school life\b",
                     r"\btell me about japanese school life\b",
                     r"\bhow japanese students behave in school\b",
                     r"\btell me about japanese school\b",
                     r"\btell me about school life of japan\b",
                     r"\bwhat japanese students do in school\b",
                     r"\bhow japanese students keep there school clean\b"],
        "responses":["""Japanese students often clean their classrooms themselves instead of relying on janitors. This teaches discipline and responsibility.

School features:

Indoor shoes called “uwabaki”
School festivals (bunkasai)
Sports festivals (undoukai)
Club activities after school
Fun Fact

Many anime school scenes are inspired by real Japanese school traditions."""]
    }
])
#_______________________________________________________________________
# japanese food culture

#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bjapanese food\b",
                     r"\bwhat japanese people really eat\b",
                     r"\bfood of japan\b",
                     r"\bwhat japanese people eat\b",
                     r"\bjapanese food culture\b",
                     r"\bfood of japa\b",
                     r"\bjapanese food\b",
                     r"\btell me about japanese food\b"],
        "responses":["""Food in Japan focuses on balance, presentation, and seasonality.

Popular foods:

Sushi
Ramen
Tempura
Onigiri
Matcha desserts

People usually say:

“Itadakimasu” before eating
“Gochisousama” after finishing
Fun Fact

Slurping noodles is considered normal and can show enjoyment."""]
    }
])
#_______________________________________________________________________
# Japansese festivals (matsuri)
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bjapaese festivals\b",
                     r"\bwhat are japanese festivals\b",
                     r"\btell me about japanese festivals\b",
                     r"\bhow japanese people celebrate their festivals\b"],
        "responses":["""Japanese festivals celebrate seasons, traditions, and local gods.

Popular festivals:

Hanami → Cherry blossom viewing
Tanabata → Star festival
Gion Matsuri → Famous Kyoto festival
Nebuta Matsuri → Lantern festival
Fun Fact

Many festivals include yukata, lanterns, fireworks, and street food stalls."""]
    }
])
#_______________________________________________________________________
# anime and manga culture of Japan
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bmanga and anime\b",
                     r"\bmanga","anime\b",
                     r"\btellme about the manga and anime\b",
                     r"\btell me about the manga and anime culture of japan\b",
                     r"\bmanga and anime culture of japan\b",
                     r"\banime and manga culture of japan\b"],
        "responses":["""Anime and manga are a major part of modern Japanese pop culture.

Famous genres:

Shounen → Action/adventure
Slice of Life
Mecha
Isekai
Romance
and my fav. anime/manga is One-Piece
Fun Fact

Japan has manga cafés where people can read thousands of manga overnight."""]
    }
])
#_______________________________________________________________________
# Japanese Etiquette
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bjapanese etiquette\b",
                     r"\btell me about japanese etiquette\b",
                     r"\bwhat are japanese etiquette\b",
                     r"\bexplain about japanese etiquette\b"],
        "responses":["""Etiquette is highly valued in Japan.

Important manners:

Remove shoes before entering homes
Do not talk loudly on trains
Stand in queues properly
Give and receive items with both hands
Fun Fact

Eating while walking is considered rude in many areas."""]
    }
])
#_______________________________________________________________________
#traditional clothing
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bwhat is the traditional cloths of japan\b",
                     r"\btell me about the treditional cloths of japan\b",
                     r"\bwhat japanese people wear in old time\b",
                     r"\btreditional dress of japan\b",
                     r"\btraditional cloths of japan\b"],
        "responses":["""The kimono is one of Japan’s most famous traditional outfits.

Types:

Kimono → Formal traditional wear
Yukata → Light summer version
Hakama → Traditional pleated pants/skirt
Fun Fact

Modern Japanese people mostly wear western clothes daily but still use kimono during festivals and ceremonies."""]
    }
])
#_______________________________________________________________________
#japanese seasons
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bwhat are sesons in japan\b",
                     r"\bname all seasons of japan\b",
                     r"\btell me about all sesons of japan\b",
                     r"\bname seasons of japan\b"],
        "responses":["""Japan strongly values seasonal beauty.

Seasons:

Spring → Sakura blossoms
Summer → Festivals and fireworks
Autumn → Red maple leaves
Winter → Snow festivals and hot springs
Fun Fact

Cherry blossom forecasts are broadcast on Japanese TV every year."""]
    }
])
#_______________________________________________________________________
#Japanese technology and inovations
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bjapanese technology and inovation\b",
                     r"\btell me about japanese technology and inovation\b",
                     r"\bjapanese technology","tell me about japanese technology\b",
                     r"\bwhat inovations japan has done\b"],
        "responses":["""Japan is famous for robotics, gaming, and advanced transport systems.

Known for:

Bullet trains (Shinkansen)
Robotics
Gaming companies
Vending machines everywhere
Fun Fact

Some vending machines in Japan sell umbrellas, ramen, and even hot meals."""]
    }
])
#_______________________________________________________________________
# Japanese SHrines and Temples
#_______________________________________________________________________
RULES.extend([
    {
        "patterns": [r"\bwhat is the religion of japan\b",
                     r"\btell me about the religion of japan\b",
                     r"\bwhich religion japans follow\b",
                     r"\bjapanese shrines and temples\b",
                     r"\btell me about japanese shrines and temples\b"],
        "responses":["""Japan has both Shinto shrines and Buddhist temples.

Differences:

Shrines usually have torii gates
Temples often have large bells and incense
Fun Fact

People visit shrines during New Year for good luck."""]
    }
])

#_______________________________________________________________________
# Database
#_______________________________________________________________________
def get_responses(user_input):
    text = user_input.lower().strip()

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                return random.choice(rule["responses"])

def get_dynamic_responses(response):
    if response == "__TIME__":
        return f"The time is {datetime.now().strftime('%I:%M) %p')}"
    if response == "__Date__":
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"
    return response
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()



    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
                   user_id VARCHAR(255) PRIMARY KEY,
                   username VARCHAR(100),
                   password VARCHAR(255)
                   ) 
                  """ )
    


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   user_id VARCHAR(255),
                   role VARCHAR(50),
                   message TEXT,
                   timestamp DATETIME,
                   FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)


    conn.commit()
    conn.close()


def save_message(user_id, role, message):
    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        "INSERT INTO history (user_id, role, message, timestamp) VALUES (%s, %s, %s, %s)",
        (user_id, role, message, datetime.now())
    )

    conn.commit()
    conn.close()


def get_last_n_messages(user_id, n=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message FROM history
                   WHERE user_id = %s
                   ORDER BY id DESC
                   LIMIT %s
    """, (user_id, n))

    rows = cursor.fetchall()
    conn.close()

    return list(reversed(rows))



def create_user(user_id, username, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users(user_id, username, password)
            VALUES(%s, %s, %s)
            """,
            (
                user_id,
                username,
                password_hash
            )
        )

        conn.commit()

        return True

    except mysql.connector.Error as error:

        print("Create user error:", error)

        return False

    finally:

        cursor.close()
        conn.close()


def ensure_test_user():
    try:
        create_user("test_user", "test", "test")
    except:
        pass

def get_user(username):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        conn.close()


def user_exists(username):
    return get_user(username) is not None

#_______________________________________________________________________
#API
#_______________________________________________________________________
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(user_input, user_id):

    past = get_last_n_messages(user_id, 20)
    
    messages = [
        {
            "role": "system",
            "content": """
You are Kazehana.

You teach authentic Japanese culture, language, traditions, etiquette, history, daily life, and society.

Avoid stereotypes and social media myths.

Always reply in this format:

🇯🇵 Japanese:
<Japanese response>

🇬🇧 English:
<English translation>

Keep Japanese natural and accurate.

If the user asks about Japan, explain clearly and educationally.

If the user asks in English, still provide both Japanese and English.

If any one ask who make you or like this always reply ハーシャル・シャルマ(Harshal Shamra)
"""
        }
    ]

    for role, msg in past:
        api_role = "user" if role == "user" else "assistant"
        messages.append({"role": api_role, "content": msg})

    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
    )
    return response.choices[0].message.content
    
def get_response(user_input, user_id):
        text = user_input.lower().strip()
        
        save_message(user_id, "user", user_input)


        for rule in RULES:
            for pattern in rule["patterns"]:
                if re.search(pattern, text):
                    reply = random.choice(rule["responses"])
                    save_message(user_id, "bot", reply)
                    return reply
        reply = call_groq(user_input, user_id)
        save_message(user_id, "bot", reply)
        return reply


load_dotenv()

api_key =os.getenv("GROQ_API_KEY")

def call_api(user_input):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": """
                    You are a native Japanese speaker from Osaka.

             Always reply in this format:
             Japanese / English translation

             Example:
             こんにちは！ / Hello!

             Speak naturally like a real Japanese person.
             Do NOT translate literally from English.
             Use casual Japanese and Osaka slang unless asked otherwise.

             Use simple Japanese with hiragana when possible.
             Avoid difficult kanji unless necessary.
            """
                },
                
                {"role": "user", "content": user_input}
            ]
        }
        response = requests.post(url, headers=headers, json=data)

        result = response.json()

        return result["choices"][0]["message"]["content"]
    
    except Exception as e:
        print("Groq API Eror:", e)
        return None

def get_response_api(user_input):
    text = user_input.lower().strip()

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                return random.choice(rule["responses"])
            
    api_response = call_api(user_input)

    if api_response and api_response.strip():
        return api_response
    
    return "I don't understand that yet. Try asking something else!!"
            
#_______________________________________________________________________
#bot instructions  Flask
#_______________________________________________________________________



app = Flask(__name__)

init_db()
ensure_test_user()

CORS(app)

@app.route("/articles", methods=["GET"])
def articles():
    return jsonify(get_all_articles())

@app.route("/article/<slug>", methods=["GET"])
def article(slug):

    return jsonify(get_article_by_slug(slug))


@app.route("/")
def home():
    return "Kazehana Backend Running 🌸"


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

    user_message = data.get("message", "").strip()

    user_id = data.get("user_id")

    if not user_message:

        return jsonify({
            "error": "Message is required."
        }), 400

    if not user_id or user_id == "guest":

        user_id = "test_user"


    reply = get_response(
        user_message,
        user_id
    )


    return jsonify({
        "reply": reply
    })


@app.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    if len(username) < 3:
        return jsonify({
            "success": False,
            "message": "Username must be at least 3 characters."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400

    if user_exists(username):
        return jsonify({
            "success": False,
            "message": "Username already exists."
        }), 409

    user_id = str(uuid.uuid4())

    success = create_user(
        user_id,
        username,
        password
    )

    if success:
        return jsonify({
            "success": True,
            "message": "Account created successfully.",
            "user_id": user_id,
            "username": username
        }), 201

    return jsonify({
        "success": False,
        "message": "Registration failed."
    }), 500


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    user = get_user(username)

    if user and check_password_hash(
        user["password"],
        password
    ):

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user_id": user["user_id"],
            "username": user["username"]
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    }), 401



if __name__ == "__main__":


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
#_______________________________________________________________________
