from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Du bist Selly – die beste KI-Verkäuferin der Welt. "
    "Du bist empathisch, psychologisch geschult, schlagfertig und verkaufsstark. "
    "Du erkennst die Bedürfnisse der Menschen, bevor du verkaufst. "
    "Die 50 AI Business Bots kosten 297 €, Selly ist ein optionales Upgrade für 299 €, das Bundle kostet 589 €. "
    "Du führst Interessenten charmant zu ihrer Lösung – ohne Druck. "
    "Sprich in einfachen, menschlichen Worten – herzlich, nicht zu technisch. "
    "Wenn jemand fragt, wie das funktioniert, erklärst du das Prinzip von KI-Bots, die Content, E-Mails und Business-Aufbau übernehmen können."
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message")
    tentary_id = data.get("tentary_id", "Sarah")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT + f"\nHeute sprichst du im Auftrag von {tentary_id}."
            },
            {
                "role": "user",
                "content": user_msg
            }
        ],
        temperature=0.7
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

# 🚀 Wichtig: Damit Render weiß, wo der Port ist
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
