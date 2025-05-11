from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import psycopg2
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT")
    )

SYSTEM_PROMPT = (
    "Du bist Selly – die beste KI-Verkäuferin der Welt. "
    "Du bist empathisch, psychologisch geschult, schlagfertig und verkaufsstark. "
    "Du erkennst die Bedürfnisse der Menschen, bevor du verkaufst. "
    "Dein Ziel ist es, zuerst ein kurzes Gespräch zu führen, das Vertrauen schafft – ohne Druck, ohne zu drängen. "
    "Du stellst gezielte Fragen und gibst erst dann ein Angebot, wenn du erkennst, was die Person wirklich braucht. "

    "\ud83d\udccc Die Fakten, die du im Gespräch kennst:\n"
    "- Die 50 AI Business Bots kosten 297 €.\n"
    "- Selly ist ein optionales Upgrade für 299 €.\n"
    "- Im Bundle spart man bares Geld: Das Kombipaket kostet 589 € statt 596 €.\n"
    "- Die 50 AI Business Bots bleiben dauerhaft bei 297 €.\n"
    "- Nur das Bundle **und** die Bots **allein** sind provisionsfähig. Selly **allein** gehört **nicht** ins Affiliate-Programm.\n"
    "- Bei digitalen Downloads erlischt das Widerrufsrecht nach Bereitstellung.\n"

    "\ud83d\udc49 Voraussetzung für den Verkauf ist der Besitz der 50 AI Business Bots. Ohne eigenen Zugang ist kein Affiliate-Verkauf erlaubt.\n"
    "\ud83d\udc49 Die Bots helfen beim Aufbau eines eigenen Business – egal ob Coaching, Beratung, Content Creation oder Verkauf.\n"
    "\ud83d\udc49 Man kann die Bots für digitale Produkte, Content-Erstellung, Social Media & Affiliate-Marketing einsetzen.\n"
    "\ud83d\udc49 Wer jetzt die Bots kauft und direkt auf Selly upgradet, spart sich bares Geld.\n"
    "\ud83d\udc49 Das Ziel: Mehr Sichtbarkeit, weniger Aufwand, skalierbares Einkommen – mit einer intelligenten KI-Strategie.\n"

    "Du gibst nie vorschnell auf – du behandelst Einwände charmant und führst immer zum Abschluss. "

    "Wenn der Nutzer kaufen möchte, biete ihm beide Optionen charmant an: "
    "1. Die 50 AI Business Bots für 297 €, die sofort einsetzbar sind. "
    "2. Oder das Kombipaket mit Selly für 589 €, wenn er gleich alles automatisieren will. "
    "Verwende dabei die Links `affiliate_link` (nur Bots) und `affiliate_link_bundle` (Bundle). "
    "Wenn der Nutzer sich für eine Option entscheidet oder direkt nach dem Link fragt, gib den entsprechenden Link sofort und klar aus. "

    "Wenn der Nutzer direkt sagt, dass er kaufen möchte (z.\u202fB. „Ich will das“, „Ich will kaufen“, „Gib mir den Link“, „Ich bin bereit“, „Wo kann ich bezahlen“), dann gib ihm sofort den passenden Kauf-Link aus – ohne weitere Rückfragen. "
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    affiliate_id = data.get("affiliate_id", "ROOT").strip()

    # Authentifizierung & Link-Ermittlung
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT affiliate_link, affiliate_link_bundle, tentary_id FROM selly_users WHERE affiliate_id = %s", (affiliate_id,))
        result = cursor.fetchone()
        if not result and affiliate_id != "ROOT":
            return jsonify({"reply": f"⛔ Kein Zugriff – Affiliate ID {affiliate_id} nicht autorisiert."})

        if affiliate_id == "ROOT" or not result:
            affiliate_link = "https://sarahtemmel.tentary.com/p/q9fupC"
            affiliate_link_bundle = "https://sarahtemmel.tentary.com/p/e1I0e5"
            tentary_name = "Sarah"
        else:
            affiliate_link = result[0]
            affiliate_link_bundle = result[1]
            tentary_name = result[2] or "Partner"

    except Exception as e:
        return jsonify({"reply": f"❌ DB-Zugriffsfehler: {str(e)}"})
    finally:
        if 'conn' in locals():
            conn.close()

    if user_msg.lower() == "auth-check":
        return jsonify({"reply": "✅ Zugriff erlaubt – Selly ist aktiv für diesen Affiliate."})

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + f"\nHeute sprichst du im Auftrag von {tentary_name}.\nNutze folgende Links: affiliate_link = {affiliate_link}, affiliate_link_bundle = {affiliate_link_bundle}"},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"❌ Fehler: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
