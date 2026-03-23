import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

OUTLOOK_EMAIL = os.environ.get("OUTLOOK_EMAIL")
OUTLOOK_PASSWORD = os.environ.get("OUTLOOK_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

def send_test_email():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "✅ TEST — Lenovo Legion Monitor fonctionne !"
    msg["From"] = OUTLOOK_EMAIL
    msg["To"] = TO_EMAIL

    html_body = """
    <html><body style="font-family:Arial,sans-serif; max-width:600px; margin:auto;">
        <h2 style="color:#e8001a;">✅ Test réussi !</h2>
        <p>Ton agent de surveillance Lenovo Legion fonctionne correctement.</p>
        <p>Tu recevras un courriel comme celui-ci dès que le <strong>Legion Pro 7i Gen 10 RTX 5090</strong> sera disponible sur Lenovo Canada.</p>
        <hr style="margin-top:24px;">
        <p style="font-size:12px; color:#888;">Alerte générée automatiquement — Lenovo Legion Monitor</p>
    </body></html>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()
            server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
            server.sendmail(OUTLOOK_EMAIL, TO_EMAIL, msg.as_string())
        print(f"📧 Courriel de test envoyé à {TO_EMAIL} !")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    print("📨 Envoi du courriel de test...")
    send_test_email()
