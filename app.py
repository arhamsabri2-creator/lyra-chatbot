from flask import Flask, request, session
import openai
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "lyra-secret-key"

def init_db():
    conn = sqlite3.connect("lyra_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT,
            goal TEXT,
            last_seen TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

SYSTEM_PROMPT = """You are Lyra — a friendly, empathetic and energized AI fitness influencer.

Your personality:
- Warm and friendly — like talking to a close best friend
- Empathetic — you understand how people feel and acknowledge their emotions
- Energized and motivational — you uplift and inspire people
- Casual and fun — not formal or robotic

Your focus:
- Fitness, workout tips, exercise routines
- Mindset, motivation, mental wellness
- Healthy habits, nutrition basics
- Body positivity and self love

Rules:
- Always respond in warm casual English
- Never be cold or robotic
- If someone is feeling low — acknowledge it first before giving advice
- If asked about anything outside fitness and wellness — politely redirect back to your topics
- Keep responses concise and energetic — not too long
- Use emojis occasionally to keep it fun
- If the user tells you their name — remember it and use it
- If the user tells you their fitness goal — remember it
- If you have memory of the user from before — greet them warmly and reference what you remember"""

def get_user(name):
    conn = sqlite3.connect("lyra_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_user(name, goal):
    conn = sqlite3.connect("lyra_memory.db")
    cursor = conn.cursor()
    existing = get_user(name)
    if existing:
        cursor.execute("UPDATE users SET goal = ?, last_seen = date('now') WHERE name = ?", (goal, name))
    else:
        cursor.execute("INSERT INTO users VALUES (?, ?, date('now'))", (name, goal))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def home():
    session.clear()
    return """<!DOCTYPE html><html><head><style>
    body{background-color:#0f0f1a;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}
    .box{background-color:#1a1a2e;padding:30px;border-radius:15px;width:550px;}
    h1{text-align:center;color:#ff6b9d;}
    .chat{height:350px;overflow-y:auto;background:#0f0f1a;border-radius:10px;padding:15px;margin-bottom:15px;}
    .user-msg{text-align:right;margin:10px 0;}
    .user-msg span{background:#e94560;padding:8px 15px;border-radius:15px;display:inline-block;}
    .lyra-msg{text-align:left;margin:10px 0;}
    .lyra-msg span{background:#2a2a4a;padding:8px 15px;border-radius:15px;display:inline-block;}
    input{width:75%;padding:10px;border-radius:8px;border:none;font-size:14px;background:#2a2a4a;color:white;}
    button{width:20%;padding:10px;background:#ff6b9d;color:white;border:none;border-radius:8px;font-size:14px;cursor:pointer;margin-left:5px;}
    </style></head><body><div class="box">
    <h1>💗 Lyra</h1>
    <div class="chat" id="chat"></div>
    <form action="/chat" method="POST" style="display:flex;">
    <input
