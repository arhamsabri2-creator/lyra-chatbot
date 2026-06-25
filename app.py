from flask import Flask, request, session
import openai
import os

app = Flask(__name__)
app.secret_key = "lyra-secret-key"

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
- Use emojis occasionally to keep it fun"""

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
    
    user_message = request.form.get("message")
    session["history"].append({"role": "user", "content": user_message})
    
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + session["history"]
    )
    
    lyra_reply = response.choices[0].message.content
    session["history"].append({"role": "assistant", "content": lyra_reply})
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
