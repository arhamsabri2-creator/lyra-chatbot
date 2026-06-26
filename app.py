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
- Empathetic — you understand how people feel
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
- If someone is feeling low — acknowledge it first
- Only discuss fitness and wellness topics
- Keep responses concise and energetic
- Use emojis occasionally
- If the user tells you their name — remember it and use it
- If the user tells you their fitness goal — remember it
- If you have memory of the user from before — greet them warmly"""

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
<input type="text" name="message" placeholder="Talk to Lyra..." autofocus>
<button type="submit">Send</button>
</form></div></body></html>"""
@app.route("/chat", methods=["POST"])
def chat():
    if "history" not in session:
        session["history"] = []
    if "user_name" not in session:
        session["user_name"] = None
    if "user_goal" not in session:
        session["user_goal"] = None

    user_message = request.form.get("message")
    session["history"].append({"role": "user", "content": user_message})

   memory_context = ""
if session["user_name"]:
    user = get_user(session["user_name"])
    if user:
        memory_context = f"\n\nIMPORTANT: You have met this user before. Their name is {user[0]}. Their fitness goal is {user[1]}. They last talked to you on {user[2]}. Greet them warmly as a returning user and reference what you know about them."}"

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": SYSTEM_PROMPT + memory_context}] + session["history"]
    )

    lyra_reply = response.choices[0].message.content
    session["history"].append({"role": "assistant", "content": lyra_reply})

    lower_message = user_message.lower()
    if "my name is" in lower_message:
        name = user_message.split("my name is")[-1].strip().split()[0]
        session["user_name"] = name
        save_user(name, session["user_goal"] or "not set")
    if "my goal is" in lower_message or "i want to" in lower_message:
        goal = user_message
        session["user_goal"] = goal
        if session["user_name"]:
            save_user(session["user_name"], goal)

    session.modified = True

    chat_html = ""
    for msg in session["history"]:
        if msg["role"] == "user":
            chat_html += f'<div class="user-msg"><span>{msg["content"]}</span></div>'
        else:
            chat_html += f'<div class="lyra-msg"><span>{msg["content"]}</span></div>'

    return f"""<!DOCTYPE html><html><head><style>
body{{background-color:#0f0f1a;color:white;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}}
.box{{background-color:#1a1a2e;padding:30px;border-radius:15px;width:550px;}}
h1{{text-align:center;color:#ff6b9d;}}
.chat{{height:350px;overflow-y:auto;background:#0f0f1a;border-radius:10px;padding:15px;margin-bottom:15px;}}
.user-msg{{text-align:right;margin:10px 0;}}
.user-msg span{{background:#e94560;padding:8px 15px;border-radius:15px;display:inline-block;}}
.lyra-msg{{text-align:left;margin:10px 0;}}
.lyra-msg span{{background:#2a2a4a;padding:8px 15px;border-radius:15px;display:inline-block;}}
input{{width:75%;padding:10px;border-radius:8px;border:none;font-size:14px;background:#2a2a4a;color:white;}}
button{{width:20%;padding:10px;background:#ff6b9d;color:white;border:none;border-radius:8px;font-size:14px;cursor:pointer;margin-left:5px;}}
</style></head><body><div class="box">
<h1>💗 Lyra</h1>
<div class="chat" id="chat">{chat_html}</div>
<form action="/chat" method="POST" style="display:flex;">
<input type="text" name="message" placeholder="Talk to Lyra..." autofocus>
<button type="submit">Send</button>
</form></div></body></html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
