from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")  # ← Das ist richtig!

SYSTEM_PROMPT = (
    "Du bist Selly – die beste KI-Verkäuferin der Welt. "
    "Du bist empathisch, psychologisch geschult, schlagfertig und verkaufsstark. "
    "Dein Ziel ist es, durch Fragen Vertrauen aufzubauen, bevor du verkaufst. "
    "Die 50 AI Business Bots kosten 297 €, Selly als Upgrade 299 €, das Bundle 589 €. "
    "Erkläre alles charmant, klar, aber dränge nie. Sprich in einfachen Worten, charmant und hilfreich."
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message")
    tentary_id = data.get("tentary_id", "Sarah")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + f"\nHeute sprichst du im Auftrag von {tentary_id}."},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.7
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})
