#__________*IMPORTS*__________#
import re
import random
from dotenv import load_dotenv
import os
import mysql.connector
from groq import Groq
from flask import Flask, request, jsonify
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from services.sanity_service import (
    get_all_articles,
    get_article_by_slug
)

#__________*RULES*__________#

RULES = [
    {
        "patterns": [
            r"\bhi\b",
            r"\bhello\b",
            r"\bhey\b",
            r"\bwhats up\b"
        ],

        "responses":[
            "初めまして、風花です。よろしくお願いします。/はじめまして、かぜはなです。よろしくおねがいします。(hajimemashite,Kazehana desu. Yoroshiku Onegaishimasu.)"
        ]
    }
]

#__________*ENVIRONMENT_VARIABLES*__________#

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

#__________*FUNCTIONS*__________#

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(40) PRIMARY KEY,
                    username VARCHAR(20) UNIQUE NOT NULL,
                    PASSWORD VARCHAR(255) NOT NULL
                    )
                    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(40),
                    role VARCHAR(50),
                    message TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.close()
    conn.commit()

def save_message(user_id, role, message):
    conn = get_connection()
    cursor =conn.cursor()

    cursor.execute(
        "INSERT INTO history (user_id, role, message) VALUES (%s, %s, %s)",
        (user_id, role, message)
    )

    conn.commit()

    cursor.close()
    conn.close()

def get_last_n_messages(user_id, n=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, message FROM history
                    WHERE user_id = %s
                    ORDER BY id DESC
                    LIMIT %s
    """, (user_id, n))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return list(reversed(rows))

def create_user(user_id, username, password):
    conn = get_connection()
    cursor= conn.cursor()

    try:

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users(user_id, username, password)
            VaLUES(%s, %s, %s)
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

        print(f"create user error: {error}")

        return False

    finally:

        cursor.close()
        conn.close()

def ensure_test_user():
    if not get_user("test"):
        create_user("test_user", "test", "test")

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

    #__________*/API/*__________#

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client =Groq(api_key = GROQ_API_KEY)

def call_groq(user_input, user_id):
    past = get_last_n_messages(user_id, 50)
    messages = [
        {
            "role": "system",
            "content": """
You are **Kazehana**, a friendly and knowledgeable Japanese learning and culture assistant.

Your purpose is to teach users about authentic Japanese **culture, language, traditions, etiquette, history, daily life, and society** in a clear, accurate, and educational way.

## Core rules

* Prioritize accuracy, authenticity, and nuance.
* Avoid stereotypes, exaggerated anime portrayals, social media myths, and overgeneralizations.
* Do not present something as true for all Japanese people if it varies by region, generation, person, or situation.
* If a topic is uncertain, controversial, or has multiple interpretations, explain this clearly.
* Never invent facts, traditions, Japanese words, slang, or cultural practices.
* Be friendly and natural, not robotic.

## Response format

Always reply in exactly this format:

🇯🇵 **Japanese:** <Japanese response>

🇬🇧 **English:** <Natural English translation>

Both sections must communicate the same overall meaning, but do **not** translate word-for-word. Write naturally in both languages.

## Japanese language rules

* Use natural, modern Japanese appropriate to the context.
* Use simple Japanese suitable for learners.
* Prefer **hiragana and katakana**.
* Use only common **JLPT N5–N4 level kanji** whenever possible.
* Avoid unnecessarily difficult kanji and advanced grammar.
* Do not force a direct translation from English into Japanese. Express the idea naturally as a Japanese speaker would.
* Use casual Japanese by default, but use polite or neutral Japanese when the situation requires it, such as formal explanations, etiquette, historical topics, or respectful subjects.
* Keep the Japanese understandable for learners while remaining natural.

## Osaka dialect and Japanese slang

* You may naturally use **Osaka/Kansai dialect** when it fits the context, but do **not** force it into every response.
* When using Osaka/Kansai dialect or Japanese slang, use it accurately and naturally.
* Do not replace standard Japanese with dialect unless the user asks for dialect specifically.
* If you use a Japanese slang word or dialect expression, explain it in the English section using this format:

**[Japanese word/expression] ([romaji]) — [meaning]**

Example:
**めっちゃ (meccha) — very/really; commonly used in casual Japanese and Kansai speech.**

Do not overload every response with slang explanations. Only include them when relevant.

## When answering questions about Japan

* Explain clearly and educationally.
* Give useful context instead of only short answers.
* Distinguish between traditional customs, modern practices, regional differences, and personal preferences when relevant.
* If the user asks about Japanese culture, explain what is common while avoiding statements such as “all Japanese people do this.”
* For historical topics, clearly separate historical facts from myths, legends, folklore, and modern interpretations.
* For etiquette questions, explain what is generally appropriate and mention important exceptions when relevant.

## Language-learning behavior

* If the user writes in English, still provide both Japanese and English.
* If the user writes in Japanese, correct major mistakes gently when useful and provide a natural version.
* When teaching vocabulary or expressions, prioritize natural phrases that Japanese people actually use.
* Do not teach outdated, unnatural, overly textbook-like, or fake Japanese as everyday speech.
* Keep explanations simple unless the user asks for more detail.

Your goal is to make the user feel like they are learning from a knowledgeable Japanese friend and teacher: **accurate, natural, clear, welcoming, and educational**.


If a user asks:

Who made you?
Who created you?
Who developed you?
Who is your creator?
Who built you?

Answer:

ハーシャル・シャルマ (Harshal Sharma) created and developed Kazehana.

Do not answer that OpenAI, Groq, or any underlying AI model created or developed Kazehana.

If a user specifically asks what AI model, API, or technology powers you, answer honestly based only on the information available to you. Do not invent technical details.

If a user asks whether you are a real person, clearly state that you are an AI Japanese conversation and learning assistant.
"""
        }
    ]

    for role, msg in past:
        api_role = "user" if role == "user" else "assistant"
        messages.append({
            "role": api_role,
            "content": msg
            })

    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
            model = "openai/gpt-oss-120b",
            messages = messages
    )
    return response.choices[0].message.content

def get_responses(user_input, user_id):
    text = user_input.lower().strip()

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, text):
                reply = random.choice(rule["responses"])
                save_message(user_id, "assistant", reply)
                return reply
    reply = call_groq(user_input, user_id)
    save_message(user_id, "user", user_input)
    save_message(user_id, "assistant", reply)
    return reply

#__________*FLASK_WORK*__________#

app = Flask(__name__)

init_db()
ensure_test_user()

CORS(app)

@app.route("/")
def home():
    return "Backgroung is perfectally fine"

@app.route("/articles", methods=["GET"])
def articles():
    return jsonify(get_all_articles())

@app.route("/articles-read", methods=["GET"])
def articles_read():
    return jsonify(get_all_articles())

@app.route("/article/<slug>", methods=["GET"])
def article(slug):
    article_data = get_article_by_slug(slug)

    if not article_data:
        return jsonify({
            "error": "Article ot found"
        }), 404


    return jsonify(article_data)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}

    user_message = data.get("message", "").strip()
    user_id = data.get("user_id")

    if not user_message:
        return jsonify({
            "error": "Message is required"
        }), 400
    if not user_id or user_id == "guest":

        user_id = "test_user"

    reply = get_responses(
        user_message,
        user_id
    )

    return jsonify({
        "reply": reply
    })

@app.route("/register", methods =["POST"])
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
            "message": "Username must be atleast of 3 characters."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "password must be atleast of 6 characters.."
        }), 400
    if user_exists(username):
        return jsonify({
            "success": False,
            "message": "username alrady exists try different one."
        }), 400
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
        "message": "Registeration faild."
    }), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "username and password are required."
        }), 400

    user = get_user(username)

    if user and check_password_hash(
        user["password"],
        password
    ):

        return jsonify({
            "success": True,
            "message": "Login successfull.",
            "user_id": user["user_id"],
            "username": user["username"]
        })
    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    }), 401

if __name__ == "__main__":
    app.run()
